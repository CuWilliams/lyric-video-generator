"""Text and font rendering with Pillow."""

import textwrap

from PIL import Image, ImageDraw, ImageFont

from src.core.theme_loader import Theme

# Output resolution
WIDTH = 1920
HEIGHT = 1080


class TextRenderer:
    """Renders styled lyric text onto PIL Images using a Theme."""

    def __init__(self, theme: Theme):
        self.theme = theme
        self.font = self._load_font()

    def _load_font(self) -> ImageFont.FreeTypeFont:
        """Load the theme font, falling back to default if unavailable."""
        try:
            return ImageFont.truetype(self.theme.font_family, self.theme.font_size)
        except OSError:
            # Try common system font paths
            for fallback in ("Arial.ttf", "DejaVuSans.ttf", "Helvetica.ttc"):
                try:
                    return ImageFont.truetype(fallback, self.theme.font_size)
                except OSError:
                    continue
            return ImageFont.load_default()

    def render_frame(self, text: str, alpha: float = 1.0) -> Image.Image:
        """Render a single frame with the given text.

        Args:
            text: The lyric text to render.
            alpha: Opacity of the text (0.0 to 1.0), used by animations.

        Returns:
            A 1920x1080 RGBA PIL Image.
        """
        bg_color = self.theme.background_color
        img = Image.new("RGBA", (WIDTH, HEIGHT), bg_color)

        if not text:
            return img

        # Wrap long lines
        wrapped = self._wrap_text(text)

        # Create a transparent overlay for text (supports alpha)
        txt_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_layer)

        # Measure text block
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=self.font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Position
        x, y = self._compute_position(text_w, text_h)

        # Convert alpha to 0-255
        a = int(alpha * 255)

        # Draw shadow if enabled
        if self.theme.text_shadow:
            sx, sy = self.theme.text_shadow_offset
            shadow_color = self._hex_to_rgba(self.theme.text_shadow_color, a)
            draw.multiline_text(
                (x + sx, y + sy), wrapped, font=self.font,
                fill=shadow_color, anchor="mm", align="center",
            )

        # Draw main text
        text_color = self._hex_to_rgba(self.theme.text_color, a)
        draw.multiline_text(
            (x, y), wrapped, font=self.font,
            fill=text_color, anchor="mm", align="center",
        )

        return Image.alpha_composite(img, txt_layer)

    def _wrap_text(self, text: str, max_chars: int = 40) -> str:
        """Wrap text to fit within the frame width."""
        return "\n".join(textwrap.wrap(text, width=max_chars))

    def _compute_position(self, text_w: int, text_h: int) -> tuple[int, int]:
        """Compute text anchor position based on theme setting."""
        pos = self.theme.text_position

        if pos == "top":
            return WIDTH // 2, HEIGHT // 4
        elif pos == "bottom":
            return WIDTH // 2, (HEIGHT * 3) // 4
        else:  # center (default)
            return WIDTH // 2, HEIGHT // 2

    @staticmethod
    def _hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
        """Convert a hex color string to an RGBA tuple."""
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return (r, g, b, alpha)
