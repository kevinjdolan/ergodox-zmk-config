#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

ZEPHYR_SDK_VERSION="0.16.8"
SDK_DIR="$HOME/zephyr-sdk"

# --- Install dependencies ---

# Homebrew packages
for pkg in cmake ninja dtc ccache wget; do
  if ! command -v "$pkg" &>/dev/null; then
    echo "Installing $pkg..."
    brew install "$pkg"
  fi
done

# West (Zephyr meta-tool)
if ! command -v west &>/dev/null; then
  echo "Installing west..."
  pip3 install west
fi

# Zephyr SDK
if [ ! -d "$SDK_DIR/arm-zephyr-eabi" ]; then
  echo "Installing Zephyr SDK $ZEPHYR_SDK_VERSION..."
  ARCH=$(uname -m)
  if [ "$ARCH" = "arm64" ]; then SDK_ARCH="aarch64"; else SDK_ARCH="x86_64"; fi

  mkdir -p "$SDK_DIR"
  curl -L -o /tmp/zephyr-sdk-minimal.tar.xz \
    "https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v${ZEPHYR_SDK_VERSION}/zephyr-sdk-${ZEPHYR_SDK_VERSION}_macos-${SDK_ARCH}_minimal.tar.xz"
  tar -xf /tmp/zephyr-sdk-minimal.tar.xz -C "$SDK_DIR" --strip-components=1

  curl -L -o /tmp/zephyr-sdk-arm-toolchain.tar.xz \
    "https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v${ZEPHYR_SDK_VERSION}/toolchain_macos-${SDK_ARCH}_arm-zephyr-eabi.tar.xz"
  tar -xf /tmp/zephyr-sdk-arm-toolchain.tar.xz -C "$SDK_DIR"

  # Register SDK with cmake
  mkdir -p ~/.cmake/packages/Zephyr-sdk
  echo "$SDK_DIR/cmake" > ~/.cmake/packages/Zephyr-sdk/zephyr-sdk

  rm -f /tmp/zephyr-sdk-minimal.tar.xz /tmp/zephyr-sdk-arm-toolchain.tar.xz
fi

# --- Initialize west workspace if needed ---
if [ ! -d .west ]; then
  echo "Initializing west workspace..."
  west init -l config
fi

# --- Fetch/update ZMK and Zephyr sources ---
echo "Updating west modules..."
west update

# Register Zephyr cmake package
west zephyr-export

# Install Zephyr Python dependencies
pip3 install -r zephyr/scripts/requirements-base.txt

# --- Build ---
export ZEPHYR_SDK_INSTALL_DIR="$SDK_DIR"
export ZEPHYR_TOOLCHAIN_VARIANT=zephyr

echo "Building firmware..."
west build -s zmk/app -b slicemk_ergodox_202205_green_left -p \
  -- -DSHIELD=slicemk_ergodox_leftcentral \
     -DZMK_CONFIG="$SCRIPT_DIR/config"

# --- Copy output ---
cp build/zephyr/zmk.uf2 config/zmk-left.uf2
echo "Done! Firmware written to config/zmk-left.uf2"
