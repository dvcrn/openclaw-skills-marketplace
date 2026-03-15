"""NIM model registry — verified working models with characteristics."""

NIM_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"

# Verified working models (benchmarked 2026-03-13)
MODELS = {
    # Fast tier (<1s)
    "llama-3.3": {
        "id": "meta/llama-3.3-70b-instruct",
        "speed": "fast",
        "family": "meta",
        "params": "70B",
        "thinking": False,
    },
    "gemma-27b": {
        "id": "google/gemma-3-27b-it",
        "speed": "fast",
        "family": "google",
        "params": "27B",
        "thinking": False,
    },
    "nemotron-super-49b": {
        "id": "nvidia/llama-3.3-nemotron-super-49b-v1",
        "speed": "fast",
        "family": "nvidia",
        "params": "49B",
        "thinking": False,
    },
    "jamba-mini": {
        "id": "ai21labs/jamba-1.5-mini-instruct",
        "speed": "fast",
        "family": "ai21",
        "params": "?",
        "thinking": False,
    },
    "dracarys-70b": {
        "id": "abacusai/dracarys-llama-3.1-70b-instruct",
        "speed": "fast",
        "family": "abacusai",
        "params": "70B",
        "thinking": False,
    },

    # Medium tier (1-3s)
    "kimi-k2": {
        "id": "moonshotai/kimi-k2-instruct",
        "speed": "medium",
        "family": "moonshot",
        "params": "?",
        "thinking": False,
    },
    "mistral-large": {
        "id": "mistralai/mistral-large-3-675b-instruct-2512",
        "speed": "medium",
        "family": "mistral",
        "params": "675B",
        "thinking": False,
    },
    "llama-405b": {
        "id": "meta/llama-3.1-405b-instruct",
        "speed": "medium",
        "family": "meta",
        "params": "405B",
        "thinking": False,
    },
    "qwen-397b": {
        "id": "qwen/qwen3.5-397b-a17b",
        "speed": "medium",
        "family": "qwen",
        "params": "397B",
        "thinking": False,
    },

    "mistral-medium": {
        "id": "mistralai/mistral-medium-3-instruct",
        "speed": "medium",
        "family": "mistral",
        "params": "?",
        "thinking": False,
    },
    # Slow tier (3s+)
    "deepseek-v3.1-term": {
        "id": "deepseek-ai/deepseek-v3.1-terminus",
        "speed": "slow",
        "family": "deepseek",
        "params": "?",
        "thinking": False,
    },

    # Thinking models (5-40s, need special handling)
    "minimax-m2.5": {
        "id": "minimaxai/minimax-m2.5",
        "speed": "slow",
        "family": "minimax",
        "params": "?",
        "thinking": True,
        "think_style": "inline",  # <think>...</think> in content field
    },
    "kimi-k2.5": {
        "id": "moonshotai/kimi-k2.5",
        "speed": "slow",
        "family": "moonshot",
        "params": "?",
        "thinking": True,
        "think_style": "separate",  # reasoning_content field, content can be null
    },
}

# Models that give false passes — excluded from default panels
EXCLUDED = {"phi-4-mini", "phi-3-small", "deepseek-v3.1", "chatglm3-6b", "italia-10b"}

# Default panels — diversity-based (mix model families for independent errors).
# Override with capability_map.json for data-driven routing.
PANELS = {
    # General: 3 different families (Mistral/Meta/Google)
    "general": ["mistral-large", "llama-3.3", "gemma-27b"],
    # Fast: all <1.5s, different families
    "fast": ["llama-3.3", "nemotron-super-49b", "gemma-27b"],
    # Max: 5 models for highest confidence
    "max": ["mistral-large", "llama-3.3", "gemma-27b", "nemotron-super-49b", "kimi-k2"],
    # Arbiter: single tiebreaker
    "arbiter": ["mistral-large"],
}


def get_model(alias: str) -> dict:
    """Look up model by alias. Returns model dict with 'id' key."""
    if alias in MODELS:
        return MODELS[alias]
    for m in MODELS.values():
        if m["id"] == alias:
            return m
    raise KeyError(f"Unknown model: {alias}. Available: {list(MODELS.keys())}")


def get_panel(name: str) -> list[str]:
    """Get a panel by name. Returns list of model aliases."""
    if name in PANELS:
        return PANELS[name]
    raise KeyError(f"Unknown panel: {name}. Available: {list(PANELS.keys())}")


def is_thinking(alias: str) -> bool:
    """Check if a model is a thinking model (needs special handling)."""
    return MODELS.get(alias, {}).get("thinking", False)


def list_models(speed: str = None, family: str = None) -> list[str]:
    """List model aliases, optionally filtered."""
    return [
        alias for alias, m in MODELS.items()
        if (not speed or m.get("speed") == speed)
        and (not family or m.get("family") == family)
    ]
