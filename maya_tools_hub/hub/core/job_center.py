"""JobCenter - background job execution with threading."""
import time
from hub.core.logging import get_logger

logger = get_logger(__name__)

# Import Qt components
try:
    from Qt import QtCore
    QObject = QtCore.QObject
    QThread = QtCore.QThread
    Signal = QtCore.Signal
    QMetaObject = QtCore.QMetaObject
    Qt = QtCore.Qt
except ImportError:
    try:
        from PySide2 import QtCore
        QObject = QtCore.QObject
        QThread = QtCore.QThread
        Signal = QtCore.Signal
        QMetaObject = QtCore.QMetaObject
        Qt = QtCore.Qt
    except ImportError:
        try:
            from PySide6 import QtCore
            QObject = QtCore.QObject
            QThread = QtCore.QThread
            Signal = QtCore.Signal
            QMetaObject = QtCore.QMetaObject
            Qt = QtCore.Qt
        except ImportError:
            # Fallback for non-Qt environments
            logger.warning("Qt not available, JobCenter will use stub implementation")
            QObject = object
            QThread = object
            Signal = lambda x: None
            QMetaObject = None
            Qt = None


class _Worker(QObject):
    """Worker object that runs in a separate thread.
    
    Executes a user-provided function and emits the result via signal.
    
    THREAD SAFETY:
    - This object lives in a worker thread
    - The function passed should NOT access Qt widgets or Maya scene
    - Use signals to communicate back to main thread
    """
    
    finished = Signal(object)  # Emits result when job completes
    error = Signal(object)     # Emits exception if job fails
    
    def __init__(self, fn):
        """Initialize worker with function to execute.
        
        Args:
            fn: Callable to execute in thread (must be thread-safe)
        """
        super().__init__()
        self._fn = fn
    
    def run(self):
        """Execute the function and emit result or error.
        
        This runs in the worker thread, NOT the main thread.
        """
        logger.debug(f"Worker thread starting: {self._fn}")
        try:
            result = self._fn()
            logger.debug(f"Worker thread completed successfully")
            # Signal emission is thread-safe in Qt
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"Worker thread failed: {e}", exc_info=True)
            self.error.emit(e)


class JobCenter(QObject):
    """Job center for executing background tasks in threads.
    
    Provides a thread-safe interface for running functions asynchronously
    without blocking the main UI thread.
    
    THREAD SAFETY DESIGN:
    1. Worker runs in separate thread
    2. Signals automatically use Qt's queued connections (thread-safe)
    3. Callbacks execute in main thread
    4. No shared mutable state between threads
    """
    
    def __init__(self, event_bus=None, parent=None):
        """Initialize job center.
        
        Args:
            event_bus: Optional EventBus for publishing job events
            parent: Optional QObject parent (for Qt object hierarchy)
        """
        super().__init__(parent)
        self._event_bus = event_bus
        self._thread = None
        self._worker = None
        self._job_count = 0  # Track number of jobs submitted
        logger.info("JobCenter initialized")
    
    def run_in_thread(self, fn, callback=None):
        """Execute a function in a background thread.
        
        THREAD SAFETY GUIDELINES:
        - fn() should NOT access Qt widgets or Maya scene directly
        - fn() should only work with data passed as parameters
        - callback() will execute in MAIN thread, safe for Qt/Maya operations
        
        Args:
            fn: Callable to execute (must be thread-safe, no Qt/Maya access)
            callback: Optional callback function(result) called in main thread
            
        Returns:
            None (result is delivered via callback or event)
        """
        self._job_count += 1
        job_id = self._job_count
        
        logger.info(f"Submitting job #{job_id} to background thread: {fn.__name__ if hasattr(fn, '__name__') else fn}")
        
        # Clean up previous thread if exists
        if self._thread is not None:
            if self._thread.isRunning():
                logger.warning("Previous job still running, waiting for completion...")
                self._thread.quit()
                self._thread.wait(5000)  # Wait up to 5 seconds
            
            # Clean up old thread
            self._cleanup_sync()
        
        # Create new thread and worker
        self._thread = QThread(self)  # Set parent for auto cleanup
        self._worker = _Worker(fn)
        
        # Move worker to thread (worker will live in the thread)
        self._worker.moveToThread(self._thread)
        
        # Connect signals (these use Qt::QueuedConnection automatically for cross-thread)
        # started signal -> worker.run (in worker thread)
        self._thread.started.connect(self._worker.run)
        
        # Worker signals -> handlers (back to main thread via queued connection)
        self._worker.finished.connect(lambda result: self._on_finished(result, callback, job_id))
        self._worker.error.connect(lambda error: self._on_error(error, callback, job_id))
        
        # Thread cleanup signals
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup)
        
        # Start thread
        logger.debug(f"Starting worker thread for job #{job_id}")
        self._thread.start()
    
    def _on_finished(self, result, callback, job_id):
        """Handle job completion.
        
        This executes in the MAIN thread (via Qt's queued connection).
        Safe to access Qt widgets and Maya scene here.
        
        Args:
            result: Result from the job function
            callback: Optional user callback
            job_id: Job identifier
        """
        logger.info(f"Job #{job_id} completed successfully, result: {result}")
        
        # Call user callback if provided (executes in main thread)
        if callback is not None:
            try:
                callback(result)
            except Exception as e:
                logger.error(f"Error in job callback: {e}", exc_info=True)
        
        # Publish event if event bus available (main thread, safe)
        if self._event_bus is not None:
            payload = {
                "job_id": job_id,
                "result": result,
                "status": "completed"
            }
            self._event_bus.publish("job/done", payload)
            logger.debug(f"Published job/done event for job #{job_id}")
    
    def _on_error(self, error, callback, job_id):
        """Handle job error.
        
        This executes in the MAIN thread (via Qt's queued connection).
        
        Args:
            error: Exception from the job function
            callback: Optional user callback (not called on error)
            job_id: Job identifier
        """
        logger.error(f"Job #{job_id} failed with error: {error}")
        
        # Publish error event if event bus available (main thread, safe)
        if self._event_bus is not None:
            payload = {
                "job_id": job_id,
                "error": str(error),
                "error_type": type(error).__name__,
                "status": "failed"
            }
            self._event_bus.publish("job/failed", payload)
            logger.debug(f"Published job/failed event for job #{job_id}")
    
    def _cleanup(self):
        """Clean up thread resources asynchronously.
        
        This is called when the thread finishes (in main thread).
        Uses deleteLater() for safe Qt object destruction.
        """
        logger.debug("Scheduling thread cleanup")
        if self._thread is not None:
            self._thread.deleteLater()
            self._thread = None
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None
    
    def _cleanup_sync(self):
        """Synchronous cleanup for thread switching."""
        logger.debug("Performing synchronous thread cleanup")
        if self._worker is not None:
            try:
                self._worker.deleteLater()
            except:
                pass
            self._worker = None
        if self._thread is not None:
            try:
                self._thread.deleteLater()
            except:
                pass
            self._thread = None
    
    def is_running(self):
        """Check if a job is currently running.
        
        Returns:
            bool: True if a job is running
        """
        return self._thread is not None and self._thread.isRunning()

