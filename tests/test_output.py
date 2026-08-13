from types import SimpleNamespace

from termux_toolbox.core.output import is_json_mode, render


def test_is_json_mode_true_when_flag_set():
    ctx = SimpleNamespace(obj={"json": True})
    assert is_json_mode(ctx) is True


def test_is_json_mode_false_when_flag_unset():
    ctx = SimpleNamespace(obj={"json": False})
    assert is_json_mode(ctx) is False


def test_is_json_mode_false_when_obj_is_none():
    ctx = SimpleNamespace(obj=None)
    assert is_json_mode(ctx) is False


def test_render_json_dict(capsys):
    render({"percentage": 87}, as_json=True)
    captured = capsys.readouterr()
    assert captured.out.strip() == '{"percentage": 87}'


def test_render_json_string_passthrough(capsys):
    render("raw text", as_json=True)
    captured = capsys.readouterr()
    assert captured.out.strip() == "raw text"


def test_render_text_dict(capsys):
    render({"percentage": 87, "status": "CHARGING"}, as_json=False)
    captured = capsys.readouterr()
    assert captured.out == "percentage: 87\nstatus: CHARGING\n"


def test_render_text_list_of_dicts(capsys):
    render([{"number": "555", "name": "Bob"}], as_json=False)
    captured = capsys.readouterr()
    assert captured.out == "number=555, name=Bob\n"


def test_render_text_list_of_scalars(capsys):
    render(["Accelerometer", "Gyroscope"], as_json=False)
    captured = capsys.readouterr()
    assert captured.out == "Accelerometer\nGyroscope\n"


def test_render_empty_string(capsys):
    render("", as_json=False)
    captured = capsys.readouterr()
    assert captured.out == "(no output)\n"


def test_render_nonempty_string(capsys):
    render("hello from clipboard", as_json=False)
    captured = capsys.readouterr()
    assert captured.out == "hello from clipboard\n"
