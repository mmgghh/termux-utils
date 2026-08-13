import json

import typer


def is_json_mode(ctx: typer.Context) -> bool:
    return bool(ctx.obj and ctx.obj.get("json"))


def render(data: dict | list | str, as_json: bool) -> None:
    if as_json:
        if isinstance(data, str):
            typer.echo(data)
        else:
            typer.echo(json.dumps(data))
        return

    if isinstance(data, str):
        typer.echo(data if data.strip() else "(no output)")
    elif isinstance(data, dict):
        for key, value in data.items():
            typer.echo(f"{key}: {value}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                typer.echo(", ".join(f"{k}={v}" for k, v in item.items()))
            else:
                typer.echo(str(item))
