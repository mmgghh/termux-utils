import functools

import typer


class TermuxToolboxError(Exception):
    """Base class for all termux-toolbox errors."""


class TermuxApiNotFound(TermuxToolboxError):
    def __init__(self, command: str):
        self.command = command
        super().__init__(
            f"'{command}' not found on PATH. Install the Termux:API app "
            "(https://f-droid.org/en/packages/com.termux.api/) and the "
            "termux-api package (`pkg install termux-api`)."
        )


class PermissionDenied(TermuxToolboxError):
    def __init__(self, command: str, stderr: str):
        self.command = command
        self.stderr = stderr
        super().__init__(
            f"'{command}' was denied permission by Android. Grant it under "
            "Android Settings > Apps > Termux:API > Permissions, then retry."
        )


class CommandFailed(TermuxToolboxError):
    def __init__(self, command: str, stderr: str, returncode: int):
        self.command = command
        self.stderr = stderr
        self.returncode = returncode
        super().__init__(f"'{command}' failed (exit {returncode}): {stderr.strip()}")


def handle_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TermuxToolboxError as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(code=1)

    return wrapper
