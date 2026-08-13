import json
import shutil
import subprocess

from termux_toolbox.core.errors import CommandFailed, PermissionDenied, TermuxApiNotFound

DEFAULT_TIMEOUT = 15.0


def run_termux_api(
    command: str,
    args: list[str] | None = None,
    input_data: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict | str:
    args = args or []

    if shutil.which(command) is None:
        raise TermuxApiNotFound(command)

    try:
        result = subprocess.run(
            [command, *args],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise CommandFailed(command, f"timed out after {timeout}s", -1) from exc

    if result.returncode != 0:
        if "permission" in result.stderr.lower():
            raise PermissionDenied(command, result.stderr)
        raise CommandFailed(command, result.stderr, result.returncode)

    stdout = result.stdout.strip()
    if not stdout:
        return ""

    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return stdout
