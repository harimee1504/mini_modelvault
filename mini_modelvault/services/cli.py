"""
cli.py – Typer application for interactive runs.
Provides the CLI entry point for running inference and interactive sessions in mini-modelvault.
Handles text and image input, logging, and error management.
"""
import typer
from mini_modelvault.router.router import ModelRouter
from mini_modelvault.logger import setup_logger
import os
from dotenv import load_dotenv
from mini_modelvault.utils import SpinnerHandler
from mini_modelvault.services.inference_service import InferenceService
from mini_modelvault.services.interactive_session import run_interactive
import re
import shutil
from mini_modelvault.utils.image_handler import handle_image

load_dotenv()

logger = setup_logger(os.getenv('LOG_DIR', './logs'), 'cli')


def main(
    input_text: str = typer.Option(None, '--text', '-t', help="Text query to process"),
    input_image: str = typer.Option(None, '--image', '-i', help="Path to the input image (optional)")
):
    """
    Run an inference via CLI. Supports interactive session with loader.

    Args:
        input_text (str): Text query to process, if provided.
        input_image (str): Path to the input image, if provided.

    This function initializes the model router and inference service, processes input,
    and either runs a one-off inference or starts an interactive session.
    Logs all actions and errors.
    """
    cfg = {k: v for k, v in os.environ.items() if k.startswith('MODEL_')}
    router = ModelRouter(cfg, logger)
    service = InferenceService(router, logger)

    logger.info("CLI started.")
    input_text, input_image = handle_image(input_text, input_image, logger)

    if input_text or input_image:
        with SpinnerHandler(logger=logger) as spinner:
            try:
                for chunk in service.run_stream(input_text or '', image_path=input_image):
                    logger.debug(f"Streaming chunk: {chunk}")
                    spinner.write_chunk(chunk)
            except Exception as e:
                logger.error(f"Error during inference: {e}")
                print(f"\n💥 Error: {e}")
        print()
        return

    logger.info("Starting interactive session.")
    try:
        run_interactive(service, logger)
    except Exception as e:
        logger.error(f"Unexpected error in interactive session: {e}", exc_info=True)
        print(f"\n💥 Error: {e}")

if __name__ == '__main__':
    """
    If this script is run directly, launch the Typer CLI application.
    """
    typer.run(main)
