"""SportSync providers."""
from __future__ import annotations

from .base import SportProvider, SportEvent
from .tvsporten import TVSportenProvider
from .tvmatchen import TVMatchenProvider

# All available providers
PROVIDERS: list[type[SportProvider]] = [
    TVSportenProvider,
    TVMatchenProvider,
]

__all__ = [
    "SportProvider",
    "SportEvent",
    "TVSportenProvider",
    "TVMatchenProvider",
    "PROVIDERS",
]
