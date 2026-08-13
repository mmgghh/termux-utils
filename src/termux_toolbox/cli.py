import typer

from termux_toolbox.commands import sensors

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
