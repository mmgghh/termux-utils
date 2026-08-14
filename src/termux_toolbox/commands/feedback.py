from enum import Enum

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


@handle_errors
def tts_engines(ctx: typer.Context) -> None:
    """List available text-to-speech engines."""
    result = run_termux_api("termux-tts-engines")
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def speech_to_text(
    ctx: typer.Context,
    progress: bool = typer.Option(
        False, "--progress", "-p", help="Show partial results as they arrive."
    ),
) -> None:
    """Convert speech to text using the device microphone."""
    args = ["-p"] if progress else []
    result = run_termux_api("termux-speech-to-text", args=args, timeout=60.0)
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def download(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="URL to download."),
    description: str | None = typer.Option(None, "--description", help="Notification description."),
    title: str | None = typer.Option(None, "--title", help="Notification title."),
    path: str | None = typer.Option(None, "--path", help="Full path to save the downloaded file to."),
) -> None:
    """Download a URL using the system download manager."""
    args = []
    if description is not None:
        args += ["-d", description]
    if title is not None:
        args += ["-t", title]
    if path is not None:
        args += ["-p", path]
    args.append(url)
    result = run_termux_api("termux-download", args=args)
    render(result, as_json=is_json_mode(ctx))


class ShareAction(str, Enum):
    view = "view"
    send = "send"
    edit = "edit"


@handle_errors
def share(
    ctx: typer.Context,
    file: str | None = typer.Argument(None, help="File to share. Omit to share stdin text instead."),
    action: ShareAction = typer.Option(ShareAction.view, "--action", "-a", help="view, send, or edit."),
    content_type: str | None = typer.Option(
        None, "--content-type", "-c", help="MIME type (guessed if omitted)."
    ),
    default_receiver: bool = typer.Option(
        False,
        "--default-receiver",
        "-d",
        help="Share to the default receiver instead of showing a chooser.",
    ),
    title: str | None = typer.Option(None, "--title", "-t", help="Title for the shared content."),
) -> None:
    """Share a file, or stdin text if no file is given."""
    args = ["-a", action.value]
    if content_type is not None:
        args += ["-c", content_type]
    if default_receiver:
        args.append("-d")
    if title is not None:
        args += ["-t", title]
    if file is not None:
        args.append(file)
    result = run_termux_api("termux-share", args=args)
    render(result, as_json=is_json_mode(ctx))
