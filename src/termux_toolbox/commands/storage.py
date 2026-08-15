import typer

from termux_toolbox.core.errors import handle_errors
from termux_toolbox.core.exec import run_termux_api
from termux_toolbox.core.output import is_json_mode, render

saf_app = typer.Typer(help="Access files and folders via the Storage Access Framework.")


@handle_errors
def storage_get(
    ctx: typer.Context,
    output_path: str = typer.Argument(..., help="Path to save the picked file to."),
) -> None:
    """Request a file from the system file picker and save it locally."""
    result = run_termux_api("termux-storage-get", args=[output_path], timeout=120.0)
    render(result, as_json=is_json_mode(ctx))


@saf_app.command("dirs")
@handle_errors
def saf_dirs(ctx: typer.Context) -> None:
    """List directories Termux:API has been given access to."""
    result = run_termux_api("termux-saf-dirs")
    render(result, as_json=is_json_mode(ctx))


@saf_app.command("managedir")
@handle_errors
def saf_managedir(ctx: typer.Context) -> None:
    """Open the system folder picker to grant Termux:API access to a folder."""
    result = run_termux_api("termux-saf-managedir", timeout=120.0)
    render(result, as_json=is_json_mode(ctx))


@saf_app.command("ls")
@handle_errors
def saf_ls(
    ctx: typer.Context,
    folder_uri: str = typer.Argument(..., help="URI of the folder to list."),
) -> None:
    """List the files and folders inside a SAF folder URI."""
    result = run_termux_api("termux-saf-ls", args=[folder_uri])
    render(result, as_json=is_json_mode(ctx))


@saf_app.command("create")
@handle_errors
def saf_create(
    ctx: typer.Context,
    folder_uri: str = typer.Argument(..., help="URI of the folder to create the file in."),
    name: str = typer.Argument(..., help="Name of the file to create."),
    mime_type: str | None = typer.Option(
        None, "--mime-type", "-t", help="MIME type (default: application/octet-stream)."
    ),
) -> None:
    """Create a file in a SAF-managed folder and print its URI."""
    args = []
    if mime_type is not None:
        args += ["-t", mime_type]
    args += [folder_uri, name]
    result = run_termux_api("termux-saf-create", args=args)
    render(result, as_json=is_json_mode(ctx))


@saf_app.command("mkdir")
@handle_errors
def saf_mkdir(
    ctx: typer.Context,
    parent_uri: str = typer.Argument(..., help="URI of the parent folder."),
    name: str = typer.Argument(..., help="Name of the folder to create."),
) -> None:
    """Create a directory in a SAF-managed folder and print its URI."""
    result = run_termux_api("termux-saf-mkdir", args=[parent_uri, name])
    render(result, as_json=is_json_mode(ctx))


@saf_app.command("stat")
@handle_errors
def saf_stat(
    ctx: typer.Context,
    uri: str = typer.Argument(..., help="URI of the file or folder."),
) -> None:
    """Show info about a file or folder identified by a SAF URI."""
    result = run_termux_api("termux-saf-stat", args=[uri])
    render(result, as_json=is_json_mode(ctx))
