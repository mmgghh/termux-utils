from unittest.mock import patch

from typer.testing import CliRunner

from termux_toolbox.cli import app

runner = CliRunner()


def test_sms_list_default_limit():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=[]) as mock_run:
        runner.invoke(app, ["sms", "list"])
    mock_run.assert_called_once_with("termux-sms-list", args=["-l", "10"])


def test_sms_list_custom_limit():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=[]) as mock_run:
        runner.invoke(app, ["sms", "list", "--limit", "5"])
    mock_run.assert_called_once_with("termux-sms-list", args=["-l", "5"])


def test_sms_send():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["sms", "send", "5551234", "hello there"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-sms-send", args=["-n", "5551234", "hello there"])


def test_call():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["call", "5551234"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-telephony-call", args=["5551234"])


def test_contacts_list():
    fake = [{"name": "Bob", "number": "555"}]
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=fake):
        result = runner.invoke(app, ["contacts", "list"])
    assert result.exit_code == 0
    assert "name=Bob" in result.output


def test_call_log_defaults():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=[]) as mock_run:
        runner.invoke(app, ["call-log"])
    mock_run.assert_called_once_with("termux-call-log", args=["-l", "10", "-o", "0"])


def test_call_log_custom_limit_and_offset():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=[]) as mock_run:
        runner.invoke(app, ["call-log", "--limit", "5", "--offset", "2"])
    mock_run.assert_called_once_with("termux-call-log", args=["-l", "5", "-o", "2"])


def test_telephony_cellinfo():
    fake = [{"type": "lte"}]
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["telephony", "cellinfo"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-telephony-cellinfo")


def test_telephony_deviceinfo():
    fake = {"network_operator": "Carrier"}
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["telephony", "deviceinfo"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-telephony-deviceinfo")


def test_sms_list_offset_and_type():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=[]) as mock_run:
        runner.invoke(app, ["sms", "list", "--offset", "20", "--type", "inbox"])
    mock_run.assert_called_once_with(
        "termux-sms-list", args=["-l", "10", "-o", "20", "-t", "inbox"]
    )


def test_sms_list_address_and_selection():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=[]) as mock_run:
        runner.invoke(
            app,
            ["sms", "list", "--from", "666", "--selection", "body LIKE 'Foo %'"],
        )
    mock_run.assert_called_once_with(
        "termux-sms-list",
        args=["-l", "10", "-f", "666", "--message-selection=body LIKE 'Foo %'"],
    )


def test_sms_list_sort_order_and_no_order_reverse():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=[]) as mock_run:
        runner.invoke(
            app,
            ["sms", "list", "--sort-order", "date ASC", "--no-order-reverse"],
        )
    mock_run.assert_called_once_with(
        "termux-sms-list",
        args=[
            "-l",
            "10",
            "--message-sort-order=date ASC",
            "--message-return-no-order-reverse",
        ],
    )


def test_sms_list_conversations_nested():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=[]) as mock_run:
        runner.invoke(
            app,
            [
                "sms",
                "list",
                "--conversations",
                "--conversation-multiple-messages",
                "--conversation-nested",
                "--conversation-limit",
                "1",
                "--limit",
                "5",
            ],
        )
    mock_run.assert_called_once_with(
        "termux-sms-list",
        args=[
            "-l",
            "5",
            "-c",
            "--conversation-limit=1",
            "--conversation-return-multiple-messages",
            "--conversation-return-nested-view",
        ],
    )


def test_sms_list_conversation_selection_and_offset():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=[]) as mock_run:
        runner.invoke(
            app,
            [
                "sms",
                "list",
                "--conversations",
                "--conversation-offset",
                "2",
                "--conversation-selection",
                "thread_id == 6",
            ],
        )
    mock_run.assert_called_once_with(
        "termux-sms-list",
        args=[
            "-l",
            "10",
            "-c",
            "--conversation-offset=2",
            "--conversation-selection=thread_id == 6",
        ],
    )


def test_sms_list_conversation_no_order_reverse_sends_explicit_sort_order():
    # Upstream only forwards --conversation-return-no-order-reverse when a
    # conversation sort order is also set, so send the documented default.
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=[]) as mock_run:
        runner.invoke(app, ["sms", "list", "--conversations", "--conversation-no-order-reverse"])
    mock_run.assert_called_once_with(
        "termux-sms-list",
        args=[
            "-l",
            "10",
            "-c",
            "--conversation-sort-order=date DESC",
            "--conversation-return-no-order-reverse",
        ],
    )


def test_sms_list_conversation_option_without_conversations_errors():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=[]) as mock_run:
        result = runner.invoke(app, ["sms", "list", "--conversation-limit", "1"])
    assert result.exit_code == 1
    assert "--conversations" in result.output
    mock_run.assert_not_called()


def test_sms_send_with_slot_and_multiple_numbers():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["sms", "send", "555,666", "hi", "--slot", "1"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-sms-send", args=["-n", "555,666", "-s", "1", "hi"]
    )
