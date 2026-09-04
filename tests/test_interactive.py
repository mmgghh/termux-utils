from enum import Enum

import pytest
import typer
from typer.main import get_command

from termux_toolbox import interactive


def _leaf(fn):
    """Build a minimal Typer app around fn and return its underlying click-like Command.

    A two-command app is used (plus a throwaway filler command) so Typer builds a
    proper Group instead of collapsing to a single top-level command, which would
    otherwise inject extra --install-completion/--show-completion params.
    """
    app = typer.Typer()
    app.command("cmd")(fn)
    app.command("_filler")(lambda: None)
    return get_command(app).commands["cmd"]


def test_required_argument_is_appended_positionally(monkeypatch):
    def fn(number: str = typer.Argument(...)):
        pass

    monkeypatch.setattr(interactive, "ask_text", lambda *a, **k: "5551234")

    assert interactive.build_argv(_leaf(fn)) == ["5551234"]


def test_option_with_default_is_prefilled_and_appended(monkeypatch):
    def fn(limit: int = typer.Option(10, "--limit", "-l")):
        pass

    seen = {}

    def fake_ask_text(message, default=None):
        seen["default"] = default
        return "20"

    monkeypatch.setattr(interactive, "ask_text", fake_ask_text)

    assert interactive.build_argv(_leaf(fn)) == ["--limit", "20"]
    assert seen["default"] == "10"


def test_plain_flag_included_when_confirmed(monkeypatch):
    def fn(conversations: bool = typer.Option(False, "--conversations", "-c")):
        pass

    monkeypatch.setattr(interactive, "ask_confirm", lambda *a, **k: True)

    assert interactive.build_argv(_leaf(fn)) == ["--conversations"]


def test_plain_flag_omitted_when_declined(monkeypatch):
    def fn(conversations: bool = typer.Option(False, "--conversations", "-c")):
        pass

    monkeypatch.setattr(interactive, "ask_confirm", lambda *a, **k: False)

    assert interactive.build_argv(_leaf(fn)) == []


@pytest.mark.parametrize(
    "selection, expected",
    [
        ("Yes", ["--charging"]),
        ("No", ["--no-charging"]),
        ("Leave unset", []),
    ],
)
def test_tristate_flag_pair(monkeypatch, selection, expected):
    def fn(charging: bool | None = typer.Option(None, "--charging/--no-charging")):
        pass

    monkeypatch.setattr(interactive, "ask_select", lambda *a, **k: selection)

    assert interactive.build_argv(_leaf(fn)) == expected


class MessageType(str, Enum):
    all = "all"
    inbox = "inbox"
    sent = "sent"


def test_choice_option_prompts_select_and_appends(monkeypatch):
    def fn(message_type: MessageType = typer.Option(MessageType.all, "--type", "-t")):
        pass

    seen = {}

    def fake_ask_select(message, choices=None, default=None):
        seen["choices"] = choices
        return "inbox"

    monkeypatch.setattr(interactive, "ask_select", fake_ask_select)

    assert interactive.build_argv(_leaf(fn)) == ["--type", "inbox"]
    assert seen["choices"] == ["all", "inbox", "sent"]


def test_optional_option_skipped_when_declined(monkeypatch):
    def fn(address: str | None = typer.Option(None, "--from", "-f")):
        pass

    monkeypatch.setattr(interactive, "ask_confirm", lambda *a, **k: False)
    monkeypatch.setattr(
        interactive, "ask_text", lambda *a, **k: pytest.fail("should not prompt for value")
    )

    assert interactive.build_argv(_leaf(fn)) == []


def test_optional_option_prompted_when_accepted(monkeypatch):
    def fn(address: str | None = typer.Option(None, "--from", "-f")):
        pass

    monkeypatch.setattr(interactive, "ask_confirm", lambda *a, **k: True)
    monkeypatch.setattr(interactive, "ask_text", lambda *a, **k: "5551234")

    assert interactive.build_argv(_leaf(fn)) == ["--from", "5551234"]


def test_variadic_argument_collects_until_blank(monkeypatch):
    def fn(sensor_names: list[str] = typer.Argument(...)):
        pass

    answers = iter(["Accelerometer", "Gyroscope", ""])
    monkeypatch.setattr(interactive, "ask_text", lambda *a, **k: next(answers))

    assert interactive.build_argv(_leaf(fn)) == ["Accelerometer", "Gyroscope"]


def test_multiple_option_collects_repeated_flag_value_pairs(monkeypatch):
    def fn(tag: list[str] = typer.Option(None, "--tag")):
        pass

    answers = iter(["a", "b", ""])
    monkeypatch.setattr(interactive, "ask_text", lambda *a, **k: next(answers))

    assert interactive.build_argv(_leaf(fn)) == ["--tag", "a", "--tag", "b"]


def _sample_app():
    app = typer.Typer()

    @app.callback()
    def main(ctx: typer.Context, json_output: bool = typer.Option(False, "--json")):
        ctx.obj = {"json": json_output}

    @app.command("battery")
    def battery(ctx: typer.Context):
        typer.echo("battery ok")

    @app.command("mode")
    def mode(ctx: typer.Context):
        typer.echo("json" if ctx.obj and ctx.obj.get("json") else "text")

    things_app = typer.Typer()

    @things_app.command("list")
    def things_list(ctx: typer.Context):
        typer.echo("listed things")

    app.add_typer(things_app, name="things")

    return app


def test_run_executes_selected_leaf_command_and_prints_output(monkeypatch, capsys):
    app = _sample_app()
    monkeypatch.setattr(interactive, "_is_interactive_terminal", lambda: True)
    monkeypatch.setattr(interactive, "ask_confirm", lambda *a, **k: False)
    monkeypatch.setattr(interactive, "ask_continue", lambda *a, **k: None)

    selections = iter(["battery", "Exit"])
    monkeypatch.setattr(interactive, "ask_select", lambda *a, **k: next(selections))

    interactive.run(app)

    assert "battery ok" in capsys.readouterr().out


def test_run_navigates_into_group_and_back(monkeypatch, capsys):
    app = _sample_app()
    monkeypatch.setattr(interactive, "_is_interactive_terminal", lambda: True)
    monkeypatch.setattr(interactive, "ask_confirm", lambda *a, **k: False)
    monkeypatch.setattr(interactive, "ask_continue", lambda *a, **k: None)

    selections = iter(["things", "list", "Back", "Exit"])
    monkeypatch.setattr(interactive, "ask_select", lambda *a, **k: next(selections))

    interactive.run(app)

    assert "listed things" in capsys.readouterr().out


def test_run_returns_to_menu_when_command_prompt_cancelled(monkeypatch, capsys):
    app = _sample_app()
    monkeypatch.setattr(interactive, "_is_interactive_terminal", lambda: True)
    monkeypatch.setattr(interactive, "ask_confirm", lambda *a, **k: False)

    def fake_build_argv(cmd):
        raise interactive.Cancelled

    monkeypatch.setattr(interactive, "build_argv", fake_build_argv)

    selections = iter(["battery", "Exit"])
    monkeypatch.setattr(interactive, "ask_select", lambda *a, **k: next(selections))

    interactive.run(app)

    assert "battery ok" not in capsys.readouterr().out


def test_run_prepends_json_flag_when_requested(monkeypatch, capsys):
    app = _sample_app()
    monkeypatch.setattr(interactive, "_is_interactive_terminal", lambda: True)
    monkeypatch.setattr(interactive, "ask_confirm", lambda *a, **k: True)
    monkeypatch.setattr(interactive, "ask_continue", lambda *a, **k: None)

    selections = iter(["mode", "Exit"])
    monkeypatch.setattr(interactive, "ask_select", lambda *a, **k: next(selections))

    interactive.run(app)

    assert "json" in capsys.readouterr().out


def test_run_pauses_for_a_keypress_after_running_a_command(monkeypatch, capsys):
    app = _sample_app()
    monkeypatch.setattr(interactive, "_is_interactive_terminal", lambda: True)
    monkeypatch.setattr(interactive, "ask_confirm", lambda *a, **k: False)

    pauses = []
    monkeypatch.setattr(interactive, "ask_continue", lambda *a, **k: pauses.append(True))

    selections = iter(["battery", "Exit"])
    monkeypatch.setattr(interactive, "ask_select", lambda *a, **k: next(selections))

    interactive.run(app)

    assert pauses == [True]


def test_run_does_not_pause_when_command_prompt_is_cancelled(monkeypatch):
    app = _sample_app()
    monkeypatch.setattr(interactive, "_is_interactive_terminal", lambda: True)
    monkeypatch.setattr(interactive, "ask_confirm", lambda *a, **k: False)

    def fake_build_argv(cmd):
        raise interactive.Cancelled

    monkeypatch.setattr(interactive, "build_argv", fake_build_argv)
    monkeypatch.setattr(
        interactive, "ask_continue", lambda *a, **k: pytest.fail("should not pause")
    )

    selections = iter(["battery", "Exit"])
    monkeypatch.setattr(interactive, "ask_select", lambda *a, **k: next(selections))

    interactive.run(app)


def test_run_requires_a_terminal(monkeypatch):
    app = _sample_app()
    monkeypatch.setattr(interactive, "_is_interactive_terminal", lambda: False)

    with pytest.raises(typer.Exit) as exc_info:
        interactive.run(app)

    assert exc_info.value.exit_code == 1
