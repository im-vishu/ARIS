import os
from openai import OpenAI, APIConnectionError, APITimeoutError, APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=_api_key, timeout=20.0) if _api_key else None


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((APIConnectionError, APITimeoutError, APIError)),
)
def handle_user_message(message: str):
    if client is None:
        raise RuntimeError("OPENAI_API_KEY is not set")
    resp = client.responses.create(model="gpt-4.1-mini", input=message)
    return {"reply": resp.output_text}