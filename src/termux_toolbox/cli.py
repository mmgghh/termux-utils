import typer

from termux_toolbox.commands import feedback, messaging, sensors

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
app.add_typer(sensors.sensor_app, name="sensor")

app.command("call")(messaging.call)
app.add_typer(messaging.sms_app, name="sms")
app.add_typer(messaging.contacts_app, name="contacts")

app.command("notify")(feedback.notify)
app.command("toast")(feedback.toast)
app.command("vibrate")(feedback.vibrate)
app.command("speak")(feedback.speak)
app.add_typer(feedback.clipboard_app, name="clipboard")
