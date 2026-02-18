"""Continuous scrolling lyric animation engine."""

from dataclasses import dataclass

import numpy as np

WIDTH = 1920
HEIGHT = 1080

# Max duration (seconds) of the scroll transition between lines.
TRANSITION_DURATION = 0.5


@dataclass
class LineRenderInfo:
    text: str
    screen_y: float   # center y position on screen in pixels
    alpha: float      # 0.0 – 1.0
    is_active: bool


class ScrollingAnimation:
    """Renders all lyric lines as a continuous scrolling stream.

    Virtual space: line i sits at y = i * line_height.  The view window
    scrolls so the active line is always centered.  Transitions between
    lines are smoothed; long instrumental gaps hold the view in place until
    the next line approaches.
    """

    def __init__(self, lines, fps: int, line_height: int = 120,
                 inactive_alphas: list | None = None):
        self.lines = lines
        self.fps = fps
        self.line_height = line_height
        # Opacity by distance from active line: [1 away, 2 away, 3 away]
        self.inactive_alphas = inactive_alphas or [0.6, 0.4, 0.2]
        self._transitions = self._compute_transitions()

    # ------------------------------------------------------------------
    # Pre-computation
    # ------------------------------------------------------------------

    def _compute_transitions(self) -> list[tuple[float, float, int, int]]:
        """Build (t_start, t_end, from_idx, to_idx) for each line change."""
        result = []
        for i in range(len(self.lines) - 1):
            end_t = self.lines[i].end_time
            start_t = self.lines[i + 1].start_time
            gap = start_t - end_t

            if gap <= 0:
                # Overlapping or adjacent — snap instantly at start_t
                t_start = start_t
                t_end = start_t
            elif gap <= TRANSITION_DURATION:
                # Short gap — animate over the entire gap
                t_start = end_t
                t_end = start_t
            else:
                # Long gap (instrumental break) — hold, then animate in the
                # last TRANSITION_DURATION seconds before the next line
                t_start = start_t - TRANSITION_DURATION
                t_end = start_t

            result.append((t_start, t_end, i, i + 1))
        return result

    # ------------------------------------------------------------------
    # Per-frame queries
    # ------------------------------------------------------------------

    def _find_active_idx(self, t: float) -> int:
        """Return index of the currently sung line, or last sung line."""
        last_idx = -1
        for i, line in enumerate(self.lines):
            if line.start_time <= t:
                last_idx = i
            if line.start_time <= t < line.end_time:
                return i
        return last_idx

    def _compute_scroll_pos(self, t: float) -> float:
        """Virtual y coordinate that should be centered on screen at time t."""
        for t_start, t_end, from_idx, to_idx in self._transitions:
            if t_start <= t <= t_end:
                if t_end == t_start:
                    return to_idx * self.line_height
                raw = (t - t_start) / (t_end - t_start)
                # Smooth ease-in-out (smoothstep)
                eased = raw * raw * (3.0 - 2.0 * raw)
                return from_idx * self.line_height + eased * self.line_height

        active_idx = self._find_active_idx(t)
        if active_idx < 0:
            return 0.0
        return active_idx * self.line_height

    def get_visible_lines(self, t: float) -> list[LineRenderInfo]:
        """Return render info for every line visible at time t."""
        scroll_pos = self._compute_scroll_pos(t)
        active_idx = self._find_active_idx(t)
        center_y = HEIGHT / 2.0

        opacity_by_distance = [1.0] + list(self.inactive_alphas)

        visible: list[LineRenderInfo] = []
        for i, line in enumerate(self.lines):
            screen_y = (i * self.line_height) - scroll_pos + center_y
            if screen_y < -self.line_height or screen_y > HEIGHT + self.line_height:
                continue

            distance = abs(i - active_idx) if active_idx >= 0 else len(opacity_by_distance)
            if distance >= len(opacity_by_distance):
                continue

            visible.append(LineRenderInfo(
                text=line.text,
                screen_y=screen_y,
                alpha=opacity_by_distance[distance],
                is_active=(i == active_idx),
            ))

        return visible

    def make_frame(self, t: float, renderer) -> np.ndarray:
        """Return a HxWx3 uint8 numpy array for time t."""
        lines_data = [
            {
                "text": li.text,
                "screen_y": li.screen_y,
                "alpha": li.alpha,
                "is_active": li.is_active,
            }
            for li in self.get_visible_lines(t)
        ]
        img = renderer.render_scroll_frame(lines_data)
        return np.array(img.convert("RGB"), dtype=np.uint8)
