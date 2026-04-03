import shlex
import platform

BLOCKED_PATTERNS = [
    "rm -rf /", "shutdown", "reboot", "mkfs", "dd if=", ":(){:|:&};:"
]

WINDOWS_BLOCKED = [
    "format", "del /f /s /q", "rd /s /q", "powershell -enc", "reg delete"
]

ALLOWED_BASE_COMMANDS = {
    "echo", "pwd", "ls", "dir", "whoami", "date", "python", "pip", "where"
}

CONFIRMATION_KEYWORDS = {"install", "uninstall", "remove", "delete", "upgrade"}

def parse_base_command(command: str) -> str:
    try:
        parts = shlex.split(command)
        return parts[0].lower() if parts else ""
    except Exception:
        return ""

def is_blocked(command: str) -> bool:
    cmd = command.lower()
    for p in BLOCKED_PATTERNS:
        if p in cmd:
            return True
    if platform.system().lower() == "windows":
        for p in WINDOWS_BLOCKED:
            if p in cmd:
                return True
    return False

def is_allowed(command: str) -> bool:
    base = parse_base_command(command)
    return base in ALLOWED_BASE_COMMANDS

def requires_confirmation(command: str) -> bool:
    cmd = command.lower()
    return any(k in cmd for k in CONFIRMATION_KEYWORDS) or parse_base_command(command) in {"pip", "python"}