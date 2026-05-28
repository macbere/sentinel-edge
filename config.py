import os
from dotenv import load_dotenv

load_dotenv()

# Qwen Cloud Configuration
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen-max"

# App Configuration
DEBUG = True
HOST = "127.0.0.1"
PORT = 5000
