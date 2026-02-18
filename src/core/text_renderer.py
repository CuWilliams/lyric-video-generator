"""Text and font rendering with Pillow."""

import textwrap

from PIL import Image, ImageDraw, ImageFont

from src.core.theme_loader import Theme

# Output resolution
WIDTH = 1920
HEIGHT = 1080

# Horizontal column layout
COLUMN_PADDING = 40  # px inset from screen edge for left/right positions


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

    def render_frame(self, text: str, alpha: float = 1.0, y_offset: int = 0) -> Image.Image:
        """Render a single frame with the given text.

        Args:
            text: The lyric text to render.
            alpha: Opacity of the text (0.0 to 1.0), used by animations.
            y_offset: Vertical pixel offset from the base position (for slide animations).

        Returns:
            A 1920x1080 RGBA PIL Image.
        """
        bg_color = self.theme.background_color
        img = Image.new("RGBA", (WIDTH, HEIGHT), bg_color)

        if not text:
            return img

        x_h, anchor, align, max_chars = self._get_horizontal_layout()

        # Wrap long lines
        wrapped = self._wrap_text(text, max_chars)

        # Create a transparent overlay for text (supports alpha)
        txt_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_layer)

        # Vertical position
        x = x_h
        y = self._compute_vertical_position()
        y += y_offset

        # Convert alpha to 0-255
        a = int(alpha * 255)

        # Draw shadow if enabled
        if self.theme.text_shadow:
            sx, sy = self.theme.text_shadow_offset
            shadow_color = self._hex_to_rgba(self.theme.text_shadow_color, a)
            draw.multiline_text(
                (x + sx, y + sy), wrapped, font=self.font,
                fill=shadow_color, anchor=anchor, align=align,
            )

        # Draw main text
        text_color = self._hex_to_rgba(self.theme.text_color, a)
        draw.multiline_text(
            (x, y), wrapped, font=self.font,
            fill=text_color, anchor=anchor, align=align,
        )

        return Image.alpha_composite(img, txt_layer)

    def render_scroll_frame(self, lines_data: list[dict]) -> Image.Image:
        """Render multiple lyric lines for the scrolling view.

        Args:
            lines_data: List of dicts with keys:
                - 'text': str
                - 'screen_y': float  (center y position on screen)
                - 'alpha': float     (0.0 – 1.0)
                - 'is_active': bool

        Returns:
            A 1920x1080 RGBA PIL Image.
        """
        img = Image.new("RGBA", (WIDTH, HEIGHT), self.theme.background_color)

        x, anchor, align, max_chars = self._get_horizontal_layout()

        for line_data in lines_data:
            text = line_data.get("text", "")
            if not text:
                continue

            screen_y = line_data["screen_y"]
            alpha = line_data["alpha"]
            is_active = line_data.get("is_active", False)

            wrapped = self._wrap_text(text, max_chars)
            a = int(alpha * 255)
            y = int(screen_y)

            txt_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            draw = ImageDraw.Draw(txt_layer)

            # Soft glow for active line
            if is_active and getattr(self.theme, "glow_enabled", True):
                glow_a = int(alpha * 38)  # ~15% opacity
                glow_color = self._hex_to_rgba(self.theme.text_color, glow_a)
                for dx, dy in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
                    draw.multiline_text(
                        (x + dx, y + dy), wrapped, font=self.font,
                        fill=glow_color, anchor=anchor, align=align,
                    )

            # Shadow
            if self.theme.text_shadow:
                sx, sy = self.theme.text_shadow_offset
                shadow_color = self._hex_to_rgba(self.theme.text_shadow_color, a)
                draw.multiline_text(
                    (x + sx, y + sy), wrapped, font=self.font,
                    fill=shadow_color, anchor=anchor, align=align,
                )

            # Main text
            text_color = self._hex_to_rgba(self.theme.text_color, a)
            draw.multiline_text(
                (x, y), wrapped, font=self.font,
                fill=text_color, anchor=anchor, align=align,
            )

            img = Image.alpha_composite(img, txt_layer)

        return img

    def _get_horizontal_layout(self) -> tuple[int, str, str, int]:
        """Return (x, anchor, align, max_chars) based on theme lyric_position."""
        pos = getattr(self.theme, "lyric_position", "center")
        if pos == "left":
            return COLUMN_PADDING, "lm", "left", 20
        elif pos == "right":
            return WIDTH - COLUMN_PADDING, "rm", "right", 20
        else:  # center (default)
            return WIDTH // 2, "mm", "center", 40

    def _wrap_text(self, text: str, max_chars: int = 40) -> str:
        """Wrap text to fit within the frame width."""
        return "\n".join(textwrap.wrap(text, width=max_chars))

    def _compute_vertical_position(self) -> int:
        """Return the vertical anchor y based on theme text_position."""
        pos = self.theme.text_position
        if pos == "top":
            return HEIGHT // 4
        elif pos == "bottom":
            return (HEIGHT * 3) // 4
        else:  # center (default)
            return HEIGHT // 2

    @staticmethod
    def _hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
        """Convert a hex color string to an RGBA tuple."""
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return (r, g, b, alpha)
