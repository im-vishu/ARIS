import json
from app.llm_client import get_model_response_with_tools
from app.safety import is_allowed, is_blocked, requires_confirmation
from app.tools.command_runner import run_command
from app.utils.logger import log_event

def extract_text_and_tool_call(response):
    text_parts = []
    tool_call = None

    for item in response.output:
        if item.type == "message":
            for c in item.content:
                if c.type == "output_text":
                    text_parts.append(c.text)
        elif item.type == "function_call" and item.name == "run_command":
            args = json.loads(item.arguments)
            tool_call = {"name": item.name, "arguments": args}

    return "\n".join(text_parts).strip(), tool_call

def handle_user_message(user_message: str):
    log_event("user_message", {"text": user_message})

    response = get_model_response_with_tools(user_message)
    text_reply, tool_call = extract_text_and_tool_call(response)

    if not tool_call:
        log_event("assistant_reply", {"text": text_reply})
        return {"type": "text", "message": text_reply or "Okay."}

    command = tool_call["arguments"].get("command", "").strip()
    log_event("tool_call", {"tool": "run_command", "command": command})

    if not command:
        return {"type": "text", "message": "I could not determine a valid command."}
    if is_blocked(command):
        return {"type": "text", "message": f"❌ Blocked for safety: `{command}`"}
    if not is_allowed(command):
        return {"type": "text", "message": f"❌ Command not allowed: `{command}`"}
    if requires_confirmation(command):
        return {"type": "confirm", "command": command, "message": f"⚠️ Confirm execution (yes/no): `{command}`"}

    result = run_command(command)
    log_event("command_result", result.__dict__)
    return {"type": "text", "message": format_command_result(result)}

def execute_confirmed_command(command: str):
    if is_blocked(command):
        return f"❌ Blocked for safety: `{command}`"
    if not is_allowed(command):
        return f"❌ Command not allowed: `{command}`"

    result = run_command(command)
    log_event("command_result", result.__dict__)
    return format_command_result(result)

def format_command_result(result):
    if result.success:
        return f"✅ `{result.command}`\n{result.stdout or '(no output)'}"
    return f"❌ `{result.command}` failed (code {result.returncode})\n{result.stderr or '(no error text)'}"