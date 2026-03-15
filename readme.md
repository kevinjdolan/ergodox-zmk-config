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

- **Left hand**: Media controls (prev/play/next on W/E/R, vol down/mute/vol up on S/D/F) and brightness (up on T, down on G).
- **Right hand**: F-keys mirroring the numpad layout — F7/F8/F9 on top, F4/F5/F6 on home, F1/F2/F3 on bottom, with F10/F11/F12 on the inner column.

## Building and Flashing

Requirements: macOS with [Homebrew](https://brew.sh) and Python 3. The build script installs everything else automatically (cmake, ninja, dtc, the Zephyr SDK + ARM toolchain, west, and Python dependencies).

```
# Build the left-side firmware
./build.sh build

# Build and update west modules
./build.sh build --upgrade

# Flash the left half (interactive — prompts you to enter bootloader mode)
./build.sh flash

# Build then flash in one step
./build.sh flash --build

# Flash the right half (downloads peripheral firmware from SliceMK)
./build.sh flash --right
```

**Important**: Check your PCB version before flashing. Put the half into bootloader mode and open `INFO_UF2.TXT` on the SliceMK drive to verify. Using firmware for the wrong PCB version can damage hardware.

The flash command will prompt you to plug in the keyboard half via USB and double-press the reset button. It automatically detects the SliceMK volume, copies the firmware, and waits for the volume to eject. The OS may report an eject error — this is normal.

Do not put both halves into bootloader mode at the same time — they both appear as "SliceMK" and your OS won't distinguish them.

## Customization

- Edit the keymap: `config/slicemk_ergodox.keymap`
- Edit ZMK options: `config/slicemk_ergodox_leftcentral.conf`
- Change the ZMK fork: `config/west.yml`

For questions, join the [SliceMK Discord](https://discord.gg/FQvyd7BAaA).
