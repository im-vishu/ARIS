from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
SYSTEM_PROMPT = "You are ARIS. Respond in JSON for commands: {'action': 'run_command', 'command': 'cmd'}"

def get_model_response(user_message):
    # Phase 1 logic
    return '{"action":"run_command","command":"echo ARIS Online"}'
