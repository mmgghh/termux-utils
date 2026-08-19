from unittest.mock import patch

from typer.testing import CliRunner

from termux_toolbox.cli import app

runner = CliRunner()


def test_torch_on():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["torch", "on"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-torch", args=["on"])


def test_torch_rejects_invalid_state():
    result = runner.invoke(app, ["torch", "sideways"])
    assert result.exit_code == 2
    assert "on" in result.output and "off" in result.output


def test_volume_no_args_queries_all_streams():
    fake = [{"stream": "music", "volume": 5, "max_volume": 15}]
    with patch("termux_toolbox.commands.device.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["volume"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-volume", args=[])


def test_volume_sets_stream_level():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["volume", "music", "8"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-volume", args=["music", "8"])


def test_volume_rejects_stream_without_level():
    result = runner.invoke(app, ["volume", "music"])
    assert result.exit_code == 1
    assert "Error:" in result.output


def test_brightness():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["brightness", "128"])
    mock_run.assert_called_once_with("termux-brightness", args=["128"])


def test_wifi_info():
    fake = {"ssid": "MyNetwork", "ip": "192.168.1.5"}
    with patch("termux_toolbox.commands.device.run_termux_api", return_value=fake):
        result = runner.invoke(app, ["wifi", "info"])
    assert result.exit_code == 0
    assert "ssid: MyNetwork" in result.output


def test_wifi_enable():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["wifi", "enable"])
    mock_run.assert_called_once_with("termux-wifi-enable", args=["true"])


def test_wifi_disable():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["wifi", "disable"])
    mock_run.assert_called_once_with("termux-wifi-enable", args=["false"])


def test_wifi_info_json_output():
    fake = {"ssid": "MyNetwork"}
    with patch("termux_toolbox.commands.device.run_termux_api", return_value=fake):
        result = runner.invoke(app, ["--json", "wifi", "info"])
    assert result.exit_code == 0
    assert result.output.strip() == '{"ssid": "MyNetwork"}'


def test_audio_info():
    fake = {"outputs": ["speaker"]}
    with patch("termux_toolbox.commands.device.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["audio-info"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-audio-info")


def test_wallpaper_from_file():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["wallpaper", "--file", "/sdcard/pic.jpg"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-wallpaper", args=["-f", "/sdcard/pic.jpg"])


def test_wallpaper_from_url_lockscreen():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["wallpaper", "--url", "https://example.com/a.jpg", "--lockscreen"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-wallpaper", args=["-u", "https://example.com/a.jpg", "-l"]
    )


def test_wallpaper_rejects_neither_file_nor_url():
    result = runner.invoke(app, ["wallpaper"])
    assert result.exit_code == 1
    assert "Error:" in result.output


def test_wallpaper_rejects_both_file_and_url():
    result = runner.invoke(app, ["wallpaper", "--file", "a.jpg", "--url", "http://x"])
    assert result.exit_code == 1
    assert "Error:" in result.output


def test_wifi_scaninfo():
    fake = [{"ssid": "MyNetwork", "level": -50}]
    with patch("termux_toolbox.commands.device.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["wifi", "scaninfo"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-wifi-scaninfo")


def test_usb_list():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value=[]) as mock_run:
        result = runner.invoke(app, ["usb", "list"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-usb", args=["-l"])


def test_usb_permission_with_device_path():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["usb", "permission", "/dev/bus/usb/001/002", "--request"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-usb", args=["-r", "/dev/bus/usb/001/002"], timeout=120.0
    )


def test_usb_permission_with_vendor_and_product_id():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(
            app, ["usb", "permission", "--vendor-id", "1234", "--product-id", "5678"]
        )
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-usb", args=["1234", "5678"], timeout=120.0)


def test_usb_permission_without_device_errors():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["usb", "permission"])
    assert result.exit_code == 1
    mock_run.assert_not_called()


def test_usb_run_command():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(
            app,
            ["usb", "run", "/dev/bus/usb/001/002", "--command", "lsusb.sh", "--env-fd", "--request"],
        )
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-usb",
        args=["-r", "-e", "lsusb.sh", "-E", "/dev/bus/usb/001/002"],
        timeout=120.0,
    )


def test_nfc_read_short_by_default():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["nfc", "read"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-nfc", args=["-r", "short"], timeout=120.0)


def test_nfc_read_full():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["nfc", "read", "--full"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-nfc", args=["-r", "full"], timeout=120.0)


def test_nfc_write():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["nfc", "write", "hello tag"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-nfc", args=["-w", "-t", "hello tag"], timeout=120.0
    )
