#!/usr/bin/env bash
set -e

# Project root is one level up from this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "[1/4] Checking Python..."
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Install with: brew install python"
    exit 1
fi

echo "[2/4] Installing / updating dependencies..."
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet -r "$ROOT/requirements.txt"
python3 -m pip install --quiet pyinstaller

echo "[3/4] Downloading EasyOCR models..."
MODELS_DIR="$ROOT/backend/models"
mkdir -p "$MODELS_DIR"

if [ ! -f "$MODELS_DIR/craft_mlt_25k.pth" ]; then
    echo "  -> craft_mlt_25k.pth"
    curl -L --insecure -o  /tmp/craft.zip \
        "https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.zip"
    unzip -o /tmp/craft.zip -d "$MODELS_DIR"
    rm /tmp/craft.zip
fi

if [ ! -f "$MODELS_DIR/latin_g2.pth" ]; then
    echo "  -> latin_g2.pth"
    curl -L --insecure -o  /tmp/latin.zip \
        "https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/latin_g2.zip"
    unzip -o /tmp/latin.zip -d "$MODELS_DIR"
    rm /tmp/latin.zip
fi

echo "[4/4] Building executable..."
python3 -m PyInstaller "$ROOT/build/salary-manager.spec" \
    --distpath "$ROOT/dist" \
    --workpath "$ROOT/build/_tmp" \
    --noconfirm

echo ""
echo "============================================================"
echo " Build complete: dist/SalaryManager/SalaryManager"
echo " OCR models are downloaded automatically on first use."
echo "============================================================"
