# ErgoDox Wireless ZMK Config

Custom ZMK keymap for the [SliceMK ErgoDox Wireless](https://www.slicemk.com/pages/ergodox-wireless) (202205 Green, dongleless).

## Layout

Three layers with a focus on keeping common programming symbols accessible without stretching.

### Main Layer

Standard QWERTY with several customizations:

- **Top row**: `DEL`, `$`, `*`, `-`, `_`, `=` on the left; `[]`, `()`, `{}` pairs on the right — all programming brackets on the right hand.
- **Custom shift keys**: Comma shifts to `?`, period shifts to `!`, slash shifts to `\`. Keeps punctuation fluid without reaching for the number row.
- **Thumb clusters**: Backspace and Escape under the left thumb; Enter and Space under the right. Home/End and PgUp/PgDn on the outer thumb keys.
- **Hyper keys**: `Ctrl+Shift+Alt` in the bottom-left and bottom-right corners; `Ctrl+Shift+Alt+Gui` on the inner thumb keys — useful for global shortcuts that won't collide with any application.
- **Modifiers**: Shift on the pinkies, Ctrl and Alt on the bottom row, Gui on the lowest thumb position.
- **`sys_off`** on the top-left key to put the keyboard to sleep.

### NumSym Layer (hold left or right home-row key)

- **Right hand**: Full numpad (0–9) with `/`, `*`, `+`, `-`, `=`.
- **Left hand**: Remaining symbols — `%`, `^`, `|`, `&`, `#`, `@`, `<`, `>`.

### Function Layer (hold either key flanking the top row)

Media controls on the right hand: previous/play-pause/next, volume down/mute/up. Everything else is disabled.

## Building

Requirements: macOS with [Homebrew](https://brew.sh). The build script installs everything else automatically (cmake, ninja, dtc, the Zephyr SDK + ARM toolchain, west, and Python dependencies).

```
./build.sh
```

This produces `config/zmk-left.uf2`.

## Flashing

The left and right halves are flashed separately. The right half runs peripheral firmware (download from [SliceMK](https://docs.slicemk.com/keyboard/ergodox/peripheral/)). The left half runs the firmware built here.

**Important**: Check your PCB version before flashing. Put the half into bootloader mode and open `INFO_UF2.TXT` on the drive to verify. Using firmware for the wrong PCB version can damage hardware.

### Flash the right half (peripheral)

1. Connect the **right half** via USB.
2. Double-press the reset button within 500ms (or hold the user button while plugging in USB).
3. A drive named **SliceMK** appears.
4. Copy the peripheral `.uf2` file onto the drive. It ejects automatically when done.

### Flash the left half (central)

1. Connect the **left half** via USB.
2. Double-press the reset button within 500ms.
3. Copy `config/zmk-left.uf2` onto the **SliceMK** drive.

Do not put both halves into bootloader mode at the same time — they both appear as "SliceMK" and your OS won't distinguish them.

The OS may report an error about the drive ejecting unexpectedly. This is normal.

## Customization

- Edit the keymap: `config/slicemk_ergodox.keymap`
- Edit ZMK options: `config/slicemk_ergodox_leftcentral.conf`
- Change the ZMK fork: `config/west.yml`

For questions, join the [SliceMK Discord](https://discord.gg/FQvyd7BAaA).
