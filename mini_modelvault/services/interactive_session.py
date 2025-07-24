"""
interactive_session.py – Interactive CLI session for mini-modelvault.
Provides a loop for user interaction, streaming inference, and error handling.
"""
# src/cli/interactive_session.py
from mini_modelvault.utils.spinner_handler import SpinnerHandler
from mini_modelvault.utils.image_handler import handle_image
from typer import prompt, echo
from loguru import logger
import os
import re
import shutil

def run_interactive(service, logger=logger):
    """
    Run an interactive CLI session with detailed logging and image tag handling.

    Args:
        service: Inference service instance.
        logger: Logger instance (default: loguru logger).

    The session continues until the user types '/bye', 'exit', or 'quit'.
    Handles image tags in user input and streams inference results.
    Logs all actions and errors.
    """
    echo("👋 Welcome to Mini-ModelVault CLI! Type '/bye' to exit.\n")
    logger.info("Interactive session started.")
    try:
        while True:
            try:
                user_input = prompt("\n\nYou")
                logger.debug(f"User input: {user_input}")
                if user_input.strip().lower() in ('/bye', 'exit', 'quit'):
                    echo("👋 Goodbye!")
                    logger.info("User exited interactive session.")
                    break
                # Handle <image> tag in user input
                input_text, input_image = handle_image(user_input, None, logger)
                with SpinnerHandler(logger=logger) as spinner:
                    try:
                        for chunk in service.run_stream(input_text or '', image_path=input_image):
                            logger.debug(f"Streamed chunk: {chunk}")
                            spinner.write_chunk(chunk)
                    except Exception as e:
                        logger.error(f"Error during streaming in interactive session: {e}", exc_info=True)
                        print(f"\n💥 Error: {e}")
            except Exception as e:
                logger.error(f"Error in interactive session loop: {e}", exc_info=True)
                print(f"\n💥 Error: {e}")
    except (EOFError, KeyboardInterrupt):
        echo("\n👋 Session ended by user.")
        logger.info("Interactive session ended by user.")
