"""
http_server.py – FastAPI server for mini-modelvault.
Provides HTTP endpoints for inference, health, and status checks.
Handles file uploads, streaming, and logging.
"""
from fastapi import FastAPI, UploadFile, File, Form, Query
from mini_modelvault.observability.health import HealthChecker
from mini_modelvault.router.router import ModelRouter
from mini_modelvault.logger import setup_logger
import os

from dotenv import load_dotenv
load_dotenv()

from fastapi.responses import StreamingResponse
from mini_modelvault.services.inference_service import InferenceService

app = FastAPI()
logger = setup_logger(os.getenv('LOG_DIR', './logs'), 'server')
cfg = {k: v for k, v in os.environ.items() if k.startswith('MODEL_')}
router = ModelRouter(cfg, logger)
service = InferenceService(router, logger)
health = HealthChecker(logger)

def log_request_info(endpoint, **kwargs):
    """
    Log information about an incoming API request.

    Args:
        endpoint (str): The endpoint being called.
        **kwargs: Additional request parameters.
    """
    logger.info(f"Endpoint '{endpoint}' called with args: {kwargs}")

@app.post('/generate')
async def generate(
    text: str = Form(None), 
    file: UploadFile = File(None),
    stream: bool = Query(False, description="Enable streaming output")
):
    """
    Generate endpoint for running inference.

    Args:
        text (str): Text input for inference.
        file (UploadFile): Optional image file for vision models.
        stream (bool): Whether to stream the output.

    Returns:
        StreamingResponse or dict: Streaming output or result/error message.
    """
    log_request_info('/generate', text=text, file=file.filename if file else None, stream=stream)
    path = None
    # Error handling for missing or empty file
    if file is not None and (not file.filename or file.filename.strip() == ""):
        logger.error("Image is required but not provided.")
        return {"error": "Image is required."}
    if file:
        os.makedirs('assets', exist_ok=True)
        path = os.path.join('assets', file.filename)
        try:
            with open(path, 'wb') as f:
                f.write(await file.read())
            logger.info(f"Saved uploaded file to {path}")
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            return {"error": str(e)}
    try:
        if stream:
            def stream_fn():
                for chunk in service.run_stream(text or '', image_path=path):
                    logger.debug(f"Streaming chunk: {chunk}")
                    yield str(chunk)
            logger.info("Streaming response initiated.")
            return StreamingResponse(stream_fn(), media_type="text/event-stream")
        else:
            result = service.run(text or '', image_path=path)
            logger.info("Non-streaming response returned.")
            return {"result": result}
    except Exception as e:
        logger.error(f"Error during inference: {e}")
        return {"error": str(e)}

@app.get('/health')
def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Health status of the application.
    """
    logger.info("Health check endpoint called.")
    return health.status()

@app.get('/status')
def status():
    """
    Status endpoint.

    Returns:
        dict: Device resource usage and health status.
    """
    logger.info("Status endpoint called.")
    return health.device_status()