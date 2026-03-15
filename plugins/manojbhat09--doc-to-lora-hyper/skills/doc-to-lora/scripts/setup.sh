#!/usr/bin/env bash
# Setup Doc-to-LoRA on macOS (Apple Silicon).
# Downloads model weights and installs dependencies.
set -e

REPO_ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$REPO_ROOT"

echo "=== Doc-to-LoRA Setup (macOS) ==="
echo "Repo root: $REPO_ROOT"

# 1. Install uv if missing
if ! command -v uv &>/dev/null; then
    echo "[1/4] Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "[1/4] uv already installed."
fi

# 2. Run the Mac install script (creates venv, installs deps)
if [ ! -d ".venv" ]; then
    echo "[2/4] Installing Python dependencies (Mac-compatible)..."
    bash install_mac.sh
else
    echo "[2/4] .venv already exists, skipping dependency install."
fi

# Activate
source .venv/bin/activate

# 3. Install MLX dependencies for fast Apple Silicon inference
echo "[3/4] Installing MLX dependencies..."
uv pip install mlx mlx-lm safetensors 2>/dev/null || true

# 4. Download pretrained D2L weights from HuggingFace
if [ ! -d "trained_d2l" ]; then
    echo "[4/4] Downloading Doc-to-LoRA weights (~3GB)..."
    echo "       You may need to set HF_TOKEN for gated models."
    uv run huggingface-cli download SakanaAI/doc-to-lora --local-dir trained_d2l
else
    echo "[4/4] trained_d2l/ already present, skipping download."
fi

# 5. Download base model (Gemma 2 2B) if not cached
echo ""
echo "Ensuring Gemma 2 2B-it is cached..."
python -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
print('Checking model cache...')
try:
    AutoTokenizer.from_pretrained('google/gemma-2-2b-it')
    print('  Tokenizer: cached')
except Exception as e:
    print(f'  Tokenizer: needs download ({e})')
try:
    AutoModelForCausalLM.from_pretrained('google/gemma-2-2b-it', device_map='cpu', torch_dtype='auto')
    print('  Model: cached')
except Exception as e:
    print(f'  Model: needs download ({e})')
" 2>/dev/null || echo "  Model download may require HF_TOKEN with Gemma access."

echo ""
echo "=== Setup complete ==="
echo "Activate:  source .venv/bin/activate"
echo ""
echo "Quick test:"
echo "  python demo_dario.py"
