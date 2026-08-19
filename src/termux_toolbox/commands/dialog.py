import typer

from termux_toolbox.core.errors import handle_errors
from termux_toolbox.core.exec import run_termux_api
from termux_toolbox.core.output import is_json_mode, render

dialog_app = typer.Typer(help="Ask for input with on-screen dialog widgets.")

# Dialogs block until the user responds, so they need far longer than the default.
DIALOG_TIMEOUT = 300.0

TITLE_OPTION = typer.Option(None, "--title", "-t", help="Dialog title.")


def _run_dialog(widget: str, title: str | None, extra: list[str], ctx: typer.Context) -> None:
    args = [widget]
    if title is not None:
        args += ["-t", title]
    args += extra
    result = run_termux_api("termux-dialog", args=args, timeout=DIALOG_TIMEOUT)
    render(result, as_json=is_json_mode(ctx))


@dialog_app.command("text")
@handle_errors
def dialog_text(
    ctx: typer.Context,
    title: str | None = TITLE_OPTION,
    hint: str | None = typer.Option(None, "--hint", "-i", help="Placeholder hint text."),
    multiline: bool = typer.Option(
        False, "--multiline", "-m", help="Accept multiple lines instead of one."
    ),
    numeric: bool = typer.Option(False, "--numeric", "-n", help="Accept numbers only."),
    password: bool = typer.Option(False, "--password", "-p", help="Mask the entered text."),
) -> None:
    """Ask for free-text input."""
    if multiline and numeric:
        typer.echo("Error: --multiline cannot be combined with --numeric.", err=True)
        raise typer.Exit(code=1)

    extra = []
    if hint is not None:
        extra += ["-i", hint]
    if multiline:
        extra.append("-m")
    if numeric:
        extra.append("-n")
    if password:
        extra.append("-p")
    _run_dialog("text", title, extra, ctx)


@dialog_app.command("confirm")
@handle_errors
def dialog_confirm(
    ctx: typer.Context,
    title: str | None = TITLE_OPTION,
    hint: str | None = typer.Option(None, "--hint", "-i", help="Placeholder hint text."),
) -> None:
    """Show a yes/no confirmation dialog."""
    extra = ["-i", hint] if hint is not None else []
    _run_dialog("confirm", title, extra, ctx)


@dialog_app.command("checkbox")
@handle_errors
def dialog_checkbox(
    ctx: typer.Context,
    values: list[str] = typer.Argument(..., help="Values to offer as checkboxes."),
    title: str | None = TITLE_OPTION,
) -> None:
    """Pick any number of values using checkboxes."""
    _run_dialog("checkbox", title, ["-v", ",".join(values)], ctx)


@dialog_app.command("radio")
@handle_errors
def dialog_radio(
    ctx: typer.Context,
    values: list[str] = typer.Argument(..., help="Values to offer as radio buttons."),
    title: str | None = TITLE_OPTION,
) -> None:
    """Pick one value from radio buttons."""
    _run_dialog("radio", title, ["-v", ",".join(values)], ctx)


@dialog_app.command("sheet")
@handle_errors
def dialog_sheet(
    ctx: typer.Context,
    values: list[str] = typer.Argument(..., help="Values to offer in the bottom sheet."),
    title: str | None = TITLE_OPTION,
) -> None:
    """Pick one value from a sliding bottom sheet."""
    _run_dialog("sheet", title, ["-v", ",".join(values)], ctx)


@dialog_app.command("spinner")
@handle_errors
def dialog_spinner(
    ctx: typer.Context,
    values: list[str] = typer.Argument(..., help="Values to offer in the dropdown."),
    title: str | None = TITLE_OPTION,
) -> None:
    """Pick one value from a dropdown spinner."""
    _run_dialog("spinner", title, ["-v", ",".join(values)], ctx)


@dialog_app.command("counter")
@handle_errors
def dialog_counter(
    ctx: typer.Context,
    title: str | None = TITLE_OPTION,
    number_range: str | None = typer.Option(
        None, "--range", "-r", help="Comma-separated 'min,max,start', e.g. '1,100,50'."
    ),
) -> None:
    """Pick a number within a range."""
    extra = ["-r", number_range] if number_range is not None else []
    _run_dialog("counter", title, extra, ctx)


@dialog_app.command("date")
@handle_errors
def dialog_date(
    ctx: typer.Context,
    title: str | None = TITLE_OPTION,
    date_format: str | None = typer.Option(
        None, "--date-format", "-d", help="SimpleDateFormat pattern, e.g. 'dd-MM-yyyy k:m:s'."
    ),
) -> None:
    """Pick a date."""
    extra = ["-d", date_format] if date_format is not None else []
    _run_dialog("date", title, extra, ctx)


@dialog_app.command("time")
@handle_errors
def dialog_time(
    ctx: typer.Context,
    title: str | None = TITLE_OPTION,
) -> None:
    """Pick a time."""
    _run_dialog("time", title, [], ctx)


@dialog_app.command("speech")
@handle_errors
def dialog_speech(
    ctx: typer.Context,
    title: str | None = TITLE_OPTION,
    hint: str | None = typer.Option(None, "--hint", "-i", help="Placeholder hint text."),
) -> None:
    """Obtain speech using the device microphone."""
    extra = ["-i", hint] if hint is not None else []
    _run_dialog("speech", title, extra, ctx)
