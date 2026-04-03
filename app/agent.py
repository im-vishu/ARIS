import json
from app.llm_client import get_model_response_with_tools
from app.safety import is_allowed, is_blocked, requires_confirmation
from app.tools.command_runner import run_command
from app.utils.logger import log_event


from app.tools.browser_tool import open_website
from app.tools.email_tool import send_email
from app.tools.reminder_tool import create_reminder
from app.validation import is_valid_url, is_valid_email, is_valid_iso_datetime


from app.tools.whatsapp_tool import send_whatsapp
from app.tools.calendar_tool import create_calendar_event
from app.validation import is_valid_phone_e164, is_valid_iso_datetime
from app.config import settings


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
    log_event("user_message", {"message": user_message})
    response = get_model_response_with_tools(user_message)
    log_event("model_response", {"response": response.__dict__})

    text, tool_call = extract_text_and_tool_call(response)

    if tool_call:
        name = tool_call["name"]
        args = tool_call["arguments"]

        if name == "run_command":
            # keep your existing run_command flow
            ...

        elif name == "open_website":
            url = args.get("url", "").strip()
            if not is_valid_url(url):
                return {"type": "text", "message": "❌ Invalid URL."}
            result = open_website(url)
            return {"type": "text", "message": f"✅ Opened: {result['url']}" if result["success"] else "❌ Could not open URL."}

        elif name == "send_email":
            to = args.get("to", "").strip()
            subject = args.get("subject", "").strip()
            body = args.get("body", "").strip()
            if not is_valid_email(to):
                return {"type": "text", "message": "❌ Invalid email address."}
            if not subject or not body:
                return {"type": "text", "message": "❌ Subject/body cannot be empty."}
            return {"type": "confirm", "command": f"send_email::{to}::{subject}::{body}", "message": f"⚠️ Confirm send email to `{to}`?"}

        elif name == "create_reminder":
            title = args.get("title", "").strip()
            when_iso = args.get("when_iso", "").strip()
            if not title or not is_valid_iso_datetime(when_iso):
                return {"type": "text", "message": "❌ Invalid reminder input (use ISO datetime)."}
            result = create_reminder(title, when_iso)
            return {"type": "text", "message": f"✅ Reminder created: {result['reminder']['title']} at {result['reminder']['when']}"}

def execute_confirmed_command(command: str):
    if command.startswith("send_email::"):
        _, to, subject, body = command.split("::", 3)
        result = send_email(to, subject, body)
        return f"✅ Email sent to {result['to']} (subject: {result['subject']})"
    # else existing command execution flow
    ...

    result = run_command(command)
    log_event("command_result", result.__dict__)
    return format_command_result(result)

def format_command_result(result):
    if result.success:
        return f"✅ `{result.command}`\n{result.stdout or '(no output)'}"
    return f"❌ `{result.command}` failed (code {result.returncode})\n{result.stderr or '(no error text)'}"