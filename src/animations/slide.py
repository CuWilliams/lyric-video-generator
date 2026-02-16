"""Slide up/down animation."""

from PIL import Image

from src.animations.base import BaseAnimation
from src.core.text_renderer import TextRenderer, HEIGHT


class SlideAnimation(BaseAnimation):
    """Text slides up from below into center, holds, then slides out upward."""

    def __init__(self, slide_in_duration: float = 0.3, slide_out_duration: float = 0.3):
        self.slide_in_duration = slide_in_duration
        self.slide_out_duration = slide_out_duration

    def generate_frames(
        self,
        text: str,
        duration: float,
        fps: int,
        renderer: TextRenderer,
    ) -> list[Image.Image]:
        total_frames = max(1, int(duration * fps))
        slide_in_frames = int(self.slide_in_duration * fps)
        slide_out_frames = int(self.slide_out_duration * fps)

        # Ensure slide frames don't exceed total
        if slide_in_frames + slide_out_frames > total_frames:
            slide_in_frames = total_frames // 3
            slide_out_frames = total_frames // 3

        # Distance to travel: from just below screen to center (0 offset)
        travel = HEIGHT // 2

        frames = []
        for i in range(total_frames):
            if i < slide_in_frames:
                # Slide in from below: large positive y_offset -> 0
                progress = i / slide_in_frames
                y_offset = int(travel * (1.0 - progress))
            elif i >= total_frames - slide_out_frames:
                # Slide out upward: 0 -> large negative y_offset
                progress = (i - (total_frames - slide_out_frames)) / slide_out_frames
                y_offset = int(-travel * progress)
            else:
                # Hold at center
                y_offset = 0

            frames.append(renderer.render_frame(text, y_offset=y_offset))

        return frames
