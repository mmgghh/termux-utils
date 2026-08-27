# Command examples

Every example below assumes `mgt` is installed and running inside Termux with the
Termux:API app granted the relevant permissions. Add `--json` right after `mgt` (before the
subcommand) on any command to get raw, scriptable JSON instead of formatted text:

```bash
mgt --json battery
mgt --json sms list --limit 1 | jq '.[0].body'
```

Commands are grouped the same way `mgt --help` groups them.

## Sensors & device state

### `battery`

```bash
mgt battery
mgt --json battery | jq .percentage
```

### `location`

```bash
mgt location                                    # gps provider, wait for a single fix
mgt location --provider network --request last  # last known fix, no new request
mgt location --provider passive --request updates
```

### `fingerprint`

```bash
mgt fingerprint
mgt fingerprint --title "Confirm purchase" --subtitle "Touch sensor" --cancel "Not now"
```

### `sensor`

`read`/`all` match sensor names by substring against the names from `sensor list`, so
`Accel` is enough to hit `Accelerometer`. Android keeps a sensor listening (and draining
battery) until it's explicitly released, which is what `cleanup` is for — run it once you're
done reading, especially after `all`.

```bash
mgt sensor list
mgt sensor read Accelerometer --limit 5
mgt sensor read Accelerometer Gyroscope --delay-ms 500 --limit 3
mgt sensor all --limit 1
mgt sensor cleanup   # release sensors held open by a previous read
```

### `infrared`

The pattern is a comma-separated list of on/off durations in milliseconds, always starting
with an "on" interval: `"20,50,20,30"` means on 20ms, off 50ms, on 20ms, off 30ms. Most
remote-control codes are expressed this way; `--frequency` is the IR carrier frequency the
receiver expects (commonly 38000Hz), not part of the pattern itself.

```bash
mgt infrared frequencies
mgt infrared transmit "20,50,20,30" --frequency 38000
mgt infrared transmit "9000,4500,560,560,560,1690" -f 38000
```

## Messaging

### `sms`

`--selection`/`--sort-order` filter and order individual messages; the `--conversation-*`
equivalents do the same for the conversation (thread) list and only take effect together with
`--conversations`. Within conversations, `--conversation-multiple-messages` returns every
message in each thread instead of just the latest one, and `--conversation-nested` reshapes
the result as an object keyed by conversation ID instead of a flat array — the two combine
to give a full nested thread view.

```bash
mgt sms list                                                    # 10 most recent, any type
mgt sms list --limit 5 --offset 10
mgt sms list --type inbox --from 5551234
mgt sms list --selection "type == 1 and body LIKE 'Foo %'" --limit 1
mgt sms list --sort-order "date ASC" --no-order-reverse

# Conversations (thread view) instead of individual messages:
mgt sms list --conversations
mgt sms list --conversations --conversation-limit 5 --conversation-offset 0
mgt sms list --conversations --conversation-selection "thread_id == 6"
mgt sms list --conversations --conversation-multiple-messages --conversation-nested
mgt sms list --conversations --conversation-sort-order "date ASC" --conversation-no-order-reverse

# Conversation flags are rejected without --conversations:
mgt sms list --conversation-limit 5
# Error: --conversation-limit only applies with --conversations.

mgt sms send 5551234 "hello"
mgt sms send 5551234,5555678 "hello everyone" --slot 1   # comma-separated recipients
```

### `sms schedule` / `sms scheduled`

`schedule` saves the message to disk instead of sending it immediately, so it survives
Termux being killed or the device rebooting; give it exactly one of `--at` (a local
time) or `--in` (a duration like `2h`, `45m`, or `1h30m`). The first time you schedule
anything, it also registers a recurring `mgt job` (Android's `JobScheduler`, ~15-minute
minimum period) that checks for and sends due messages — so delivery can lag up to
~15 minutes after the target time, and nothing sends until that job actually ticks. A
failed send is retried automatically up to 3 times before being marked `failed`; it then
stays visible in `scheduled list` (rather than vanishing) until you `scheduled cancel` it.
`scheduled run-due` is what the background job calls — run it by hand to force an
immediate check instead of waiting for the next tick.

```bash
mgt sms schedule 5551234 "don't forget the meeting" --at "2026-08-27 15:00"
mgt sms schedule 5551234,5555678 "reminder" --in 2h --slot 1
mgt sms schedule 5551234 "hi" --at "2026-08-27 15:00" --in 1h
# Error: provide exactly one of --at or --in.

mgt sms scheduled list
mgt sms scheduled run-due     # force an immediate check instead of waiting for the job
mgt sms scheduled cancel 62d44af8
```

### `call` / `call-log`

```bash
mgt call 5551234
mgt call-log
mgt call-log --limit 20 --offset 5
```

### `contacts`

```bash
mgt contacts list
mgt --json contacts list | jq '.[] | select(.name | test("Ana"))'
```

### `telephony`

```bash
mgt telephony cellinfo
mgt telephony deviceinfo
```

## Feedback & notifications

### `notify`

`--id` names the notification so a later `mgt notify` with the same `--id` replaces it in
place instead of stacking a new one — this is what makes `--ongoing` (a pinned, undismissable
notification) removable at all, hence the required pairing. `--type media` swaps in
transport-style buttons (play/pause/next/previous) instead of the generic `--button1..3`,
each firing the shell action given to the matching `--media-*` flag. `--led-*` flags only
have a visible effect on devices with a physical notification LED.

```bash
mgt notify "Title" "Body text"
echo "Body from stdin" | mgt notify "Title"

# Actionable notification with two buttons:
mgt notify "Build" "Deploy?" --id build --button1 Ship --button1-action "deploy.sh" \
  --button2 Cancel --button2-action "true"

# Ongoing (pinned) notification requires --id:
mgt notify "Sync" "Running..." --id sync --ongoing
mgt notify "Sync" "Running..." --ongoing
# Error: --ongoing needs --id, otherwise the notification can't be removed.

# Priority, channel, group, LED, vibration and sound:
mgt notify "Alert" "Something happened" --priority high --channel alerts --group monitoring \
  --led-color FF0000 --led-on 500 --led-off 500 --vibrate "500,1000,200" --sound

# Media-style notification:
mgt notify "Podcast" "Episode 12" --type media \
  --media-play "mgt media play" --media-pause "mgt media pause" \
  --media-next "next.sh" --media-previous "prev.sh"
```

### `toast`

```bash
mgt toast "saved"
mgt toast "saved" --short --gravity top --background "#FF333333"
mgt toast "error" --background red --text-color white --gravity bottom
```

### `vibrate`

```bash
mgt vibrate
mgt vibrate --duration-ms 2000
mgt vibrate --duration-ms 500 --force   # vibrate even in silent mode
```

### `speak` / `tts-engines` / `speech-to-text`

`--stream` picks which Android audio stream the speech plays on (default `NOTIFICATION`), which
matters because it's controlled by a different hardware volume slider than `MUSIC` or
`ALARM` — use `mgt tts-engines` first to see which `--engine` values are installed.
`speech-to-text --progress` prints partial transcriptions as they're recognized instead of
only the final result once you stop speaking.

```bash
mgt tts-engines
mgt speak "hello"
mgt speak "hello there" --pitch 1.2 --rate 0.9 --stream MUSIC
mgt speak "bonjour" --engine com.google.android.tts --language fr --region FR
mgt speech-to-text
mgt speech-to-text --progress
```

### `download`

```bash
mgt download "https://example.com/file.zip"
mgt download "https://example.com/file.zip" --title "My file" --description "Nightly build" \
  --path /sdcard/Download/file.zip
```

### `share`

`--action` controls what Android is asked to do with the content: `view` opens it, `send`
hands it to another app (e.g. a messaging app), `edit` opens an editor for it. Normally this
pops the system chooser so the user picks an app; `--default-receiver` skips that and sends
straight to whatever app Android has set as the default handler for the content type.

```bash
mgt share /sdcard/photo.jpg                          # opens the share sheet (view)
mgt share /sdcard/photo.jpg --action send --title "Vacation pic"
mgt share /sdcard/report.pdf --action edit --content-type application/pdf
echo "shared text" | mgt share --default-receiver     # no file: shares stdin text
```

### `clipboard`

```bash
mgt clipboard set "copied text"
mgt clipboard get
mgt clipboard get | mgt notify "Clipboard"
```

### `notification`

```bash
mgt notification list
mgt notification remove build
mgt notification channel create alerts "Alerts"
mgt notification channel delete alerts
```

## Media

### `camera`

```bash
mgt camera info
mgt camera photo /sdcard/photo.jpg                  # back camera by default
mgt camera photo /sdcard/selfie.jpg --camera front
mgt camera photo /sdcard/photo.jpg --camera 2        # raw camera ID from 'camera info'
```

### `media`

```bash
mgt media play /sdcard/song.mp3
mgt media play               # resume playback with no file
mgt media pause
mgt media stop
mgt media info
mgt media scan /sdcard/Music --recursive --verbose
```

### `mic`

```bash
mgt mic record /sdcard/memo.m4a --duration 10
mgt mic record /sdcard/memo.opus --duration 0 --encoder opus   # 0 = record until stopped
mgt mic record --duration 30 --bitrate 128 --sample-rate 44100 --channels 2
mgt mic info
mgt mic stop
```

## Device control

### `torch` / `volume` / `brightness` / `audio-info`

```bash
mgt torch on
mgt torch off
mgt volume                    # show every stream's current level
mgt volume music 8            # set the music stream to level 8
mgt volume music
# Error: provide both stream and level, or neither.
mgt brightness 128
mgt brightness auto
mgt audio-info
```

### `wallpaper`

```bash
mgt wallpaper --file /sdcard/pic.jpg
mgt wallpaper --url "https://example.com/wall.jpg"
mgt wallpaper --file /sdcard/pic.jpg --lockscreen
mgt wallpaper --file /sdcard/pic.jpg --url "https://example.com/wall.jpg"
# Error: provide exactly one of --file or --url.
```

### `wifi`

```bash
mgt wifi info
mgt wifi enable
mgt wifi disable
mgt wifi scaninfo
```

### `usb`

Android doesn't let apps open USB device nodes directly; instead it hands over an already-open
file descriptor once permission is granted. Identify the device either by its path from
`usb list`, or by `--vendor-id`/`--product-id` (useful for scripts that shouldn't hardcode a
path that can change between plug-ins). `--request` pops the system permission dialog if
access hasn't been granted yet; without it the command just checks/fails silently on missing
permission. `usb run` executes `--command` with that descriptor available as file descriptor 3
by default, or exported as the `$TERMUX_USB_FD` environment variable if `--env-fd` is set.

```bash
mgt usb list
mgt usb permission /dev/bus/usb/001/002
mgt usb permission /dev/bus/usb/001/002 --request       # show the permission dialog if needed
mgt usb permission --vendor-id 0x1234 --product-id 0x5678 --request
mgt usb run /dev/bus/usb/001/002 --command "cat /proc/self/fd/3" --request
mgt usb run /dev/bus/usb/001/002 --command "my-tool" --env-fd   # fd via $TERMUX_USB_FD instead
```

### `nfc`

`--full` on `read` returns the tag's complete NDEF record data (all fields Android exposes);
without it you get a short summary. Both `read` and `write` block waiting for a tag, so hold
it against the device's NFC antenna after running the command, not before.

```bash
mgt nfc read                 # hold a tag against the device when prompted
mgt nfc read --full
mgt nfc write "hello tag"
```

## Storage

### `storage-get`

```bash
mgt storage-get /sdcard/downloaded.pdf   # opens the system file picker
```

### `saf`

The Storage Access Framework is Android's permission-scoped alternative to raw file paths:
access is granted per-folder through a system picker (`managedir`), and everything inside is
then addressed by opaque `content://` URIs rather than filesystem paths — you can't construct
these by hand. Get the folder's URI from `dirs`, then get file/subfolder URIs by listing it
with `ls` or by capturing the output of `create`/`mkdir`, which print the URI of what they just
made.

```bash
mgt saf managedir                                        # grant access to a folder via picker
mgt saf dirs                                              # list folders already granted

mgt saf ls content://tree/primary%3ADownload
mgt saf stat content://tree/primary%3ADownload/document/primary%3ADownload%2Ffile.txt
mgt saf create content://tree/primary%3ADownload notes.txt --mime-type text/plain
mgt saf mkdir content://tree/primary%3ADownload archive

# Byte streams go through stdin/stdout rather than --json:
mgt saf read content://tree/primary%3ADownload/document/primary%3ADownload%2Ffile.txt > /tmp/out
cat local.txt | mgt saf write content://tree/primary%3ADownload/document/primary%3ADownload%2Fnotes.txt

mgt saf rm content://tree/primary%3ADownload/document/primary%3ADownload%2Fnotes.txt
```

## Dialogs

Every dialog blocks until the user responds (or dismisses it), so give it time.

```bash
mgt dialog text --title "Name" --hint "First name"
mgt dialog text --title "PIN" --numeric --password
mgt dialog text --title "Notes" --multiline
mgt dialog text --title "Notes" --multiline --numeric
# Error: --multiline cannot be combined with --numeric.

mgt dialog confirm --title "Deploy?"
mgt dialog checkbox red green blue --title "Pick colours"
mgt dialog radio red green blue --title "Pick a colour"
mgt dialog sheet Yes No Maybe --title "Bottom sheet pick"
mgt dialog spinner Mon Tue Wed --title "Pick a day"
mgt dialog counter --title "Quantity" --range 1,100,50   # min,max,starting-value
mgt dialog date --title "Birthday" --date-format "dd-MM-yyyy"
mgt dialog time --title "Alarm"
mgt dialog speech --title "Say something" --hint "Speak now"
```

## System

### `job`

This wraps Android's `JobScheduler`, so the OS decides exactly when a scheduled script runs
within the constraints given — it is not a precise cron. Without `--period-ms` the job fires
once at the OS's discretion; with it, the job repeats roughly every N milliseconds, but Android
enforces a minimum of 900000ms (15 minutes) and may delay further to save battery. Reusing a
`--job-id` replaces that job instead of adding a new one. `--trigger-content-uri` runs the job
whenever the given content provider URI changes (e.g. new photos), instead of on a timer;
`--trigger-content-flag` tunes how that change notification is matched (default 1) and only
applies alongside it, on Android 7+.

```bash
mgt job schedule /data/data/com.termux/files/home/backup.sh --period-ms 900000 --charging
mgt job schedule ~/sync.sh --job-id 3 --network unmetered --battery-not-low --persisted
mgt job schedule ~/once.sh                                      # runs once, no period
mgt job schedule ~/on-change.sh --trigger-content-uri content://media/external/images/media \
  --trigger-content-flag 1
mgt job list
mgt job cancel 3
mgt job cancel-all
```

### `keystore`

Keys live in Android's hardware-backed keystore and never leave it — there's no export; you
can only generate, use, or delete them. `--size` depends on `--algorithm`: 2048/3072/4096 for
RSA, 256/384/521 for EC. `--validity` requires the key to be unlocked (e.g. by device
screen-lock) within that many seconds before each use, and is omitted by default (no
unlock requirement). `sign`/`verify` operate on stdin so they compose with pipes, and the
algorithm string (e.g. `SHA256withECDSA`, `SHA256withRSA`) must match what the key's
`--algorithm` supports.

```bash
mgt keystore generate mykey --algorithm EC --size 256
mgt keystore generate mykey-rsa --algorithm RSA --size 4096 --validity 300
mgt keystore list
mgt keystore list --detailed
mgt keystore sign mykey SHA256withECDSA < data.bin > data.sig
mgt keystore verify mykey SHA256withECDSA data.sig < data.bin
mgt keystore delete mykey
```

### `api`

```bash
mgt api start
mgt api stop
```
