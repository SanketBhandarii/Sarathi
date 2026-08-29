from __future__ import annotations

from app.eligibility.layers import LAYER_LABEL, Layer
from app.eligibility.verdict import BUCKET_LABEL, Bucket
from app.language.phrases import Language, say


def bucket_label(bucket: Bucket, language: Language) -> str:
    if language is Language.ENGLISH:
        return BUCKET_LABEL[bucket]
    return say(f"bucket.{bucket.value}", language)


def layer_label(layer: Layer, language: Language) -> str:
    if language is Language.ENGLISH:
        return LAYER_LABEL[layer]
    return say(f"layer.{layer.value}", language)
