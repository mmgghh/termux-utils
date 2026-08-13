import json

import typer


def is_json_mode(ctx: typer.Context) -> bool:
    return bool(ctx.obj and ctx.obj.get("json"))


def render(data: dict | list | str, as_json: bool) -> None:
    if as_json:
        typer.echo(json.dumps(data))
        return

    if isinstance(data, str):
        typer.echo(data if data.strip() else "(no output)")
    elif isinstance(data, dict):
        if not data:
            typer.echo("(no output)")
        else:
            for key, value in data.items():
                typer.echo(f"{key}: {value}")
    elif isinstance(data, list):
        if not data:
            typer.echo("(no output)")
        else:
            for item in data:
                if isinstance(item, dict):
                    typer.echo(", ".join(f"{k}={v}" for k, v in item.items()))
                else:
                    typer.echo(str(item))
