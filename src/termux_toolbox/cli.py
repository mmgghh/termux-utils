import typer

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
