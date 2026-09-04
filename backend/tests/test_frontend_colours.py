from __future__ import annotations

import re
from pathlib import Path

import pytest

FRONTEND = Path(__file__).resolve().parents[2] / "frontend" / "src"
STYLES = FRONTEND / "app" / "globals.css"

DEFINED = re.compile(r"--color-([a-z0-9-]+)\s*:")
USED = re.compile(r"\b(?:bg|text|border|from|to|ring|fill|stroke)-([a-z][a-z0-9-]*)\b")

BUILT_IN = {
    "white", "black", "transparent", "current", "inherit", "none", "auto",
    "left", "right", "center", "justify", "start", "end", "wrap", "nowrap",
    "clip", "ellipsis", "balance", "pretty", "solid", "dashed", "dotted",
    "hidden", "collapse", "separate", "b", "t", "l", "r", "x", "y", "s", "e",
    "0", "1", "2", "4", "8", "px", "full", "screen", "min", "max", "fit",
}


def _defined_colours() -> set[str]:
    return set(DEFINED.findall(STYLES.read_text(encoding="utf-8")))


def _source_files() -> list[Path]:
    return sorted(FRONTEND.rglob("*.tsx"))


@pytest.mark.skipif(not STYLES.exists(), reason="frontend styles are not present")
def test_every_colour_class_the_pages_use_is_actually_defined():
    defined = _defined_colours()
    unknown: dict[str, set[str]] = {}

    for path in _source_files():
        text = path.read_text(encoding="utf-8")
        for name in USED.findall(text):
            if name in defined or name in BUILT_IN:
                continue
            if any(name.startswith(f"{known}-") for known in defined):
                continue
            unknown.setdefault(str(path.relative_to(FRONTEND)), set()).add(name)

    assert not unknown, (
        "these colour names are used in the pages but never defined in globals.css, "
        "so they paint nothing and can make text invisible: "
        + "; ".join(f"{where}: {sorted(names)}" for where, names in sorted(unknown.items()))
    )


@pytest.mark.skipif(not STYLES.exists(), reason="frontend styles are not present")
def test_a_white_label_is_never_put_on_an_undefined_background():
    defined = _defined_colours()
    offenders: list[str] = []

    for path in _source_files():
        for line in path.read_text(encoding="utf-8").splitlines():
            if "text-white" not in line:
                continue
            backgrounds = re.findall(r"\bbg-([a-z][a-z0-9-]*)\b", line)
            for name in backgrounds:
                base = name.split("-")[0]
                if name in defined or base in defined or name in BUILT_IN:
                    continue
                offenders.append(f"{path.relative_to(FRONTEND)}: bg-{name} with text-white")

    assert not offenders, "white text on a background that paints nothing: " + "; ".join(offenders)
