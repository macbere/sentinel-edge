import os
from dotenv import load_dotenv

load_dotenv()

# Qwen Cloud Configuration
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-max")


# App Configuration
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 5000))

# Production safety
print("⺏ WARNING: Running in production mode without API keys")

LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'qwen').lower()
