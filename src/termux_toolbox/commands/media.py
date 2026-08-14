from enum import Enum

import typer

from termux_toolbox.core.errors import handle_errors
from termux_toolbox.core.exec import run_termux_api
from termux_toolbox.core.output import is_json_mode, render

camera_app = typer.Typer(help="Take photos with device cameras.")
media_app = typer.Typer(help="Control on-device media playback.")
mic_app = typer.Typer(help="Record audio with the device microphone.")


class Camera(str, Enum):
    front = "front"
    back = "back"


@camera_app.command("photo")
@handle_errors
def camera_photo(
    ctx: typer.Context,
    output_path: str = typer.Argument(..., help="File path to save the photo to."),
    camera: Camera = typer.Option(Camera.back, "--camera", help="'front' or 'back'."),
) -> None:
    """Take a photo."""
    camera_id = "0" if camera == Camera.back else "1"
    result = run_termux_api("termux-camera-photo", args=["-c", camera_id, output_path])
    render(result, as_json=is_json_mode(ctx))


@camera_app.command("info")
@handle_errors
def camera_info(ctx: typer.Context) -> None:
    """Show information about available cameras."""
    result = run_termux_api("termux-camera-info")
    render(result, as_json=is_json_mode(ctx))


@media_app.command("play")
@handle_errors
def media_play(
    ctx: typer.Context,
    file: str | None = typer.Argument(
        None, help="Path to the media file to play. Omit to resume playback."
    ),
) -> None:
    """Play a media file, or resume playback if no file is given."""
    args = ["play", file] if file is not None else ["play"]
    result = run_termux_api("termux-media-player", args=args)
    render(result, as_json=is_json_mode(ctx))


@media_app.command("pause")
@handle_errors
def media_pause(ctx: typer.Context) -> None:
    """Pause media playback."""
    result = run_termux_api("termux-media-player", args=["pause"])
    render(result, as_json=is_json_mode(ctx))


@media_app.command("stop")
@handle_errors
def media_stop(ctx: typer.Context) -> None:
    """Stop media playback."""
    result = run_termux_api("termux-media-player", args=["stop"])
    render(result, as_json=is_json_mode(ctx))


@media_app.command("info")
@handle_errors
def media_info(ctx: typer.Context) -> None:
    """Show current playback information."""
    result = run_termux_api("termux-media-player", args=["info"])
    render(result, as_json=is_json_mode(ctx))


@media_app.command("scan")
@handle_errors
def media_scan(
    ctx: typer.Context,
    files: list[str] = typer.Argument(..., help="File paths to scan and add to the media store."),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Scan directories recursively."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output."),
) -> None:
    """Scan file(s) and add them to the media content provider."""
    args = []
    if recursive:
        args.append("-r")
    if verbose:
        args.append("-v")
    args += files
    result = run_termux_api("termux-media-scan", args=args, timeout=30.0)
    render(result, as_json=is_json_mode(ctx))


@mic_app.command("record")
@handle_errors
def mic_record(
    ctx: typer.Context,
    output_path: str = typer.Argument(..., help="File path to save the recording to."),
    duration_s: int = typer.Option(10, "--duration", help="Recording length in seconds."),
) -> None:
    """Record audio from the microphone."""
    result = run_termux_api(
        "termux-microphone-record", args=["-f", output_path, "-l", str(duration_s)]
    )
    render(result, as_json=is_json_mode(ctx))
