import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "30"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))


def get_llm_client() -> OpenAI:
    return OpenAI(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
        timeout=LLM_TIMEOUT,
        max_retries=LLM_MAX_RETRIES,
    )