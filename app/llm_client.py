from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are ARIs, a safe personal AI assistant.
Use the run_command tool only when needed.
Prefer read-only commands.
Never attempt destructive or privileged actions.
"""


def get_model_response_with_tools(user_message: str):
    response = client.responses.create(
        model=settings.OPENAI_MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        tools=TOOLS
    )
    return response