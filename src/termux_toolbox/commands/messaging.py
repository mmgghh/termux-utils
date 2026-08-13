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


@contacts_app.command("list")
@handle_errors
def contacts_list(ctx: typer.Context) -> None:
    """List device contacts."""
    result = run_termux_api("termux-contact-list")
    render(result, as_json=is_json_mode(ctx))
