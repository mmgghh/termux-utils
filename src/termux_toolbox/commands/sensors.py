from enum import Enum

import typer

from termux_toolbox.core.errors import handle_errors
from termux_toolbox.core.exec import run_termux_api
from termux_toolbox.core.output import is_json_mode, render

sensor_app = typer.Typer(help="Read device sensors.")


class LocationProvider(str, Enum):
    gps = "gps"
    network = "network"
    passive = "passive"


class LocationRequest(str, Enum):
    once = "once"
    last = "last"
    updates = "updates"


@handle_errors
def battery(ctx: typer.Context) -> None:
    """Show battery status."""
    result = run_termux_api("termux-battery-status")
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def location(
    ctx: typer.Context,
    provider: LocationProvider = typer.Option(
        LocationProvider.gps, "--provider", help="gps, network, or passive."
    ),
    request: LocationRequest = typer.Option(
        LocationRequest.once,
        "--request",
        help="once (wait for a fix), last (last known), or updates (stream).",
    ),
) -> None:
    """Show current device location."""
    result = run_termux_api(
        "termux-location", args=["-p", provider.value, "-r", request.value], timeout=60.0
    )
    render(result, as_json=is_json_mode(ctx))


@sensor_app.command("list")
@handle_errors
def sensor_list(ctx: typer.Context) -> None:
    """List available sensors."""
    result = run_termux_api("termux-sensor", args=["-l"])
    render(result, as_json=is_json_mode(ctx))


@sensor_app.command("read")
@handle_errors
def sensor_read(
    ctx: typer.Context,
    sensor_names: list[str] = typer.Argument(
        ..., help="Sensor name(s), as shown by 'mgt sensor list'. Partial names match."
    ),
    delay_ms: int = typer.Option(1000, "--delay-ms", help="Delay between readings, in milliseconds."),
    limit: int = typer.Option(1, "--limit", help="Number of readings to take."),
) -> None:
    """Read values from specific sensor(s)."""
    args = ["-s", ",".join(sensor_names), "-d", str(delay_ms), "-n", str(limit)]
    timeout = max(15.0, (delay_ms * limit) / 1000 + 5)
    result = run_termux_api("termux-sensor", args=args, timeout=timeout)
    render(result, as_json=is_json_mode(ctx))


@sensor_app.command("all")
@handle_errors
def sensor_all(
    ctx: typer.Context,
    delay_ms: int = typer.Option(1000, "--delay-ms", help="Delay between readings, in milliseconds."),
    limit: int = typer.Option(1, "--limit", help="Number of readings to take."),
) -> None:
    """Read values from every sensor at once (may have a battery impact)."""
    args = ["-a", "-d", str(delay_ms), "-n", str(limit)]
    timeout = max(15.0, (delay_ms * limit) / 1000 + 5)
    result = run_termux_api("termux-sensor", args=args, timeout=timeout)
    render(result, as_json=is_json_mode(ctx))


@sensor_app.command("cleanup")
@handle_errors
def sensor_cleanup(ctx: typer.Context) -> None:
    """Release sensor resources held by a previous read."""
    result = run_termux_api("termux-sensor", args=["-c"])
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def fingerprint(
    ctx: typer.Context,
    title: str | None = typer.Option(None, "--title", help="Dialog title."),
    description: str | None = typer.Option(None, "--description", help="Dialog description."),
    subtitle: str | None = typer.Option(None, "--subtitle", help="Dialog subtitle."),
    cancel: str | None = typer.Option(None, "--cancel", help="Cancel button text."),
) -> None:
    """Authenticate using the device fingerprint sensor."""
    args = []
    if title is not None:
        args += ["-t", title]
    if description is not None:
        args += ["-d", description]
    if subtitle is not None:
        args += ["-s", subtitle]
    if cancel is not None:
        args += ["-c", cancel]
    result = run_termux_api("termux-fingerprint", args=args, timeout=30.0)
    render(result, as_json=is_json_mode(ctx))


infrared_app = typer.Typer(help="Use the device's infrared transmitter.")


@infrared_app.command("frequencies")
@handle_errors
def infrared_frequencies(ctx: typer.Context) -> None:
    """List the infrared transmitter's supported carrier frequencies."""
    result = run_termux_api("termux-infrared-frequencies")
    render(result, as_json=is_json_mode(ctx))


@infrared_app.command("transmit")
@handle_errors
def infrared_transmit(
    ctx: typer.Context,
    pattern: str = typer.Argument(
        ..., help="Comma-separated on/off intervals, e.g. '20,50,20,30'."
    ),
    frequency: int = typer.Option(..., "--frequency", "-f", help="IR carrier frequency in Hertz."),
) -> None:
    """Transmit an infrared pattern."""
    result = run_termux_api("termux-infrared-transmit", args=["-f", str(frequency), pattern])
    render(result, as_json=is_json_mode(ctx))
