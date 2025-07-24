"""
router.py – Model routing logic for mini-modelvault.
Implements the ModelRouter class using LangChain and ChatOllama models.
Routes requests to general, coding, or vision models based on input.
"""
from langchain_core.runnables import RunnableBranch
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import base64
import re
from typing import Dict, Any


class ModelRouter:
    """
    LangChain v0.2+ ModelRouter using ChatOllama models.
    Applies SOLID principles and supports general, coding, and vision input.

    Args:
        config (Dict[str, Any]): Configuration dictionary with model names.
        logger: Logger instance for logging actions and errors.
    """

    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize the ModelRouter with configuration and logger.

        Args:
            config (Dict[str, Any]): Model configuration.
            logger: Logger instance.
        """
        self.logger = logger
        self._load_models(config)

    def _load_models(self, cfg: Dict[str, Any]):
        """
        Instantiate ChatOllama models and build routing logic.

        Args:
            cfg (Dict[str, Any]): Model configuration.
        """
        # Set default model names
        DEFAULTS = {
            "MODEL_GENERAL": "llama3.2:3b",
            "MODEL_CODING": "qwen2.5-coder:3b",
            "MODEL_VISION": "llava-phi3"
        }
        # Use config value if present, else fallback to default
        general_model = cfg.get("MODEL_GENERAL", DEFAULTS["MODEL_GENERAL"])
        coding_model = cfg.get("MODEL_CODING", DEFAULTS["MODEL_CODING"])
        vision_model = cfg.get("MODEL_VISION", DEFAULTS["MODEL_VISION"])
        try:
            self.general = ChatOllama(model=general_model)
            self.coding = ChatOllama(model=coding_model)
            self.vision = ChatOllama(model=vision_model)
            self.logger.info(f"Models loaded: general={general_model}, coding={coding_model}, vision={vision_model}.")
        except Exception as e:
            self.logger.error(f"Failed to load models: {e}")
            raise
        self.output_parser = StrOutputParser()
        self.router_model = ChatOllama(model=cfg["MODEL_GENERAL"])
        self.router_chain = (
            self.router_model
            | self.output_parser
        )
        self.router_branch = RunnableBranch(
            (lambda x: "image_path" in x and x["image_path"] is not None, self._vision_invoke),
            (lambda x: self._classify(x["input"]) == "coding", self._coding_invoke),
            self._general_invoke
        )

    def _classify(self, input_text: str) -> str:
        """
        Classify input text as 'general', 'coding', or 'vision' using the router model.

        Args:
            input_text (str): The input text to classify.

        Returns:
            str: The classification label.
        """
        self.logger.debug(f"Classifying input: {input_text}")
        result = self.router_chain.invoke([HumanMessage(content=f"Classify the following input into one of: general, coding, vision:\n{input_text}")])
        match = re.search(r'\b(general|coding|vision)\b', result.lower())
        if match:
            label = match.group(1)
            self.logger.info(f"Input classified as: {label}")
            return label
        self.logger.warning(f"Classifier returned unexpected result: {result}")
        return result.strip().lower()

    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode an image file to a base64 string.

        Args:
            image_path (str): Path to the image file.

        Returns:
            str: Base64-encoded image string.
        """
        try:
            with open(image_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            self.logger.debug(f"Encoded image {image_path} to base64.")
            return encoded
        except Exception as e:
            self.logger.error(f"Failed to encode image {image_path}: {e}")
            raise

    def _vision_invoke(self, x: dict) -> str:
        """
        Invoke the vision model for image-based input.

        Args:
            x (dict): Input dictionary with 'input' and 'image_path'.

        Returns:
            str: Model response.
        """
        self.logger.info("Routing to vision model.")
        image_base64 = self.encode_image_to_base64(x["image_path"])
        image_url = f"data:image/png;base64,{image_base64}"
        message = HumanMessage(content=[
            {"type": "text", "text": x["input"]},
            {"type": "image_url", "image_url": {"url": image_url}}
        ])
        result = self.vision.invoke([message])
        self.logger.debug(f"Vision model result: {result}")
        return result

    def _general_invoke(self, x: dict) -> str:
        """
        Invoke the general model for text input.

        Args:
            x (dict): Input dictionary with 'input'.

        Returns:
            str: Model response.
        """
        self.logger.info("Routing to general model.")
        message = HumanMessage(content=x["input"])
        result = self.general.invoke([message])
        self.logger.debug(f"General model result: {result}")
        return result

    def _coding_invoke(self, x: dict) -> str:
        """
        Invoke the coding model for code-related input.

        Args:
            x (dict): Input dictionary with 'input'.

        Returns:
            str: Model response.
        """
        self.logger.info("Routing to coding model.")
        message = HumanMessage(content=x["input"])
        result = self.coding.invoke([message])
        self.logger.debug(f"Coding model result: {result}")
        return result

    def route(self, text: str, image_path: str = None):
        """
        Routes the input to the appropriate model and returns (model_type, response).
        Logs both the classifier model and the response model.

        Args:
            text (str): Input text for inference.
            image_path (str, optional): Path to input image.

        Returns:
            tuple: (model_type, response)
        """
        payload = {"input": text}
        if image_path:
            payload["image_path"] = image_path
            self.logger.info(f"Image input detected: {image_path}")
            try:
                image_base64 = self.encode_image_to_base64(image_path)
                image_url = f"data:image/png;base64,{image_base64}"
                message = HumanMessage(content=[
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ])
                result = self.vision.invoke([message])
                self.logger.info("Vision model invoked successfully.")
                return ("vision", result)
            except Exception as e:
                self.logger.error(f"Vision model invocation failed: {e}")
                raise
        else:
            self.logger.info(f"Text input: {text}")
            try:
                message = HumanMessage(content=text)
                if self._classify(text) == "coding":
                    model = self.coding
                    model_type = "coding"
                else:
                    model = self.general
                    model_type = "general"
                result = model.invoke([message])
                self.logger.info(f"Model '{model_type}' invoked successfully.")
                return (model_type, result)
            except Exception as e:
                self.logger.error(f"Text model invocation failed: {e}")
                raise

    def stream_route(self, text: str, image_path: str = None):
        """
        Stream output from the appropriate model. Returns (model_type, stream).

        Args:
            text (str): Input text for inference.
            image_path (str, optional): Path to input image.

        Returns:
            tuple: (model_type, stream)
        """
        payload = {"input": text}
        if image_path:
            payload["image_path"] = image_path
            self.logger.info(f"Image input detected: {image_path}")
            try:
                image_base64 = self.encode_image_to_base64(image_path)
                image_url = f"data:image/png;base64,{image_base64}"
                message = HumanMessage(content=[
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ])
                stream = self.vision.stream([message])
                self.logger.info("Vision model streaming started.")
                model_type = "vision"
            except Exception as e:
                self.logger.error(f"Vision model streaming failed: {e}")
                raise
        else:
            self.logger.info(f"Text input: {text}")
            try:
                message = HumanMessage(content=text)
                if self._classify(text) == "coding":
                    model = self.coding
                    model_type = "coding"
                else:
                    model = self.general
                    model_type = "general"
                stream = model.stream([message])
                self.logger.info(f"Model '{model_type}' streaming started.")
            except Exception as e:
                self.logger.error(f"Text model streaming failed: {e}")
                raise
        def stream_with_type():
            for chunk in stream:
                self.logger.debug(f"Stream chunk: {chunk}")
                yield chunk.content if hasattr(chunk, "content") else chunk
        return (model_type, stream_with_type())
