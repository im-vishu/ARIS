import subprocess
from dataclasses import dataclass

@dataclass
class CommandResult:
    success: bool
    command: str
    stdout: str
    stderr: str
    returncode: int

def run_command(command: str, timeout: int = 20) -> CommandResult:
    try:
        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return CommandResult(
            success=completed.returncode == 0,
            command=command,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
            returncode=completed.returncode
        )
    except subprocess.TimeoutExpired:
        return CommandResult(
            success=False,
            command=command,
            stdout="",
            stderr="Command timed out",
            returncode=124
        )
    except Exception as e:
        return CommandResult(
            success=False,
            command=command,
            stdout="",
            stderr=str(e),
            returncode=1
        )