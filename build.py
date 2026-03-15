#!/usr/bin/env python3
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import click
import urllib.request

ROOT = Path(__file__).resolve().parent
FIRMWARE_DIR = ROOT / "firmware"
VOLUME = Path("/Volumes/SliceMK")
ZEPHYR_SDK_VERSION = "0.16.8"
SDK_DIR = Path.home() / "zephyr-sdk"


def run(cmd, **kwargs):
    click.echo(f"$ {cmd}")
    subprocess.run(cmd, shell=True, check=True, **kwargs)


def has_cmd(name):
    return shutil.which(name) is not None


def get_board():
    build_yaml = ROOT / "build.yaml"
    for line in build_yaml.read_text().splitlines():
        m = re.search(r"board:\s*(\S+)", line)
        if m:
            return m.group(1)
    raise click.ClickException("No board found in build.yaml")


def get_pcb_version():
    board = get_board()
    # slicemk_ergodox_202205_green_left -> 202205_green
    version = re.sub(r"^slicemk_ergodox_", "", board)
    version = re.sub(r"_(left|right)$", "", version)
    return version


def install_deps():
    for pkg in ("cmake", "ninja", "dtc", "ccache", "wget"):
        if not has_cmd(pkg):
            click.echo(f"Installing {pkg}...")
            run(f"brew install {pkg}")

    if not has_cmd("west"):
        click.echo("Installing west...")
        run("pip3 install west")

    if not (SDK_DIR / "arm-zephyr-eabi").is_dir():
        click.echo(f"Installing Zephyr SDK {ZEPHYR_SDK_VERSION}...")
        arch = "aarch64" if platform.machine() == "arm64" else "x86_64"
        SDK_DIR.mkdir(parents=True, exist_ok=True)

        minimal = f"zephyr-sdk-{ZEPHYR_SDK_VERSION}_macos-{arch}_minimal.tar.xz"
        toolchain = f"toolchain_macos-{arch}_arm-zephyr-eabi.tar.xz"
        base_url = f"https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v{ZEPHYR_SDK_VERSION}"

        for filename in (minimal, toolchain):
            tmp = Path(f"/tmp/{filename}")
            run(f'curl -L -o {tmp} "{base_url}/{filename}"')
            if filename == minimal:
                run(f"tar -xf {tmp} -C {SDK_DIR} --strip-components=1")
            else:
                run(f"tar -xf {tmp} -C {SDK_DIR}")
            tmp.unlink()

        cmake_pkg = Path.home() / ".cmake" / "packages" / "Zephyr-sdk"
        cmake_pkg.mkdir(parents=True, exist_ok=True)
        (cmake_pkg / "zephyr-sdk").write_text(str(SDK_DIR / "cmake"))


def init_workspace(upgrade):
    os.chdir(ROOT)

    if not (ROOT / ".west").is_dir():
        click.echo("Initializing west workspace...")
        run("west init -l config")

    if not (ROOT / "zmk").is_dir() or upgrade:
        click.echo("Updating west modules...")
        run("west update")
        run("west zephyr-export")
        run("pip3 install -r zephyr/scripts/requirements-base.txt")
    else:
        click.echo("Skipping west update (use --upgrade to update).")


@click.group()
def cli():
    """ZMK firmware build and flash tool for SliceMK ErgoDox."""


@cli.command()
@click.option("--upgrade", is_flag=True, help="Force update of west modules.")
def build(upgrade):
    """Build the left-side ZMK firmware."""
    install_deps()
    init_workspace(upgrade)

    board = get_board()
    env = {
        **os.environ,
        "ZEPHYR_SDK_INSTALL_DIR": str(SDK_DIR),
        "ZEPHYR_TOOLCHAIN_VARIANT": "zephyr",
    }

    click.echo("Building firmware...")
    run(
        f"west build -s zmk/app -b {board} -p"
        f" -- -DSHIELD=slicemk_ergodox_leftcentral"
        f' -DZMK_CONFIG="{ROOT / "config"}"',
        env=env,
    )

    FIRMWARE_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "build" / "zephyr" / "zmk.uf2", FIRMWARE_DIR / "zmk-left.uf2")
    click.echo(f"Done! Firmware written to firmware/zmk-left.uf2")


@cli.command()
@click.option("--right", is_flag=True, help="Flash the right peripheral instead.")
@click.option("--build", "do_build", is_flag=True, help="Run build before flashing.")
@click.option("--upgrade", is_flag=True, help="Pass --upgrade to build.")
def flash(right, do_build, upgrade):
    """Flash firmware to a keyboard half."""
    if do_build:
        ctx = click.get_current_context()
        ctx.invoke(build, upgrade=upgrade)

    if right:
        uf2 = FIRMWARE_DIR / "zmk-right.uf2"
        FIRMWARE_DIR.mkdir(parents=True, exist_ok=True)
        if not uf2.exists():
            pcb = get_pcb_version()
            url = f"https://static.slicemk.com/firmware/keyboard/peripheral/4.2.0/ergodox-{pcb}-peripheral_ble-right.uf2"
            click.echo(f"Downloading right peripheral firmware...\n  {url}")
            urllib.request.urlretrieve(url, uf2)
        side_label = "RIGHT"
    else:
        uf2 = FIRMWARE_DIR / "zmk-left.uf2"
        side_label = "LEFT"

    if not uf2.exists():
        raise click.ClickException(f"{uf2} not found. Run 'build' first.")

    click.secho(f"1. Plug the {side_label} half of the keyboard in via USB.", fg="yellow")
    click.secho("2. Double-press the reset button within 500ms.", fg="yellow")
    click.secho("3. Wait for the LED to turn solid green (bootloader mode).", fg="yellow")
    click.echo()
    click.echo("Waiting for SliceMK volume to appear...")

    while not VOLUME.is_dir():
        time.sleep(0.5)

    click.secho("SliceMK volume detected! Waiting for mount...", fg="green")
    time.sleep(3)
    click.echo(f"Copying {uf2.name}...")
    dest = VOLUME / "CURRENT.UF2"
    if not dest.exists():
        dest = VOLUME / uf2.name
    with open(uf2, "rb") as src, open(dest, "wb") as dst:
        dst.write(src.read())

    click.echo("Waiting for flash to complete...")
    while VOLUME.is_dir():
        time.sleep(0.5)

    click.echo("Done! Volume ejected. Firmware has been flashed.")


if __name__ == "__main__":
    cli()
