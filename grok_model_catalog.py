from __future__ import annotations

from typing import Any, Dict, List, Optional

# Catalog of Grok models and published limits/pricing.
# Keep this list ordered as provided by the user request.
GROK_MODEL_CATALOG: List[Dict[str, Any]] = [
    {
        "model": "grok-4-1-fast-reasoning",
        "category": "language",
        "modalities": ["text"],
        "capabilities": ["reasoning"],
        "context_tokens": 2_000_000,
        "rate_limits": {"tpm": 4_000_000, "rpm": 480},
        "pricing": {"unit": "per_million_tokens", "input_usd": 0.20, "output_usd": 0.50},
    },
    {
        "model": "grok-4-1-fast-non-reasoning",
        "category": "language",
        "modalities": ["text"],
        "capabilities": ["non-reasoning"],
        "context_tokens": 2_000_000,
        "rate_limits": {"tpm": 4_000_000, "rpm": 480},
        "pricing": {"unit": "per_million_tokens", "input_usd": 0.20, "output_usd": 0.50},
    },
    {
        "model": "grok-code-fast-1",
        "category": "language",
        "modalities": ["text"],
        "capabilities": ["code"],
        "context_tokens": 256_000,
        "rate_limits": {"tpm": 2_000_000, "rpm": 480},
        "pricing": {"unit": "per_million_tokens", "input_usd": 0.20, "output_usd": 1.50},
    },
    {
        "model": "grok-4-fast-reasoning",
        "category": "language",
        "modalities": ["text"],
        "capabilities": ["reasoning"],
        "context_tokens": 2_000_000,
        "rate_limits": {"tpm": 4_000_000, "rpm": 480},
        "pricing": {"unit": "per_million_tokens", "input_usd": 0.20, "output_usd": 0.50},
    },
    {
        "model": "grok-4-fast-non-reasoning",
        "category": "language",
        "modalities": ["text"],
        "capabilities": ["non-reasoning"],
        "context_tokens": 2_000_000,
        "rate_limits": {"tpm": 4_000_000, "rpm": 480},
        "pricing": {"unit": "per_million_tokens", "input_usd": 0.20, "output_usd": 0.50},
    },
    {
        "model": "grok-4-0709",
        "category": "language",
        "modalities": ["text"],
        "capabilities": ["reasoning"],
        "context_tokens": 256_000,
        "rate_limits": {"tpm": 2_000_000, "rpm": 480},
        "pricing": {"unit": "per_million_tokens", "input_usd": 3.00, "output_usd": 15.00},
    },
    {
        "model": "grok-3-mini",
        "category": "language",
        "modalities": ["text"],
        "capabilities": ["general"],
        "context_tokens": 131_072,
        "rate_limits": {"tpm": None, "rpm": 480},
        "pricing": {"unit": "per_million_tokens", "input_usd": 0.30, "output_usd": 0.50},
    },
    {
        "model": "grok-3",
        "category": "language",
        "modalities": ["text"],
        "capabilities": ["general"],
        "context_tokens": 131_072,
        "rate_limits": {"tpm": None, "rpm": 600},
        "pricing": {"unit": "per_million_tokens", "input_usd": 3.00, "output_usd": 15.00},
    },
    {
        "model": "grok-2-vision-1212",
        "category": "language",
        "modalities": ["text", "vision"],
        "capabilities": ["vision"],
        "context_tokens": 32_768,
        "rate_limits": {"tpm": None, "rpm": 600},
        "pricing": {"unit": "per_million_tokens", "input_usd": 2.00, "output_usd": 10.00},
    },
    {
        "model": "grok-imagine-image-pro",
        "category": "image",
        "modalities": ["image"],
        "capabilities": ["image-generation"],
        "context_tokens": None,
        "rate_limits": {"tpm": None, "rpm": 30},
        "pricing": {"unit": "per_image_output", "price_usd": 0.07},
    },
    {
        "model": "grok-imagine-image",
        "category": "image",
        "modalities": ["image"],
        "capabilities": ["image-generation"],
        "context_tokens": None,
        "rate_limits": {"tpm": None, "rpm": 30},
        "pricing": {"unit": "per_image_output", "price_usd": 0.02},
    },
    {
        "model": "grok-2-image-1212",
        "category": "image",
        "modalities": ["image"],
        "capabilities": ["image-generation"],
        "context_tokens": None,
        "rate_limits": {"tpm": None, "rpm": 300},
        "pricing": {"unit": "per_image_output", "price_usd": 0.07},
    },
    {
        "model": "grok-imagine-video",
        "category": "video",
        "modalities": ["video"],
        "capabilities": ["video-generation"],
        "context_tokens": None,
        "rate_limits": {"tpm": None, "rpm": None},
        "pricing": {"unit": "per_second", "price_usd": None},
    },
]

# Legacy names that are still exposed in existing nodes but not part of the new pricing list.
LEGACY_GROK_MODELS: List[str] = [
    "grok-2-vision-latest",
    "grok-3-latest",
    "grok-beta",
    "grok-4",
]


def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


GROK_MODEL_NAMES: List[str] = [entry["model"] for entry in GROK_MODEL_CATALOG]
ALL_GROK_MODELS: List[str] = _dedupe(GROK_MODEL_NAMES + LEGACY_GROK_MODELS)
