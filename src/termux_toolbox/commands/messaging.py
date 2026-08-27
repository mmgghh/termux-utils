import time
from enum import Enum

import typer

from termux_toolbox.core import scheduled_sms
from termux_toolbox.core.errors import TermuxToolboxError, handle_errors
from termux_toolbox.core.exec import run_termux_api
from termux_toolbox.core.output import is_json_mode, render

sms_app = typer.Typer(help="Read and send SMS messages.")
scheduled_app = typer.Typer(help="Manage SMS messages scheduled with 'mgt sms schedule'.")
sms_app.add_typer(scheduled_app, name="scheduled")
contacts_app = typer.Typer(help="Read device contacts.")

# Reserved termux-job-scheduler job ID for the recurring "send due scheduled SMS" job
# registered by 'mgt sms schedule'. Fixed so repeated registrations overwrite the same
# job instead of accumulating duplicates; picking your own --job-id with 'mgt job
# schedule' equal to this would silently overwrite it (an accepted, documented trade-off).
RUN_DUE_JOB_ID = "999001"
RUN_DUE_PERIOD_MS = "900000"

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


def _build_sms_send_args(number: str, message: str, slot: int | None) -> list[str]:
    args = ["-n", number]
    if slot is not None:
        args += ["-s", str(slot)]
    args.append(message)
    return args


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
    result = run_termux_api("termux-sms-send", args=_build_sms_send_args(number, message, slot))
    render(result, as_json=is_json_mode(ctx))


def _ensure_run_due_job_registered() -> None:
    script_path = scheduled_sms.state_dir() / "run-due.sh"
    if not script_path.exists():
        script_path.write_text(
            "#!/data/data/com.termux/files/usr/bin/sh\nmgt sms scheduled run-due\n"
        )
        script_path.chmod(0o755)
    try:
        run_termux_api(
            "termux-job-scheduler",
            args=[
                "--script", str(script_path),
                "--job-id", RUN_DUE_JOB_ID,
                "--period-ms", RUN_DUE_PERIOD_MS,
                "--persisted", "true",
            ],
        )
    except TermuxToolboxError as exc:
        typer.echo(
            f"Warning: could not schedule automatic delivery ({exc}). Run "
            "'mgt sms scheduled run-due' manually, or wire it into cron/Termux:Boot yourself.",
            err=True,
        )


@sms_app.command("schedule")
@handle_errors
def sms_schedule(
    ctx: typer.Context,
    number: str = typer.Argument(
        ..., help="Recipient phone number, or several separated by commas."
    ),
    message: str = typer.Argument(..., help="Message text to send later."),
    at: str | None = typer.Option(
        None, "--at", help="Absolute local time to send at, e.g. '2026-08-27 15:00'."
    ),
    in_: str | None = typer.Option(
        None, "--in", help="Relative delay before sending, e.g. '2h', '45m', '1h30m'."
    ),
    slot: int | None = typer.Option(
        None, "--slot", "-s", help="SIM slot to send from (requires READ_PHONE_STATE)."
    ),
) -> None:
    """Schedule an SMS to send at a future time (see 'mgt sms scheduled')."""
    now = time.time()
    try:
        send_at_epoch = scheduled_sms.resolve_target_epoch(at, in_, now)
    except ValueError as exc:
        typer.echo(f"Error: {exc}.", err=True)
        raise typer.Exit(code=1) from exc

    entry_id = scheduled_sms.add(number, message, send_at_epoch, slot=slot, now=now)
    _ensure_run_due_job_registered()
    render(
        {"id": entry_id, "number": number, "send_at_epoch": send_at_epoch, "status": "pending"},
        as_json=is_json_mode(ctx),
    )


@scheduled_app.command("list")
@handle_errors
def scheduled_list(ctx: typer.Context) -> None:
    """List pending and failed scheduled SMS sends."""
    render(scheduled_sms.list_entries(), as_json=is_json_mode(ctx))


@scheduled_app.command("cancel")
@handle_errors
def scheduled_cancel(
    ctx: typer.Context,
    entry_id: str = typer.Argument(
        ..., help="ID of the scheduled send to cancel (see 'mgt sms scheduled list')."
    ),
) -> None:
    """Cancel a pending or failed scheduled SMS send."""
    if not scheduled_sms.cancel(entry_id):
        typer.echo(f"Error: no scheduled send with id '{entry_id}'.", err=True)
        raise typer.Exit(code=1)
    render(f"Cancelled {entry_id}.", as_json=is_json_mode(ctx))


@scheduled_app.command("run-due")
@handle_errors
def scheduled_run_due(ctx: typer.Context) -> None:
    """Send every scheduled SMS that's due (invoked periodically by 'mgt sms schedule')."""
    results = []
    for entry in scheduled_sms.pop_due(time.time()):
        args = _build_sms_send_args(entry["number"], entry["message"], entry["slot"])
        try:
            run_termux_api("termux-sms-send", args=args)
            results.append({"id": entry["id"], "status": "sent"})
        except TermuxToolboxError as exc:
            updated = scheduled_sms.record_failure(entry, str(exc))
            results.append({"id": entry["id"], "status": updated["status"], "error": str(exc)})
    render(results, as_json=is_json_mode(ctx))


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
