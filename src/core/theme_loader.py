"""Theme loading and defaults."""

import json
from dataclasses import dataclass, field
from pathlib import Path

DEFAULTS = {
    "name": "Default",
    "background_color": "#1a1a1a",
    "text_color": "#ffffff",
    "font_family": "Arial",
    "font_size": 72,
    "text_position": "center",
    "lyric_position": "center",
    "text_shadow": False,
    "text_shadow_color": "#000000",
    "text_shadow_offset": [3, 3],
    "line_height": 120,
    "glow_enabled": True,
    "inactive_alphas": [0.6, 0.4, 0.2],
    "highlight_mode": "line",
    "highlight_dim_alpha": 0.3,
}


@dataclass
class Theme:
    """Resolved theme settings."""
    name: str
    background_color: str
    text_color: str
    font_family: str
    font_size: int
    text_position: str
    text_shadow: bool
    text_shadow_color: str
    lyric_position: str = "center"
    text_shadow_offset: list[int] = field(default_factory=lambda: [3, 3])
    line_height: int = 120
    glow_enabled: bool = True
    inactive_alphas: list[float] = field(default_factory=lambda: [0.6, 0.4, 0.2])
    highlight_mode: str = "line"
    highlight_dim_alpha: float = 0.3


def load_theme(filepath: str | Path | None = None) -> Theme:
    """Load a theme JSON file with fallbacks to defaults.

    Args:
        filepath: Path to theme JSON. If None, returns the default theme.

    Returns:
        A Theme instance with all properties resolved.
    """
    if filepath is None:
        return Theme(**DEFAULTS)

    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Theme file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    merged = {**DEFAULTS, **data}
    return Theme(
        name=merged["name"],
        background_color=merged["background_color"],
        text_color=merged["text_color"],
        font_family=merged["font_family"],
        font_size=merged["font_size"],
        text_position=merged["text_position"],
        lyric_position=merged["lyric_position"],
        text_shadow=merged["text_shadow"],
        text_shadow_color=merged["text_shadow_color"],
        text_shadow_offset=merged["text_shadow_offset"],
        line_height=merged["line_height"],
        glow_enabled=merged["glow_enabled"],
        inactive_alphas=merged["inactive_alphas"],
        highlight_mode=merged["highlight_mode"],
        highlight_dim_alpha=merged["highlight_dim_alpha"],
    )
