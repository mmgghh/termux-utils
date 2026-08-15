from enum import Enum

import typer

from termux_toolbox.core.errors import handle_errors
from termux_toolbox.core.exec import run_termux_api
from termux_toolbox.core.output import is_json_mode, render

wifi_app = typer.Typer(help="Inspect and toggle WiFi.")


class TorchState(str, Enum):
    on = "on"
    off = "off"


@handle_errors
def torch(
    ctx: typer.Context,
    state: TorchState = typer.Argument(..., help="'on' or 'off'."),
) -> None:
    """Turn the camera flashlight on or off."""
    result = run_termux_api("termux-torch", args=[state.value])
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def volume(
    ctx: typer.Context,
    stream: str | None = typer.Argument(None, help="Audio stream, e.g. 'music', 'ring', 'alarm'."),
    level: int | None = typer.Argument(None, help="Volume level to set for the given stream."),
) -> None:
    """Show or set volume levels."""
    if stream is not None and level is None:
        typer.echo("Error: provide both stream and level, or neither.", err=True)
        raise typer.Exit(code=1)
    args = [] if stream is None else [stream, str(level)]
    result = run_termux_api("termux-volume", args=args)
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def brightness(
    ctx: typer.Context,
    level: str = typer.Argument(..., help="0-255, or 'auto'."),
) -> None:
    """Set screen brightness."""
    result = run_termux_api("termux-brightness", args=[level])
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def audio_info(ctx: typer.Context) -> None:
    """Show audio capabilities and device info."""
    result = run_termux_api("termux-audio-info")
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def wallpaper(
    ctx: typer.Context,
    file: str | None = typer.Option(None, "--file", help="Set wallpaper from a local file."),
    url: str | None = typer.Option(None, "--url", help="Set wallpaper from a URL."),
    lockscreen: bool = typer.Option(
        False, "--lockscreen", help="Apply to the lockscreen (Android 7+)."
    ),
) -> None:
    """Change the device wallpaper."""
    if (file is None) == (url is None):
        typer.echo("Error: provide exactly one of --file or --url.", err=True)
        raise typer.Exit(code=1)
    args = ["-f", file] if file is not None else ["-u", url]
    if lockscreen:
        args.append("-l")
    result = run_termux_api("termux-wallpaper", args=args)
    render(result, as_json=is_json_mode(ctx))


@wifi_app.command("info")
@handle_errors
def wifi_info(ctx: typer.Context) -> None:
    """Show current WiFi connection info."""
    result = run_termux_api("termux-wifi-connectioninfo")
    render(result, as_json=is_json_mode(ctx))


@wifi_app.command("enable")
@handle_errors
def wifi_enable(ctx: typer.Context) -> None:
    """Enable WiFi."""
    result = run_termux_api("termux-wifi-enable", args=["true"])
    render(result, as_json=is_json_mode(ctx))


@wifi_app.command("disable")
@handle_errors
def wifi_disable(ctx: typer.Context) -> None:
    """Disable WiFi."""
    result = run_termux_api("termux-wifi-enable", args=["false"])
    render(result, as_json=is_json_mode(ctx))


@wifi_app.command("scaninfo")
@handle_errors
def wifi_scaninfo(ctx: typer.Context) -> None:
    """Show results of the last WiFi scan."""
    result = run_termux_api("termux-wifi-scaninfo")
    render(result, as_json=is_json_mode(ctx))
