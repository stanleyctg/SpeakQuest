from dotenv import load_dotenv
import os

def load_config_from_env():
    load_dotenv()
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }