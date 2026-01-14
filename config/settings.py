import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_KEY = os.getenv("QUBRID_API_KEY")
    # Use the URL from .env, or fallback to the one you found
    API_URL = os.getenv("QUBRID_API_URL", "https://platform.qubrid.com/api/v1/qubridai/multimodal/chat")
    
    # EXACT Model ID from your playground snippet
    MODEL_NAME = "Qwen/Qwen3-VL-30B-A3B-Instruct" 

settings = Settings()