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


usb_app = typer.Typer(help="List and access USB devices.")
nfc_app = typer.Typer(help="Read and write NDEF NFC tags.")

# Both wait on hardware or a permission dialog, so they need longer than the default.
USB_TIMEOUT = 120.0
NFC_TIMEOUT = 120.0


def _usb_target(device: str | None, vendor_id: str | None, product_id: str | None) -> list[str]:
    """Resolve a device path or a vendor/product ID pair into trailing arguments."""
    if device is not None:
        if vendor_id is not None or product_id is not None:
            typer.echo(
                "Error: give either a device path or --vendor-id with --product-id, not both.",
                err=True,
            )
            raise typer.Exit(code=1)
        return [device]
    if vendor_id is not None and product_id is not None:
        return [vendor_id, product_id]
    typer.echo(
        "Error: give a device path (see 'mgt usb list') or both --vendor-id and --product-id.",
        err=True,
    )
    raise typer.Exit(code=1)


@usb_app.command("list")
@handle_errors
def usb_list(ctx: typer.Context) -> None:
    """List available USB devices."""
    result = run_termux_api("termux-usb", args=["-l"])
    render(result, as_json=is_json_mode(ctx))


@usb_app.command("permission")
@handle_errors
def usb_permission(
    ctx: typer.Context,
    device: str | None = typer.Argument(None, help="Device path, as shown by 'mgt usb list'."),
    vendor_id: str | None = typer.Option(None, "--vendor-id", help="Device vendor ID."),
    product_id: str | None = typer.Option(None, "--product-id", help="Device product ID."),
    request: bool = typer.Option(
        False, "--request", "-r", help="Show the permission request dialog if needed."
    ),
) -> None:
    """Check (or request) permission to access a USB device."""
    target = _usb_target(device, vendor_id, product_id)
    args = ["-r"] if request else []
    args += target
    result = run_termux_api("termux-usb", args=args, timeout=USB_TIMEOUT)
    render(result, as_json=is_json_mode(ctx))


@usb_app.command("run")
@handle_errors
def usb_run(
    ctx: typer.Context,
    device: str | None = typer.Argument(None, help="Device path, as shown by 'mgt usb list'."),
    command: str = typer.Option(
        ..., "--command", "-e", help="Command to run with the device file descriptor."
    ),
    vendor_id: str | None = typer.Option(None, "--vendor-id", help="Device vendor ID."),
    product_id: str | None = typer.Option(None, "--product-id", help="Device product ID."),
    env_fd: bool = typer.Option(
        False,
        "--env-fd",
        "-E",
        help="Pass the descriptor as the TERMUX_USB_FD env var instead of an argument.",
    ),
    request: bool = typer.Option(
        False, "--request", "-r", help="Show the permission request dialog if needed."
    ),
) -> None:
    """Run a command with a file descriptor for a USB device."""
    target = _usb_target(device, vendor_id, product_id)
    args = ["-r"] if request else []
    args += ["-e", command]
    if env_fd:
        args.append("-E")
    args += target
    result = run_termux_api("termux-usb", args=args, timeout=USB_TIMEOUT)
    render(result, as_json=is_json_mode(ctx))


@nfc_app.command("read")
@handle_errors
def nfc_read(
    ctx: typer.Context,
    full: bool = typer.Option(False, "--full", help="Read full tag information instead of short."),
) -> None:
    """Read an NDEF tag; hold the tag against the device when prompted."""
    result = run_termux_api("termux-nfc", args=["-r", "full" if full else "short"], timeout=NFC_TIMEOUT)
    render(result, as_json=is_json_mode(ctx))


@nfc_app.command("write")
@handle_errors
def nfc_write(
    ctx: typer.Context,
    text: str = typer.Argument(..., help="Text to write to the tag."),
) -> None:
    """Write text to an NDEF tag; hold the tag against the device when prompted."""
    result = run_termux_api("termux-nfc", args=["-w", "-t", text], timeout=NFC_TIMEOUT)
    render(result, as_json=is_json_mode(ctx))
