import sys
from enum import Enum

import typer

from termux_toolbox.core.errors import handle_errors
from termux_toolbox.core.exec import run_termux_api, run_termux_api_bytes
from termux_toolbox.core.output import is_json_mode, render

job_app = typer.Typer(help="Schedule scripts to run in the background.")
keystore_app = typer.Typer(help="Manage keys in the hardware-backed Android keystore.")
api_app = typer.Typer(help="Control the Termux:API background service.")


class JobNetwork(str, Enum):
    any = "any"
    unmetered = "unmetered"
    cellular = "cellular"
    not_roaming = "not_roaming"
    none = "none"


class KeyAlgorithm(str, Enum):
    RSA = "RSA"
    EC = "EC"


@job_app.command("list")
@handle_errors
def job_list(ctx: typer.Context) -> None:
    """List pending jobs."""
    result = run_termux_api("termux-job-scheduler", args=["--pending"])
    render(result, as_json=is_json_mode(ctx))


@job_app.command("schedule")
@handle_errors
def job_schedule(
    ctx: typer.Context,
    script: str = typer.Argument(..., help="Path to the script to run."),
    job_id: int | None = typer.Option(
        None, "--job-id", help="Job ID; reusing one overwrites that job."
    ),
    period_ms: int | None = typer.Option(
        None,
        "--period-ms",
        help="Run about every N milliseconds (omit to run once; Android's minimum is 900000).",
    ),
    network: JobNetwork | None = typer.Option(
        None, "--network", help="Only run on this kind of network connection."
    ),
    battery_not_low: bool | None = typer.Option(
        None, "--battery-not-low/--no-battery-not-low", help="Only run when the battery isn't low."
    ),
    storage_not_low: bool | None = typer.Option(
        None, "--storage-not-low/--no-storage-not-low", help="Only run when storage isn't low."
    ),
    charging: bool | None = typer.Option(
        None, "--charging/--no-charging", help="Only run while charging."
    ),
    persisted: bool | None = typer.Option(
        None, "--persisted/--no-persisted", help="Keep the job across reboots."
    ),
    trigger_content_uri: str | None = typer.Option(
        None, "--trigger-content-uri", help="Run when this content URI changes (Android 7+)."
    ),
    trigger_content_flag: int | None = typer.Option(
        None, "--trigger-content-flag", help="Content trigger flag (default 1, Android 7+)."
    ),
) -> None:
    """Schedule a script to run in the background."""
    args = ["--script", script]
    if job_id is not None:
        args += ["--job-id", str(job_id)]
    if period_ms is not None:
        args += ["--period-ms", str(period_ms)]
    if network is not None:
        args += ["--network", network.value]
    for flag, value in (
        ("--battery-not-low", battery_not_low),
        ("--storage-not-low", storage_not_low),
        ("--charging", charging),
        ("--persisted", persisted),
    ):
        if value is not None:
            args += [flag, "true" if value else "false"]
    if trigger_content_uri is not None:
        args += ["--trigger-content-uri", trigger_content_uri]
    if trigger_content_flag is not None:
        args += ["--trigger-content-flag", str(trigger_content_flag)]
    result = run_termux_api("termux-job-scheduler", args=args)
    render(result, as_json=is_json_mode(ctx))


@job_app.command("cancel")
@handle_errors
def job_cancel(
    ctx: typer.Context,
    job_id: int = typer.Argument(..., help="ID of the job to cancel (see 'mgt job list')."),
) -> None:
    """Cancel a pending job."""
    result = run_termux_api("termux-job-scheduler", args=["--cancel", "--job-id", str(job_id)])
    render(result, as_json=is_json_mode(ctx))


@job_app.command("cancel-all")
@handle_errors
def job_cancel_all(ctx: typer.Context) -> None:
    """Cancel every pending job."""
    result = run_termux_api("termux-job-scheduler", args=["--cancel-all"])
    render(result, as_json=is_json_mode(ctx))


@keystore_app.command("list")
@handle_errors
def keystore_list(
    ctx: typer.Context,
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Include key parameters."),
) -> None:
    """List the keys stored in the keystore."""
    args = ["list", "-d"] if detailed else ["list"]
    result = run_termux_api("termux-keystore", args=args)
    render(result, as_json=is_json_mode(ctx))


@keystore_app.command("generate")
@handle_errors
def keystore_generate(
    ctx: typer.Context,
    alias: str = typer.Argument(..., help="Alias to store the new key under."),
    algorithm: KeyAlgorithm = typer.Option(
        KeyAlgorithm.RSA, "--algorithm", "-a", help="Key algorithm."
    ),
    size: int | None = typer.Option(
        None, "--size", "-s", help="Key size: 2048/3072/4096 for RSA, 256/384/521 for EC."
    ),
    validity: int | None = typer.Option(
        None,
        "--validity",
        "-u",
        help="Seconds the key stays usable after an unlock (omit to disable).",
    ),
) -> None:
    """Create a new key inside the hardware keystore."""
    args = ["generate", alias, "-a", algorithm.value]
    if size is not None:
        args += ["-s", str(size)]
    if validity is not None:
        args += ["-u", str(validity)]
    result = run_termux_api("termux-keystore", args=args)
    render(result, as_json=is_json_mode(ctx))


@keystore_app.command("delete")
@handle_errors
def keystore_delete(
    ctx: typer.Context,
    alias: str = typer.Argument(..., help="Alias of the key to delete."),
) -> None:
    """Permanently delete a key from the keystore."""
    result = run_termux_api("termux-keystore", args=["delete", alias])
    render(result, as_json=is_json_mode(ctx))


@keystore_app.command("sign")
@handle_errors
def keystore_sign(
    ctx: typer.Context,
    alias: str = typer.Argument(..., help="Alias of the key to sign with."),
    algorithm: str = typer.Argument(..., help="Signing algorithm, e.g. 'SHA256withRSA'."),
) -> None:
    """Sign data read from stdin, writing the raw signature to stdout."""
    data = sys.stdin.buffer.read()
    signature = run_termux_api_bytes(
        "termux-keystore", args=["sign", alias, algorithm], input_bytes=data, timeout=60.0
    )
    sys.stdout.buffer.write(signature)


@keystore_app.command("verify")
@handle_errors
def keystore_verify(
    ctx: typer.Context,
    alias: str = typer.Argument(..., help="Alias of the key the data was signed with."),
    algorithm: str = typer.Argument(..., help="Algorithm used to sign, e.g. 'SHA256withRSA'."),
    signature_file: str = typer.Argument(..., help="File holding the signature to verify."),
) -> None:
    """Verify a signature against data read from stdin."""
    data = sys.stdin.buffer.read()
    output = run_termux_api_bytes(
        "termux-keystore",
        args=["verify", alias, algorithm, signature_file],
        input_bytes=data,
        timeout=60.0,
    )
    render(output.decode(errors="replace").strip(), as_json=is_json_mode(ctx))


@api_app.command("start")
@handle_errors
def api_start(ctx: typer.Context) -> None:
    """Start the Termux:API keep-alive service."""
    result = run_termux_api("termux-api-start")
    render(result, as_json=is_json_mode(ctx))


@api_app.command("stop")
@handle_errors
def api_stop(ctx: typer.Context) -> None:
    """Stop the Termux:API keep-alive service."""
    result = run_termux_api("termux-api-stop")
    render(result, as_json=is_json_mode(ctx))
