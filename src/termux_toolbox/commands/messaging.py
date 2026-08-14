import typer

from termux_toolbox.core.errors import handle_errors
from termux_toolbox.core.exec import run_termux_api
from termux_toolbox.core.output import is_json_mode, render

sms_app = typer.Typer(help="Read and send SMS messages.")
contacts_app = typer.Typer(help="Read device contacts.")


@sms_app.command("list")
@handle_errors
def sms_list(
    ctx: typer.Context,
    limit: int = typer.Option(10, "--limit", help="Maximum number of messages to list."),
) -> None:
    """List SMS messages."""
    result = run_termux_api("termux-sms-list", args=["-l", str(limit)])
    render(result, as_json=is_json_mode(ctx))


@sms_app.command("send")
@handle_errors
def sms_send(
    ctx: typer.Context,
    number: str = typer.Argument(..., help="Recipient phone number."),
    message: str = typer.Argument(..., help="Message text to send."),
) -> None:
    """Send an SMS message."""
    result = run_termux_api("termux-sms-send", args=["-n", number, message])
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def call(
    ctx: typer.Context,
    number: str = typer.Argument(..., help="Phone number to call."),
) -> None:
    """Place a phone call."""
    result = run_termux_api("termux-telephony-call", args=[number])
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def call_log(
    ctx: typer.Context,
    limit: int = typer.Option(10, "--limit", help="Maximum number of call log entries to list."),
    offset: int = typer.Option(0, "--offset", help="Offset into the call log."),
) -> None:
    """List call log history."""
    result = run_termux_api("termux-call-log", args=["-l", str(limit), "-o", str(offset)])
    render(result, as_json=is_json_mode(ctx))


@contacts_app.command("list")
@handle_errors
def contacts_list(ctx: typer.Context) -> None:
    """List device contacts."""
    result = run_termux_api("termux-contact-list")
    render(result, as_json=is_json_mode(ctx))


telephony_app = typer.Typer(help="Query telephony/cellular information.")


@telephony_app.command("cellinfo")
@handle_errors
def telephony_cellinfo(ctx: typer.Context) -> None:
    """Show observed cell tower information."""
    result = run_termux_api("termux-telephony-cellinfo")
    render(result, as_json=is_json_mode(ctx))


@telephony_app.command("deviceinfo")
@handle_errors
def telephony_deviceinfo(ctx: typer.Context) -> None:
    """Show telephony device information."""
    result = run_termux_api("termux-telephony-deviceinfo")
    render(result, as_json=is_json_mode(ctx))
