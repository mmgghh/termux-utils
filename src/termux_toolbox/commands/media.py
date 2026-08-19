from enum import Enum

import typer

from termux_toolbox.core.errors import handle_errors
from termux_toolbox.core.exec import run_termux_api
from termux_toolbox.core.output import is_json_mode, render

camera_app = typer.Typer(help="Take photos with device cameras.")
media_app = typer.Typer(help="Control on-device media playback.")
mic_app = typer.Typer(help="Record audio with the device microphone.")


# Convenience aliases for the two IDs Android assigns by convention; any other ID
# from 'mgt camera info' can be passed through directly.
CAMERA_ALIASES = {"back": "0", "front": "1"}


@camera_app.command("photo")
@handle_errors
def camera_photo(
    ctx: typer.Context,
    output_path: str = typer.Argument(..., help="File path to save the photo to."),
    camera: str = typer.Option(
        "back", "--camera", "-c", help="'front', 'back', or a camera ID from 'mgt camera info'."
    ),
) -> None:
    """Take a photo."""
    camera_id = CAMERA_ALIASES.get(camera, camera)
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


class MicEncoder(str, Enum):
    aac = "aac"
    amr_wb = "amr_wb"
    amr_nb = "amr_nb"
    opus = "opus"


@mic_app.command("record")
@handle_errors
def mic_record(
    ctx: typer.Context,
    output_path: str | None = typer.Argument(
        None, help="File path to save the recording to. Omit to record with device defaults."
    ),
    duration_s: int = typer.Option(
        10, "--duration", help="Recording length in seconds; 0 records until stopped."
    ),
    encoder: MicEncoder | None = typer.Option(None, "--encoder", help="Recording encoder."),
    bitrate: int | None = typer.Option(None, "--bitrate", help="Recording bitrate in kbps."),
    sample_rate: int | None = typer.Option(
        None, "--sample-rate", help="Recording sampling rate in Hz."
    ),
    channels: int | None = typer.Option(None, "--channels", help="Channel count, e.g. 1 or 2."),
) -> None:
    """Start recording audio from the microphone."""
    args = ["-f", output_path] if output_path is not None else ["-d"]
    args += ["-l", str(duration_s)]
    if encoder is not None:
        args += ["-e", encoder.value]
    if bitrate is not None:
        args += ["-b", str(bitrate)]
    if sample_rate is not None:
        args += ["-r", str(sample_rate)]
    if channels is not None:
        args += ["-c", str(channels)]
    result = run_termux_api("termux-microphone-record", args=args)
    render(result, as_json=is_json_mode(ctx))


@mic_app.command("info")
@handle_errors
def mic_info(ctx: typer.Context) -> None:
    """Show information about the current recording."""
    result = run_termux_api("termux-microphone-record", args=["-i"])
    render(result, as_json=is_json_mode(ctx))


@mic_app.command("stop")
@handle_errors
def mic_stop(ctx: typer.Context) -> None:
    """Stop the current recording."""
    result = run_termux_api("termux-microphone-record", args=["-q"])
    render(result, as_json=is_json_mode(ctx))
