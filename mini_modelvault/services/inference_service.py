"""
inference_service.py – Service for running inference using a model router.
Handles both streaming and non-streaming inference, logging all actions and errors.
"""

import json

class InferenceService:
    """
    Service for running inference using a model router.

    Args:
        router: ModelRouter instance for routing inference requests.
        logger: Logger instance for logging actions and errors.
    """
    def __init__(self, router, logger):
        """
        Initialize the InferenceService.

        Args:
            router: ModelRouter instance.
            logger: Logger instance.
        """
        self.router = router
        self.logger = logger

    def run_stream(self, text: str, image_path: str = None):
        """
        Run streaming inference.

        Args:
            text (str): Input text for inference.
            image_path (str, optional): Path to input image.

        Yields:
            str: Chunks of the inference result.
        """
        self.logger.info(f"Running stream inference. Text: {text}, Image: {image_path}")
        try:
            model_type, stream = self.router.stream_route(text, image_path=image_path)
            chunks = []
            for chunk in stream:
                self.logger.debug(f"Streamed chunk: {chunk}")
                chunks.append(chunk)
                yield chunk
            # Log the full response after streaming is complete
            full_response = ''.join(str(c) for c in chunks)
            log_obj = {
                "model_type": model_type,
                "input_text": text,
                "image_path": image_path,
                "response": full_response
            }
            self.logger.info(json.dumps(log_obj, ensure_ascii=False))
        except Exception as e:
            self.logger.error(f"Stream inference failed: {e}")
            raise

    def run(self, text: str, image_path: str = None):
        """
        Run non-streaming inference.

        Args:
            text (str): Input text for inference.
            image_path (str, optional): Path to input image.

        Returns:
            str: Inference result.
        """
        self.logger.info(f"Running inference. Text: {text}, Image: {image_path}")
        try:
            model_type, result = self.router.route(text, image_path=image_path)
            log_obj = {
                "model_type": model_type,
                "input_text": text,
                "image_path": image_path,
                "response": result
            }
            self.logger.info(json.dumps(log_obj, ensure_ascii=False))
            self.logger.info("Inference completed successfully.")
            return result
        except Exception as e:
            self.logger.error(f"Inference failed: {e}")
            raise
