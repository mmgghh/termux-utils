import sys

import questionary
import typer
from typer.main import get_command
from typer.testing import CliRunner


class Cancelled(Exception):
    """Raised when the user backs out of a prompt (Ctrl+C/Esc)."""


def ask_text(message: str, default: str | None = None) -> str:
    result = questionary.text(message, default=default or "").ask()
    if result is None:
        raise Cancelled
    return result


def ask_confirm(message: str, default: bool = False) -> bool:
    result = questionary.confirm(message, default=default).ask()
    if result is None:
        raise Cancelled
    return result


def ask_select(message: str, choices: list[str], default: str | None = None) -> str:
    result = questionary.select(message, choices=choices, default=default).ask()
    if result is None:
        raise Cancelled
    return result


def ask_continue(message: str = "Press any key to continue...") -> None:
    questionary.press_any_key_to_continue(message).ask()


def _default_str(default: object) -> str | None:
    if default is None:
        return None
    return str(getattr(default, "value", default))


def _label(param) -> str:
    name = param.opts[0] if param.opts else param.name
    return f"{name} ({param.help})" if getattr(param, "help", None) else name


def _prompt_param(param) -> list[str]:
    is_argument = param.param_type_name == "argument"
    flag = None if is_argument else param.opts[0]
    label = _label(param)

    if getattr(param, "is_flag", False):
        if getattr(param, "secondary_opts", None):
            choice = ask_select(f"{label}?", choices=["Yes", "No", "Leave unset"])
            if choice == "Yes":
                return [param.opts[0]]
            if choice == "No":
                return [param.secondary_opts[0]]
            return []
        if ask_confirm(f"{label}?", default=bool(param.default)):
            return [flag]
        return []

    variadic = param.nargs == -1 or getattr(param, "multiple", False)
    if variadic:
        values: list[str] = []
        while True:
            value = ask_text(f"{label} (value {len(values) + 1}, blank to stop)")
            if not value:
                break
            values.append(value)
        if flag is None:
            return values
        result: list[str] = []
        for value in values:
            result += [flag, value]
        return result

    optional = not param.required and param.default is None
    if optional and not ask_confirm(f"Set {label}?", default=False):
        return []

    choices = getattr(param.type, "choices", None)
    default_str = _default_str(param.default)
    if choices:
        value = ask_select(label, choices=list(choices), default=default_str if default_str in choices else None)
    else:
        value = ask_text(label, default=default_str)
        while not value and param.required:
            value = ask_text(f"{label} (required)")

    if flag is None:
        return [value]
    return [flag, value]


def build_argv(cmd) -> list[str]:
    argv: list[str] = []
    for param in cmd.params:
        argv.extend(_prompt_param(param))
    return argv


def _is_interactive_terminal() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def run(app: typer.Typer) -> None:
    if not _is_interactive_terminal():
        typer.echo("Error: 'mgt interactive' needs a real terminal.", err=True)
        raise typer.Exit(code=1)

    try:
        json_mode = ask_confirm("Use JSON output for results?", default=False)
    except Cancelled:
        return
    base_args = ["--json"] if json_mode else []

    root = get_command(app)
    runner = CliRunner()

    stack = [root]
    path: list[str] = []
    while True:
        group = stack[-1]
        choices = sorted(group.commands)
        if len(stack) > 1:
            choices.append("Back")
        choices.append("Exit")

        try:
            selection = ask_select(" > ".join(path) or "mgt", choices=choices)
        except Cancelled:
            selection = "Back" if len(stack) > 1 else "Exit"

        if selection == "Exit":
            return
        if selection == "Back":
            stack.pop()
            path.pop()
            continue

        cmd = group.commands[selection]
        if hasattr(cmd, "commands"):
            stack.append(cmd)
            path.append(selection)
            continue

        try:
            argv = build_argv(cmd)
        except Cancelled:
            continue

        result = runner.invoke(app, base_args + path + [selection] + argv)
        typer.echo(result.output, nl=False)
        if result.exception is not None and not isinstance(result.exception, SystemExit):
            typer.echo(f"Unexpected error: {result.exception}", err=True)
        ask_continue()
