import typer

from termux_toolbox.core.errors import handle_errors
from termux_toolbox.core.exec import run_termux_api
from termux_toolbox.core.output import is_json_mode, render

clipboard_app = typer.Typer(help="Read and write the system clipboard.")


@clipboard_app.command("get")
@handle_errors
def clipboard_get(ctx: typer.Context) -> None:
    """Print the current clipboard contents."""
    result = run_termux_api("termux-clipboard-get")
    render(result, as_json=is_json_mode(ctx))


@clipboard_app.command("set")
@handle_errors
def clipboard_set(
    ctx: typer.Context,
    text: str = typer.Argument(..., help="Text to copy to the clipboard."),
) -> None:
    """Set the clipboard contents."""
    result = run_termux_api("termux-clipboard-set", args=[text])
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def notify(
    ctx: typer.Context,
    title: str = typer.Argument(..., help="Notification title."),
    content: str = typer.Argument(..., help="Notification body text."),
) -> None:
    """Show an Android notification."""
    result = run_termux_api("termux-notification", args=["-t", title, "-c", content])
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def toast(
    ctx: typer.Context,
    text: str = typer.Argument(..., help="Text to show in the toast popup."),
) -> None:
    """Show a short-lived toast popup."""
    result = run_termux_api("termux-toast", args=[text])
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def vibrate(
    ctx: typer.Context,
    duration_ms: int = typer.Option(1000, "--duration-ms", help="Vibration duration in milliseconds."),
) -> None:
    """Vibrate the device."""
    result = run_termux_api("termux-vibrate", args=["-d", str(duration_ms)])
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def speak(
    ctx: typer.Context,
    text: str = typer.Argument(..., help="Text to speak aloud."),
) -> None:
    """Speak text aloud via text-to-speech."""
    result = run_termux_api("termux-tts-speak", args=[text])
    render(result, as_json=is_json_mode(ctx))
