"""Base animation class."""

from abc import ABC, abstractmethod

from PIL import Image

from src.core.text_renderer import TextRenderer


class BaseAnimation(ABC):
    """Abstract base class for lyric line animations."""

    @abstractmethod
    def generate_frames(
        self,
        text: str,
        duration: float,
        fps: int,
        renderer: TextRenderer,
    ) -> list[Image.Image]:
        """Generate the sequence of frames for a single lyric line.

        Args:
            text: The lyric text to animate.
            duration: How long this line is displayed, in seconds.
            fps: Frames per second.
            renderer: TextRenderer instance for producing styled frames.

        Returns:
            A list of PIL Images representing each frame.
        """
