"""
image_handler.py – Utility for handling image input in mini-modelvault.
Extracts images from text tags or file input, copies to assets, and returns updated paths.
"""
import os
import re
import shutil
from loguru import logger as default_logger
from typing import Optional, Tuple

def handle_image(input_text: Optional[str], input_image: Optional[str], logger=default_logger) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract image from <image> tag in text or from input_image, copy to assets, and return updated text and image path.

    Args:
        input_text (Optional[str]): Text input possibly containing <image> tag.
        input_image (Optional[str]): Path to image file, if provided.
        logger: loguru logger instance.

    Returns:
        Tuple[Optional[str], Optional[str]]: (updated_text, image_path or None)
    """
    if not input_image and input_text:
        image_tag = re.search(r"<image>(.*?)<image>", input_text)
        logger.debug(f"Image tag found: {image_tag}")
        if image_tag:
            image_path = image_tag.group(1).strip()
            if os.path.isfile(image_path):
                os.makedirs('assets', exist_ok=True)
                filename = os.path.basename(image_path)
                dest_path = os.path.join('assets', filename)
                # Skip copying if source and destination are the same file
                if os.path.abspath(image_path) != os.path.abspath(dest_path):
                    shutil.copy(image_path, dest_path)
                    logger.info(f"Copied image from {image_path} to {dest_path}")
                else:
                    logger.info(f"Skipped copying: '{image_path}' and '{dest_path}' are the same file.")
                input_image = dest_path
                input_text = re.sub(r"<image>.*?<image>", "", input_text).strip()
            else:
                logger.error(f"Image file '{image_path}' not found.")
                print(f"\n💥 Error: Image file '{image_path}' not found.")
                return input_text, None
    elif input_image:
        image_path = input_image.strip()
        if os.path.isfile(image_path):
            os.makedirs('assets', exist_ok=True)
            filename = os.path.basename(image_path)
            dest_path = os.path.join('assets', filename)
            # Skip copying if source and destination are the same file
            if os.path.abspath(image_path) != os.path.abspath(dest_path):
                shutil.copy(image_path, dest_path)
                logger.info(f"Copied image from {image_path} to {dest_path}")
            else:
                logger.info(f"Skipped copying: '{image_path}' and '{dest_path}' are the same file.")
            input_image = dest_path
        else:
            logger.error(f"Image file '{image_path}' not found.")
            print(f"\n💥 Error: Image file '{image_path}' not found.")
            return input_text, None
    return input_text, input_image 