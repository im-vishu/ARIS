from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are ARIs, a safe personal AI assistant.
Use the run_command tool only when needed.
Prefer read-only commands.
Never attempt destructive or privileged actions.
"""

TOOLS = [
    {
        "type": "function",
        "name": "run_command",
        "description": "Run a shell command on user's machine",
        "parameters": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "open_website",
        "description": "Open a website in default browser",
        "parameters": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "send_email",
        "description": "Send email via SMTP",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"}
            },
            "required": ["to", "subject", "body"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "create_reminder",
        "description": "Create reminder with ISO datetime",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "when_iso": {"type": "string"}
            },
            "required": ["title", "when_iso"],
            "additionalProperties": False
        }
    }
]

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