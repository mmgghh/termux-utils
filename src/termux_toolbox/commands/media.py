import typer

from termux_toolbox.core.errors import handle_errors
from termux_toolbox.core.exec import run_termux_api
from termux_toolbox.core.output import is_json_mode, render

camera_app = typer.Typer(help="Take photos with device cameras.")
media_app = typer.Typer(help="Control on-device media playback.")
mic_app = typer.Typer(help="Record audio with the device microphone.")


@camera_app.command("photo")
@handle_errors
def camera_photo(
    ctx: typer.Context,
    output_path: str = typer.Argument(..., help="File path to save the photo to."),
    camera: str = typer.Option("back", "--camera", help="'front' or 'back'."),
) -> None:
    """Take a photo."""
    camera_id = "0" if camera == "back" else "1"
    result = run_termux_api("termux-camera-photo", args=["-c", camera_id, output_path])
    render(result, as_json=is_json_mode(ctx))


@media_app.command("play")
@handle_errors
def media_play(
    ctx: typer.Context,
    file: str = typer.Argument(..., help="Path to the media file to play."),
) -> None:
    """Play a media file."""
    result = run_termux_api("termux-media-player", args=["play", file])
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
