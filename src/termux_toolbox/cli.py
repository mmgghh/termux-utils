import typer

from termux_toolbox.commands import (
    device,
    dialog,
    feedback,
    media,
    messaging,
    sensors,
    storage,
    system,
)

app = typer.Typer(help="A CLI toolbox exposing Termux:API device capabilities.")


@app.callback()
def main(
    ctx: typer.Context,
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit raw machine-readable output instead of formatted text.",
    ),
) -> None:
    ctx.obj = {"json": json_output}


app.command("battery")(sensors.battery)
app.command("location")(sensors.location)
app.command("fingerprint")(sensors.fingerprint)
app.add_typer(sensors.infrared_app, name="infrared")
app.add_typer(sensors.sensor_app, name="sensor")

app.command("call")(messaging.call)
app.command("call-log")(messaging.call_log)
app.add_typer(messaging.sms_app, name="sms")
app.add_typer(messaging.contacts_app, name="contacts")
app.add_typer(messaging.telephony_app, name="telephony")

app.command("notify")(feedback.notify)
app.command("toast")(feedback.toast)
app.command("vibrate")(feedback.vibrate)
app.command("speak")(feedback.speak)
app.command("tts-engines")(feedback.tts_engines)
app.command("speech-to-text")(feedback.speech_to_text)
app.command("download")(feedback.download)
app.command("share")(feedback.share)
app.add_typer(feedback.clipboard_app, name="clipboard")
app.add_typer(feedback.notification_app, name="notification")

app.add_typer(media.camera_app, name="camera")
app.add_typer(media.media_app, name="media")
app.add_typer(media.mic_app, name="mic")

app.command("torch")(device.torch)
app.command("volume")(device.volume)
app.command("brightness")(device.brightness)
app.command("audio-info")(device.audio_info)
app.command("wallpaper")(device.wallpaper)
app.add_typer(device.wifi_app, name="wifi")
app.add_typer(device.usb_app, name="usb")
app.add_typer(device.nfc_app, name="nfc")

app.command("storage-get")(storage.storage_get)
app.add_typer(storage.saf_app, name="saf")

app.add_typer(dialog.dialog_app, name="dialog")

app.add_typer(system.job_app, name="job")
app.add_typer(system.keystore_app, name="keystore")
app.add_typer(system.api_app, name="api")
