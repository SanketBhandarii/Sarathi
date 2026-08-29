from __future__ import annotations

from functools import lru_cache

from strands.models import BedrockModel, Model
from strands.models.litellm import LiteLLMModel

from app.core.config import get_settings

DEFAULT_MAX_TOKENS = 3500


def _groq(model_id: str, temperature: float, max_tokens: int) -> Model:
    return LiteLLMModel(
        model_id=model_id,
        params={
            "temperature": temperature,
            "max_tokens": max_tokens,
            "reasoning_effort": "low",
        },
    )


def _bedrock(model_id: str, temperature: float, max_tokens: int) -> Model:
    settings = get_settings()
    return BedrockModel(
        model_id=model_id,
        region_name=settings.bedrock_region,
        temperature=temperature,
        max_tokens=max_tokens,
    )


@lru_cache
def fast_model(temperature: float = 0.0, max_tokens: int = DEFAULT_MAX_TOKENS) -> Model:
    settings = get_settings()
    if settings.model_provider == "bedrock":
        return _bedrock(settings.bedrock_fast_model, temperature, max_tokens)
    return _groq(settings.groq_fast_model, temperature, max_tokens)


@lru_cache
def smart_model(temperature: float = 0.0, max_tokens: int = DEFAULT_MAX_TOKENS) -> Model:
    settings = get_settings()
    if settings.model_provider == "bedrock":
        return _bedrock(settings.bedrock_smart_model, temperature, max_tokens)
    return _groq(settings.groq_smart_model, temperature, max_tokens)
