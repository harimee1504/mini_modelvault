"""
spinner_handler.py – Utility for displaying a spinner during long-running CLI operations.
Implements SpinnerHandler context manager for streaming output with logging.
"""
from yaspin import yaspin
from yaspin.spinners import Spinners
from loguru import logger as default_logger

class SpinnerHandler:
    """
    Context manager for displaying a spinner and streaming output in the CLI.

    Args:
        text (str): Optional spinner text.
        logger: Logger instance (default: loguru logger).
    """
    def __init__(self, text="", logger=None):
        """
        Initialize the SpinnerHandler.

        Args:
            text (str): Spinner text.
            logger: Logger instance.
        """
        self.spinner = yaspin(Spinners.line, text=text)
        self.first_chunk = True
        self.logger = logger or default_logger

    def __enter__(self):
        """
        Start the spinner when entering the context.

        Returns:
            SpinnerHandler: The context manager instance.
        """
        self.spinner.start()
        self.logger.debug("Spinner started.")
        return self

    def write_chunk(self, chunk):
        """
        Write a chunk of output, stopping the spinner on the first chunk.

        Args:
            chunk: Output chunk to write.
        """
        if self.first_chunk:
            self.spinner.stop()
            print("🤖 ", end="", flush=True)
            self.first_chunk = False
            self.logger.debug("First chunk written, spinner stopped.")
        print(chunk, end="", flush=True)
        self.logger.debug(f"Chunk output: {chunk}")

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stop the spinner and handle any exceptions on exit.

        Args:
            exc_type: Exception type.
            exc_value: Exception value.
            traceback: Exception traceback.
        """
        if exc_type:
            self.spinner.fail("💥")
            self.logger.error(f"Spinner failed due to exception: {exc_value}", exc_info=True)
        elif self.first_chunk:
            self.spinner.ok("✅")
            self.logger.debug("Spinner completed with no output.")
