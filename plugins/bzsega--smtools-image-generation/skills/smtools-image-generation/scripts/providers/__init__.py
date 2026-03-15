from providers.base_provider import BaseImageProvider
from providers.openrouter_provider import OpenRouterProvider
from providers.kie_provider import KieProvider

PROVIDERS = {
    "openrouter": OpenRouterProvider,
    "kie": KieProvider,
}


def get_provider(name: str) -> type:
    provider_cls = PROVIDERS.get(name)
    if provider_cls is None:
        raise ValueError(
            f"Unknown provider: {name}. Available: {', '.join(PROVIDERS.keys())}"
        )
    return provider_cls
