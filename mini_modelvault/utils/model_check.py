import subprocess
import os

REQUIRED_MODELS = [
    os.getenv("MODEL_GENERAL", "llama3.2:3b"),
    os.getenv("MODEL_CODING", "qwen2.5-coder:3b"),
    os.getenv("MODEL_VISION", "llava-phi3:latest"),
]

def check_and_pull_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        installed_models = [line.split()[0] for line in result.stdout.strip().split('\n')[1:] if line]
    except Exception as e:
        print("[model_check] Could not check Ollama models. Is Ollama running and in your PATH?")
        return

    for model in REQUIRED_MODELS:
        if model not in installed_models:
            print(f"[model_check] Model '{model}' not found. Pulling with Ollama...")
            try:
                subprocess.run(["ollama", "pull", model], check=True)
            except Exception as e:
                print(f"[model_check] Failed to pull model '{model}': {e}")
        else:
            print(f"[model_check] Model '{model}' is already installed.") 