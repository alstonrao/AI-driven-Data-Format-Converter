import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def get_api_key():
    return os.getenv("OPENAI_API_KEY")

def get_base_url():
    return os.getenv("OPENAI_BASE_URL")

def get_model_name():
    return os.getenv("OPENAI_MODEL_NAME", "gpt-4-turbo-preview")

def get_output_dir():
    return os.getenv("OUTPUT_DIR", "outputs/runs")
