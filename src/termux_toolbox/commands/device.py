import typer

from termux_toolbox.core.errors import handle_errors
from termux_toolbox.core.exec import run_termux_api
from termux_toolbox.core.output import is_json_mode, render

wifi_app = typer.Typer(help="Inspect and toggle WiFi.")


@handle_errors
def torch(
    ctx: typer.Context,
    state: str = typer.Argument(..., help="'on' or 'off'."),
) -> None:
    """Turn the camera flashlight on or off."""
    if state not in ("on", "off"):
        typer.echo("Error: state must be 'on' or 'off'", err=True)
        raise typer.Exit(code=1)
    result = run_termux_api("termux-torch", args=[state])
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
