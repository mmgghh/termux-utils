from enum import Enum

import typer

from termux_toolbox.core.errors import handle_errors
from termux_toolbox.core.exec import run_termux_api
from termux_toolbox.core.output import is_json_mode, render

sms_app = typer.Typer(help="Read and send SMS messages.")
contacts_app = typer.Typer(help="Read device contacts.")

# termux-sms-list documents 'date DESC' as its conversation sort default, but only
# forwards --conversation-return-no-order-reverse when a sort order is also set, so
# send the default explicitly to make the flag take effect on its own.
DEFAULT_CONVERSATION_SORT_ORDER = "date DESC"


class MessageType(str, Enum):
    all = "all"
    inbox = "inbox"
    sent = "sent"
    draft = "draft"
    outbox = "outbox"
    failed = "failed"
    queued = "queued"


@sms_app.command("list")
@handle_errors
def sms_list(
    ctx: typer.Context,
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of messages to list."),
    offset: int = typer.Option(0, "--offset", "-o", help="Offset into the message list."),
    message_type: MessageType = typer.Option(
        MessageType.all, "--type", "-t", help="Type of messages to list."
    ),
    address: str | None = typer.Option(
        None, "--from", "-f", help="Only list messages for this address/phone number."
    ),
    selection: str | None = typer.Option(
        None, "--selection", help="SQL selection for messages, e.g. \"type == 1 and address == '666'\"."
    ),
    sort_order: str | None = typer.Option(
        None, "--sort-order", help="Message sort order, as in SQL 'ORDER BY' (default: 'date DESC')."
    ),
    no_order_reverse: bool = typer.Option(
        False,
        "--no-order-reverse",
        help="Print newest messages first instead of reversing the sort.",
    ),
    conversations: bool = typer.Option(
        False, "--conversations", "-c", help="List SMS conversations instead of messages."
    ),
    conversation_limit: int | None = typer.Option(
        None, "--conversation-limit", help="SQL limit for returned conversations."
    ),
    conversation_offset: int | None = typer.Option(
        None, "--conversation-offset", help="SQL offset for returned conversations."
    ),
    conversation_selection: str | None = typer.Option(
        None, "--conversation-selection", help="SQL selection for conversations, e.g. \"thread_id == 6\"."
    ),
    conversation_sort_order: str | None = typer.Option(
        None,
        "--conversation-sort-order",
        help="Conversation sort order, as in SQL 'ORDER BY' (default: 'date DESC').",
    ),
    conversation_multiple_messages: bool = typer.Option(
        False,
        "--conversation-multiple-messages",
        help="Return multiple messages per conversation instead of just one.",
    ),
    conversation_nested: bool = typer.Option(
        False,
        "--conversation-nested",
        help="Return conversations as nested objects keyed by conversation id.",
    ),
    conversation_no_order_reverse: bool = typer.Option(
        False,
        "--conversation-no-order-reverse",
        help="Print newest conversations first instead of reversing the sort.",
    ),
) -> None:
    """List SMS messages, or SMS conversations with --conversations."""
    conversation_options = {
        "--conversation-limit": conversation_limit is not None,
        "--conversation-offset": conversation_offset is not None,
        "--conversation-selection": conversation_selection is not None,
        "--conversation-sort-order": conversation_sort_order is not None,
        "--conversation-multiple-messages": conversation_multiple_messages,
        "--conversation-nested": conversation_nested,
        "--conversation-no-order-reverse": conversation_no_order_reverse,
    }
    if not conversations:
        used = [name for name, is_set in conversation_options.items() if is_set]
        if used:
            typer.echo(
                f"Error: {used[0]} only applies with --conversations.",
                err=True,
            )
            raise typer.Exit(code=1)

    args = ["-l", str(limit)]
    if offset:
        args += ["-o", str(offset)]
    if message_type is not MessageType.all:
        args += ["-t", message_type.value]
    if address is not None:
        args += ["-f", address]
    if selection is not None:
        args.append(f"--message-selection={selection}")
    if sort_order is not None:
        args.append(f"--message-sort-order={sort_order}")
    if no_order_reverse:
        args.append("--message-return-no-order-reverse")

    if conversations:
        args.append("-c")
        if conversation_limit is not None:
            args.append(f"--conversation-limit={conversation_limit}")
        if conversation_offset is not None:
            args.append(f"--conversation-offset={conversation_offset}")
        if conversation_selection is not None:
            args.append(f"--conversation-selection={conversation_selection}")
        if conversation_sort_order is None and conversation_no_order_reverse:
            conversation_sort_order = DEFAULT_CONVERSATION_SORT_ORDER
        if conversation_sort_order is not None:
            args.append(f"--conversation-sort-order={conversation_sort_order}")
        if conversation_multiple_messages:
            args.append("--conversation-return-multiple-messages")
        if conversation_nested:
            args.append("--conversation-return-nested-view")
        if conversation_no_order_reverse:
            args.append("--conversation-return-no-order-reverse")

    result = run_termux_api("termux-sms-list", args=args)
    render(result, as_json=is_json_mode(ctx))


@sms_app.command("send")
@handle_errors
def sms_send(
    ctx: typer.Context,
    number: str = typer.Argument(
        ..., help="Recipient phone number, or several separated by commas."
    ),
    message: str = typer.Argument(..., help="Message text to send."),
    slot: int | None = typer.Option(
        None, "--slot", "-s", help="SIM slot to send from (requires READ_PHONE_STATE)."
    ),
) -> None:
    """Send an SMS message."""
    args = ["-n", number]
    if slot is not None:
        args += ["-s", str(slot)]
    args.append(message)
    result = run_termux_api("termux-sms-send", args=args)
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
