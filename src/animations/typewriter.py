"""Typewriter effect animation."""

from PIL import Image

from src.animations.base import BaseAnimation
from src.core.text_renderer import TextRenderer


class TypewriterAnimation(BaseAnimation):
    """Characters appear one at a time, evenly spaced across the line's duration."""

    def generate_frames(
        self,
        text: str,
        duration: float,
        fps: int,
        renderer: TextRenderer,
    ) -> list[Image.Image]:
        total_frames = max(1, int(duration * fps))
        char_count = len(text)

        if char_count == 0:
            return [renderer.render_frame("") for _ in range(total_frames)]

        frames = []
        for i in range(total_frames):
            # How many characters should be visible at this frame
            progress = (i + 1) / total_frames
            visible_chars = int(progress * char_count)
            visible_chars = min(visible_chars, char_count)

            partial_text = text[:visible_chars]
            frames.append(renderer.render_frame(partial_text))

        return frames
