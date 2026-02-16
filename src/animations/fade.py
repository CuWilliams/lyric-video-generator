"""Fade in/out animation."""

from PIL import Image

from src.animations.base import BaseAnimation
from src.core.text_renderer import TextRenderer


class FadeAnimation(BaseAnimation):
    """Text fades in, holds, then fades out."""

    def __init__(self, fade_in_duration: float = 0.3, fade_out_duration: float = 0.3):
        self.fade_in_duration = fade_in_duration
        self.fade_out_duration = fade_out_duration

    def generate_frames(
        self,
        text: str,
        duration: float,
        fps: int,
        renderer: TextRenderer,
    ) -> list[Image.Image]:
        total_frames = max(1, int(duration * fps))
        fade_in_frames = int(self.fade_in_duration * fps)
        fade_out_frames = int(self.fade_out_duration * fps)

        # Ensure fade frames don't exceed total
        if fade_in_frames + fade_out_frames > total_frames:
            fade_in_frames = total_frames // 3
            fade_out_frames = total_frames // 3

        frames = []
        for i in range(total_frames):
            if i < fade_in_frames:
                # Fade in: 0.0 -> 1.0
                alpha = i / fade_in_frames
            elif i >= total_frames - fade_out_frames:
                # Fade out: 1.0 -> 0.0
                remaining = total_frames - 1 - i
                alpha = remaining / fade_out_frames
            else:
                # Hold at full opacity
                alpha = 1.0

            frames.append(renderer.render_frame(text, alpha=alpha))

        return frames
