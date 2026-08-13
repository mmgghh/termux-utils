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
) -> None:
    """Show current device location."""
    result = run_termux_api(
        "termux-location", args=["-p", provider.value, "-r", "once"], timeout=60.0
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
    sensor_name: str = typer.Argument(..., help="Exact sensor name, as shown by 'mgt sensor list'."),
    delay_ms: int = typer.Option(1000, "--delay-ms", help="Delay between readings, in milliseconds."),
    limit: int = typer.Option(1, "--limit", help="Number of readings to take."),
) -> None:
    """Read values from a specific sensor."""
    args = ["-s", sensor_name, "-d", str(delay_ms), "-n", str(limit)]
    timeout = max(15.0, (delay_ms * limit) / 1000 + 5)
    result = run_termux_api("termux-sensor", args=args, timeout=timeout)
    render(result, as_json=is_json_mode(ctx))
