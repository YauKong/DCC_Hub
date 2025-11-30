"""AIGC service client stub implementation."""
from hub.core.logging import get_logger

logger = get_logger(__name__)


class AigcClientStub:
    """Stub implementation of AIGC service client.
    
    This is a placeholder implementation that logs method calls.
    Replace with actual HTTP/gRPC client when integrating with real AIGC service.
    """
    
    def __init__(self):
        """Initialize AIGC client stub."""
        logger.info("AigcClientStub initialized")
    
    def submit(self, inputs):
        """Submit a job to AIGC service.
        
        Args:
            inputs: Input parameters for AIGC job (dict)
            
        Returns:
            job_id: Fake job ID (string)
        """
        logger.info(f"AigcClientStub.submit() called with inputs: {inputs}")
        
        # Generate fake job ID
        import uuid
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        
        logger.debug(f"Generated fake job_id: {job_id}")
        return job_id
    
    def poll(self, job_id):
        """Poll job status from AIGC service.
        
        Args:
            job_id: Job ID to poll (string)
            
        Returns:
            status: Job status dict with 'state' and optional 'result'
        """
        logger.info(f"AigcClientStub.poll() called with job_id: {job_id}")
        
        # Return fake completed status
        status = {
            "state": "completed",
            "progress": 100,
            "result": {
                "output_path": "/fake/path/to/result.obj",
                "message": "Fake AIGC job completed successfully"
            }
        }
        
        logger.debug(f"Returning fake status: {status}")
        return status
    
    def cancel(self, job_id):
        """Cancel a running job.
        
        Args:
            job_id: Job ID to cancel (string)
            
        Returns:
            success: Whether cancellation was successful (bool)
        """
        logger.info(f"AigcClientStub.cancel() called with job_id: {job_id}")
        return True

