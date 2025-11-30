"""Home panel - environment info and AIGC controls."""
from hub.core.logging import get_logger
from hub.core.qt_import import import_qt
QtWidgets = import_qt()

logger = get_logger(__name__)


class HomePanel(QtWidgets.QWidget):
    """Home panel displaying environment info and AIGC job controls."""

    def __init__(self, context=None, console_widget=None, parent=None):
        """Initialize Home panel.

        Args:
            context: ToolContext instance
            console_widget: Console widget for displaying messages
            parent: Parent widget
        """
        super().__init__(parent)
        self.context = context
        self.console_widget = console_widget

        # Create layout
        layout = QtWidgets.QVBoxLayout(self)

        # Environment info
        env_label = QtWidgets.QLabel("Home")
        layout.addWidget(env_label)

        # Add AIGC test button if JobCenter is available
        if self.context and hasattr(self.context, 'job_center') and self.context.job_center:
            aigc_button = QtWidgets.QPushButton("Submit Fake AIGC Job")
            aigc_button.clicked.connect(self._on_submit_aigc_job)
            layout.addWidget(aigc_button)
            logger.debug("Added AIGC test button to Home panel")

        layout.addStretch()

    def _on_submit_aigc_job(self):
        """Handle AIGC job submission button click.

        THREAD SAFETY:
        - Extracts all needed data in main thread
        - Passes only simple data types to worker thread
        - Worker function doesn't access Qt widgets or self
        - Callback executes in main thread for safe Qt/EventBus access
        """
        logger.info("AIGC job submission requested")

        if not self.context or not hasattr(self.context, 'services'):
            logger.error("Services not available")
            return

        if not hasattr(self.context, 'job_center') or not self.context.job_center:
            logger.error("JobCenter not available")
            return

        # Extract needed objects in MAIN thread
        aigc_client = self.context.services.get("aigc")
        if not aigc_client:
            logger.error("AIGC client not found in services")
            return

        evt_bus = self.context.evt_bus

        # Define AIGC job function - capture only the aigc_client, no self or Qt objects
        def aigc_job():
            """Fake AIGC job that simulates submission and polling.

            THREAD SAFE: Only accesses aigc_client (thread-safe stub),
            no Qt widgets, no Maya scene access.
            """
            import time

            logger.info("AIGC job started in background thread")

            # Submit job (aigc_client methods are thread-safe stubs)
            inputs = {
                "prompt": "Generate a sci-fi spaceship model",
                "style": "realistic",
                "resolution": "2048x2048"
            }
            job_id = aigc_client.submit(inputs)
            logger.info(f"AIGC job submitted: {job_id}")

            # Simulate waiting for job completion
            time.sleep(2)

            # Poll job status
            status = aigc_client.poll(job_id)
            logger.info(f"AIGC job polling completed: {job_id}")

            # Return simple data (no objects, no Qt, no Maya)
            return {
                "job_id": job_id,
                "status": status,
                "inputs": inputs
            }

        # Define completion callback - executes in MAIN thread
        def on_complete(result):
            """Callback executed in main thread after job completes.

            MAIN THREAD: Safe to access Qt widgets and EventBus here.
            """
            logger.info(f"AIGC job callback in main thread: {result.get('job_id')}")

            # Publish aigc/done event (main thread, safe)
            aigc_payload = {
                "job_id": result.get("job_id"),
                "status": result.get("status"),
                "inputs": result.get("inputs")
            }
            evt_bus.publish("aigc/done", aigc_payload)

        # Submit to JobCenter
        try:
            self.context.job_center.run_in_thread(aigc_job, callback=on_complete)
            logger.info("AIGC job submitted to JobCenter")

            # Show user feedback (main thread, safe)
            if self.console_widget:
                self.console_widget.append("[INFO] AIGC job submitted, please wait...\n")
        except Exception as e:
            logger.error(f"Error submitting AIGC job: {e}", exc_info=True)
