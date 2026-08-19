from enum import Enum

import typer

from termux_toolbox.core.errors import handle_errors
from termux_toolbox.core.exec import run_termux_api
from termux_toolbox.core.output import is_json_mode, render

clipboard_app = typer.Typer(help="Read and write the system clipboard.")


@clipboard_app.command("get")
@handle_errors
def clipboard_get(ctx: typer.Context) -> None:
    """Print the current clipboard contents."""
    result = run_termux_api("termux-clipboard-get")
    render(result, as_json=is_json_mode(ctx))


@clipboard_app.command("set")
@handle_errors
def clipboard_set(
    ctx: typer.Context,
    text: str = typer.Argument(..., help="Text to copy to the clipboard."),
) -> None:
    """Set the clipboard contents."""
    result = run_termux_api("termux-clipboard-set", args=[text])
    render(result, as_json=is_json_mode(ctx))


class NotificationPriority(str, Enum):
    max = "max"
    high = "high"
    default = "default"
    low = "low"
    min = "min"


class NotificationType(str, Enum):
    default = "default"
    media = "media"


@handle_errors
def notify(
    ctx: typer.Context,
    title: str | None = typer.Argument(None, help="Notification title."),
    content: str | None = typer.Argument(
        None, help="Notification body text. Read from stdin if omitted."
    ),
    notification_id: str | None = typer.Option(
        None, "--id", "-i", help="Notification ID; reusing one replaces that notification."
    ),
    channel: str | None = typer.Option(
        None, "--channel", help="Channel ID to post on (see 'mgt notification channel create')."
    ),
    group: str | None = typer.Option(
        None, "--group", help="Group name; notifications in a group are shown together."
    ),
    priority: NotificationPriority | None = typer.Option(
        None, "--priority", help="Notification priority."
    ),
    icon: str | None = typer.Option(
        None, "--icon", help="Status bar icon name (default: event_note)."
    ),
    image_path: str | None = typer.Option(
        None, "--image-path", help="Absolute path to an image to show in the notification."
    ),
    led_color: str | None = typer.Option(
        None, "--led-color", help="Blinking LED color as RRGGBB."
    ),
    led_on: int | None = typer.Option(
        None, "--led-on", help="Milliseconds the LED stays on while flashing."
    ),
    led_off: int | None = typer.Option(
        None, "--led-off", help="Milliseconds the LED stays off while flashing."
    ),
    vibrate: str | None = typer.Option(
        None, "--vibrate", help="Vibrate pattern in milliseconds, e.g. '500,1000,200'."
    ),
    sound: bool = typer.Option(False, "--sound", help="Play a sound with the notification."),
    ongoing: bool = typer.Option(
        False, "--ongoing", help="Pin the notification (requires --id to stay removable)."
    ),
    alert_once: bool = typer.Option(
        False, "--alert-once", help="Do not alert again when the notification is edited."
    ),
    action: str | None = typer.Option(
        None, "--action", help="Shell action to run when the notification is pressed."
    ),
    on_delete: str | None = typer.Option(
        None, "--on-delete", help="Shell action to run when the notification is cleared."
    ),
    button1: str | None = typer.Option(None, "--button1", help="Text for the first button."),
    button1_action: str | None = typer.Option(
        None, "--button1-action", help="Shell action for the first button."
    ),
    button2: str | None = typer.Option(None, "--button2", help="Text for the second button."),
    button2_action: str | None = typer.Option(
        None, "--button2-action", help="Shell action for the second button."
    ),
    button3: str | None = typer.Option(None, "--button3", help="Text for the third button."),
    button3_action: str | None = typer.Option(
        None, "--button3-action", help="Shell action for the third button."
    ),
    notification_type: NotificationType | None = typer.Option(
        None, "--type", help="Notification style: default or media."
    ),
    media_play: str | None = typer.Option(
        None, "--media-play", help="Shell action for the media-play button (--type media)."
    ),
    media_pause: str | None = typer.Option(
        None, "--media-pause", help="Shell action for the media-pause button (--type media)."
    ),
    media_next: str | None = typer.Option(
        None, "--media-next", help="Shell action for the media-next button (--type media)."
    ),
    media_previous: str | None = typer.Option(
        None, "--media-previous", help="Shell action for the media-previous button (--type media)."
    ),
) -> None:
    """Show an Android notification."""
    if ongoing and notification_id is None:
        typer.echo(
            "Error: --ongoing needs --id, otherwise the notification can't be removed.",
            err=True,
        )
        raise typer.Exit(code=1)

    args = []
    if title is not None:
        args += ["-t", title]
    if content is not None:
        args += ["-c", content]
    for flag, value in (
        ("--id", notification_id),
        ("--channel", channel),
        ("--group", group),
        ("--priority", priority),
        ("--icon", icon),
        ("--image-path", image_path),
        ("--led-color", led_color),
        ("--led-on", led_on),
        ("--led-off", led_off),
        ("--vibrate", vibrate),
        ("--action", action),
        ("--on-delete", on_delete),
        ("--button1", button1),
        ("--button1-action", button1_action),
        ("--button2", button2),
        ("--button2-action", button2_action),
        ("--button3", button3),
        ("--button3-action", button3_action),
        ("--type", notification_type),
        ("--media-play", media_play),
        ("--media-pause", media_pause),
        ("--media-next", media_next),
        ("--media-previous", media_previous),
    ):
        if value is not None:
            args += [flag, value.value if isinstance(value, Enum) else str(value)]
    if sound:
        args.append("--sound")
    if ongoing:
        args.append("--ongoing")
    if alert_once:
        args.append("--alert-once")

    result = run_termux_api("termux-notification", args=args)
    render(result, as_json=is_json_mode(ctx))


class ToastGravity(str, Enum):
    top = "top"
    middle = "middle"
    bottom = "bottom"


@handle_errors
def toast(
    ctx: typer.Context,
    text: str = typer.Argument(..., help="Text to show in the toast popup."),
    short: bool = typer.Option(False, "--short", "-s", help="Show the toast only briefly."),
    background: str | None = typer.Option(
        None,
        "--background",
        "-b",
        help="Background color: a name like 'red' or (AA)RRGGBB hex (default: gray).",
    ),
    text_color: str | None = typer.Option(
        None,
        "--text-color",
        "-c",
        help="Text color: a name like 'red' or (AA)RRGGBB hex (default: white).",
    ),
    gravity: ToastGravity | None = typer.Option(
        None, "--gravity", "-g", help="Toast position (default: middle)."
    ),
) -> None:
    """Show a short-lived toast popup."""
    args = []
    if short:
        args.append("-s")
    if background is not None:
        args += ["-b", background]
    if text_color is not None:
        args += ["-c", text_color]
    if gravity is not None:
        args += ["-g", gravity.value]
    args.append(text)
    result = run_termux_api("termux-toast", args=args)
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def vibrate(
    ctx: typer.Context,
    duration_ms: int = typer.Option(1000, "--duration-ms", help="Vibration duration in milliseconds."),
    force: bool = typer.Option(
        False, "--force", "-f", help="Vibrate even when the device is in silent mode."
    ),
) -> None:
    """Vibrate the device."""
    args = ["-d", str(duration_ms)]
    if force:
        args.append("-f")
    result = run_termux_api("termux-vibrate", args=args)
    render(result, as_json=is_json_mode(ctx))


class TtsStream(str, Enum):
    ALARM = "ALARM"
    MUSIC = "MUSIC"
    NOTIFICATION = "NOTIFICATION"
    RING = "RING"
    SYSTEM = "SYSTEM"
    VOICE_CALL = "VOICE_CALL"


@handle_errors
def speak(
    ctx: typer.Context,
    text: str = typer.Argument(..., help="Text to speak aloud."),
    engine: str | None = typer.Option(
        None, "--engine", "-e", help="TTS engine to use (see 'mgt tts-engines')."
    ),
    language: str | None = typer.Option(None, "--language", "-l", help="Language to speak in."),
    region: str | None = typer.Option(None, "--region", "-n", help="Region of the language."),
    variant: str | None = typer.Option(None, "--variant", "-v", help="Variant of the language."),
    pitch: float | None = typer.Option(
        None, "--pitch", "-p", help="Speech pitch; 1.0 is normal, lower is deeper."
    ),
    rate: float | None = typer.Option(
        None, "--rate", "-r", help="Speech rate; 1.0 is normal, 2.0 is twice as fast."
    ),
    stream: TtsStream | None = typer.Option(
        None, "--stream", "-s", help="Audio stream to play on (default: NOTIFICATION)."
    ),
) -> None:
    """Speak text aloud via text-to-speech."""
    args = []
    if engine is not None:
        args += ["-e", engine]
    if language is not None:
        args += ["-l", language]
    if region is not None:
        args += ["-n", region]
    if variant is not None:
        args += ["-v", variant]
    if pitch is not None:
        args += ["-p", str(pitch)]
    if rate is not None:
        args += ["-r", str(rate)]
    if stream is not None:
        args += ["-s", stream.value]
    args.append(text)
    result = run_termux_api("termux-tts-speak", args=args)
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def tts_engines(ctx: typer.Context) -> None:
    """List available text-to-speech engines."""
    result = run_termux_api("termux-tts-engines")
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def speech_to_text(
    ctx: typer.Context,
    progress: bool = typer.Option(
        False, "--progress", "-p", help="Show partial results as they arrive."
    ),
) -> None:
    """Convert speech to text using the device microphone."""
    args = ["-p"] if progress else []
    result = run_termux_api("termux-speech-to-text", args=args, timeout=60.0)
    render(result, as_json=is_json_mode(ctx))


@handle_errors
def download(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="URL to download."),
    description: str | None = typer.Option(None, "--description", help="Notification description."),
    title: str | None = typer.Option(None, "--title", help="Notification title."),
    path: str | None = typer.Option(None, "--path", help="Full path to save the downloaded file to."),
) -> None:
    """Download a URL using the system download manager."""
    args = []
    if description is not None:
        args += ["-d", description]
    if title is not None:
        args += ["-t", title]
    if path is not None:
        args += ["-p", path]
    args.append(url)
    result = run_termux_api("termux-download", args=args)
    render(result, as_json=is_json_mode(ctx))


class ShareAction(str, Enum):
    view = "view"
    send = "send"
    edit = "edit"


@handle_errors
def share(
    ctx: typer.Context,
    file: str | None = typer.Argument(None, help="File to share. Omit to share stdin text instead."),
    action: ShareAction = typer.Option(ShareAction.view, "--action", "-a", help="view, send, or edit."),
    content_type: str | None = typer.Option(
        None, "--content-type", "-c", help="MIME type (guessed if omitted)."
    ),
    default_receiver: bool = typer.Option(
        False,
        "--default-receiver",
        "-d",
        help="Share to the default receiver instead of showing a chooser.",
    ),
    title: str | None = typer.Option(None, "--title", "-t", help="Title for the shared content."),
) -> None:
    """Share a file, or stdin text if no file is given."""
    args = ["-a", action.value]
    if content_type is not None:
        args += ["-c", content_type]
    if default_receiver:
        args.append("-d")
    if title is not None:
        args += ["-t", title]
    if file is not None:
        args.append(file)
    result = run_termux_api("termux-share", args=args)
    render(result, as_json=is_json_mode(ctx))


notification_app = typer.Typer(help="Manage notifications posted via 'mgt notify'.")
notification_channel_app = typer.Typer(help="Create or delete notification channels.")
notification_app.add_typer(notification_channel_app, name="channel")


@notification_app.command("list")
@handle_errors
def notification_list(ctx: typer.Context) -> None:
    """List currently shown notifications."""
    result = run_termux_api("termux-notification-list")
    render(result, as_json=is_json_mode(ctx))


@notification_app.command("remove")
@handle_errors
def notification_remove(
    ctx: typer.Context,
    notification_id: str = typer.Argument(..., help="ID of the notification to remove."),
) -> None:
    """Remove a previously shown notification by ID (see 'mgt notification list')."""
    result = run_termux_api("termux-notification-remove", args=[notification_id])
    render(result, as_json=is_json_mode(ctx))


@notification_channel_app.command("create")
@handle_errors
def notification_channel_create(
    ctx: typer.Context,
    channel_id: str = typer.Argument(..., help="Channel ID."),
    channel_name: str = typer.Argument(..., help="Channel display name."),
) -> None:
    """Create a notification channel, or rename an existing one."""
    result = run_termux_api("termux-notification-channel", args=[channel_id, channel_name])
    render(result, as_json=is_json_mode(ctx))


@notification_channel_app.command("delete")
@handle_errors
def notification_channel_delete(
    ctx: typer.Context,
    channel_id: str = typer.Argument(..., help="ID of the channel to delete."),
) -> None:
    """Delete a notification channel."""
    result = run_termux_api("termux-notification-channel", args=["-d", channel_id])
    render(result, as_json=is_json_mode(ctx))
