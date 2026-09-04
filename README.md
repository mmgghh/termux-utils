# termux-toolbox

A CLI toolbox exposing Termux:API device capabilities through one command, `mgt`.

## Requirements

- [Termux](https://f-droid.org/en/packages/com.termux/) and the
  [Termux:API](https://f-droid.org/en/packages/com.termux.api/) companion app, both installed
  from F-Droid (not the Play Store builds — they don't interoperate).
- Inside Termux: `pkg install termux-api python`

## Install

```bash
pip install -e '.[dev]'
```

This installs the `mgt` command and pulls in `pytest` for running the test suite.

## Usage

```bash
mgt --help
mgt interactive
mgt battery
mgt --json battery | jq .percentage
mgt sms list --limit 5
mgt sms list --type inbox --from 5551234
mgt sms list --selection "type == 1 and body LIKE 'Foo %'" --limit 1
mgt sms list --conversations --conversation-multiple-messages --conversation-nested
mgt sms send 5551234,5555678 "hello" --slot 1
mgt sms schedule 5551234 "hello later" --at "2026-08-27 15:00"
mgt sms schedule 5551234 "hello later" --in 2h
mgt sms scheduled list
mgt sms scheduled cancel 62d44af8
mgt call-log --limit 5
mgt location --provider network --request last
mgt sensor list
mgt sensor read Accelerometer Gyroscope --delay-ms 500 --limit 3
mgt sensor all --limit 1
mgt sensor cleanup
mgt clipboard get
mgt clipboard set "copied text"
mgt notify "Title" "Body text"
mgt notify "Build" "Deploy?" --id build --button1 Ship --button1-action "deploy.sh"
mgt toast "saved" --short --gravity top --background "#FF333333"
mgt speak "hello" --pitch 1.2 --rate 0.9 --stream MUSIC
mgt notification list
mgt torch on
mgt wifi info
mgt wifi scaninfo
mgt camera info
mgt media play /sdcard/song.mp3
mgt media pause
mgt mic record /sdcard/memo.m4a --duration 0 --encoder opus
mgt mic info
mgt mic stop
mgt share /sdcard/photo.jpg --action send
mgt saf dirs
mgt saf ls content://tree/primary%3ADownload
mgt dialog text --title "Name" --hint "First name"
mgt dialog radio red green blue --title "Pick a colour"
mgt dialog confirm --title "Deploy?"
mgt job schedule /data/data/com.termux/files/home/backup.sh --period-ms 900000 --charging
mgt job list
mgt job cancel 3
mgt keystore generate mykey --algorithm EC --size 256
mgt keystore sign mykey SHA256withECDSA < data.bin > data.sig
mgt keystore verify mykey SHA256withECDSA data.sig < data.bin
mgt usb list
mgt usb permission /dev/bus/usb/001/002 --request
mgt nfc read --full
mgt nfc write "hello tag"
mgt api start
```

Every command supports `--json` (placed before the command, e.g. `mgt --json battery`) for
scriptable output.

See [docs/EXAMPLES.md](docs/EXAMPLES.md) for a comprehensive example of every command and flag.

### Interactive mode

`mgt interactive` browses every command through an arrow-key menu and prompts for each option,
instead of typing flags by hand. It builds on the same command definitions as the regular CLI, so
it stays in sync automatically as commands are added or changed. It needs a real terminal — it
works fine in Termux's terminal app, but not when stdin/stdout are piped or redirected. Commands
that read binary data from stdin (`keystore sign`/`verify`) are still listed but are an awkward
fit for the prompted flow; run those directly instead.

## Coverage

Every command shipped by the `termux-api` package is wrapped, with each binary's full option set
exposed. Two files in that package are deliberately left out: `termux-sms-inbox`, which upstream
replaced with `termux-sms-list`, and `termux-callback`, an internal helper the Termux:API app
invokes on its own. `termux-sms-list`'s legacy `-d`/`-n` flags are also skipped — upstream keeps
them only for backward compatibility.

`sms schedule`/`sms scheduled` is the one exception to the thin-wrapper rule above: it's built
on top of `termux-sms-send` and `termux-job-scheduler` rather than mapping to a single
`termux-api` binary, adding its own local state file to track pending sends.

## Running tests

```bash
pytest
```

All tests mock the underlying `termux-api-*` calls, so the suite runs anywhere — including
directly inside Termux on-device — with no real hardware or granted permissions required.

## Manual smoke-test checklist (real device)

Automated tests mock every `termux-api-*` call, so they can't catch flag mismatches against the
real binaries. Before relying on a new or changed command, run it for real on-device and confirm:

- [ ] `mgt battery` — prints real battery percentage/status
- [ ] `mgt location --provider gps` — prompts for location permission on first run, then prints coordinates
- [ ] `mgt sensor list` — lists real device sensors
- [ ] `mgt sms list --limit 3` — prompts for SMS permission on first run, then lists real messages
- [ ] `mgt sms list --conversations --conversation-nested --conversation-multiple-messages` — returns nested conversations
- [ ] `mgt sms list --type inbox --limit 1 --no-order-reverse` — filters by type and prints newest first
- [ ] `mgt sms schedule <your-number> "test" --in 1m` then wait a minute and `mgt sms scheduled run-due` — a real SMS actually sends and the entry disappears from `mgt sms scheduled list`
- [ ] `mgt sensor all --limit 1` then `mgt sensor cleanup` — reads every sensor once, then releases them
- [ ] `mgt mic record /sdcard/memo.m4a --duration 0` then `mgt mic info` then `mgt mic stop` — records, reports, and stops
- [ ] `mgt contacts list` — prompts for contacts permission on first run, then lists real contacts
- [ ] `mgt clipboard set "test"` then `mgt clipboard get` — round-trips correctly
- [ ] `mgt notify "Test" "Body"` — a real Android notification appears
- [ ] `mgt torch on` then `mgt torch off` — flashlight actually toggles
- [ ] `mgt wifi info` — prints real WiFi connection details
- [ ] `mgt camera photo /sdcard/test.jpg` — prompts for camera permission on first run, then saves a real photo
- [ ] `mgt fingerprint` — prompts the fingerprint sensor and reports the auth result
- [ ] `mgt wallpaper --file /sdcard/pic.jpg` — home screen wallpaper actually changes
- [ ] `mgt wallpaper --file /sdcard/pic.jpg --lockscreen` — lockscreen wallpaper actually changes (regression check for the -l flag fix)
- [ ] `mgt saf managedir` then `mgt saf dirs` — grants folder access via the system picker, then lists it
- [ ] `mgt saf ls <uri>` then `mgt saf read <uri-of-a-file> > /tmp/out` — round-trips a real file's bytes
- [ ] `mgt download "https://example.com/file.zip"` — a real download starts, visible in the notification shade
- [ ] `mgt share /sdcard/photo.jpg` — the Android share sheet appears with the photo attached
- [ ] `mgt notification list` after `mgt notify "Test" "Body"` — the notification appears in the list; `mgt notification remove <id>` clears it
- [ ] `mgt dialog text --title "Name"` — the input dialog appears and the typed text comes back
- [ ] `mgt dialog radio a b c` — the radio dialog appears and the picked value comes back
- [ ] `mgt job schedule ~/hello.sh --period-ms 900000` then `mgt job list` then `mgt job cancel <id>` — the job is scheduled, listed, and cancelled
- [ ] `mgt keystore generate smoketest --algorithm EC` then `mgt keystore list` then `mgt keystore delete smoketest` — the key round-trips
- [ ] `mgt usb list` — lists attached USB devices (empty list is a valid result)
- [ ] `mgt nfc read` — prompts for a tag on NFC-capable devices
- [ ] `mgt api start` — the Termux:API keep-alive service starts without error
- [ ] `mgt interactive` — arrow keys navigate the menu, prompted values run the underlying command correctly, Ctrl+C backs out a level instead of crashing

## License

MIT — see [LICENSE](LICENSE).
