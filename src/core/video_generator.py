"""Main video generation engine."""

import sys
from pathlib import Path

import numpy as np
from moviepy import AudioFileClip, VideoClip

from src.animations.base import BaseAnimation
from src.animations.fade import FadeAnimation
from src.animations.slide import SlideAnimation
from src.animations.typewriter import TypewriterAnimation
from src.core.audio_handler import load_audio
from src.core.lyrics_parser import LyricLine, parse_lyrics
from src.core.text_renderer import TextRenderer, WIDTH, HEIGHT
from src.core.theme_loader import load_theme

ANIMATIONS = {
    "fade": FadeAnimation,
    "slide": SlideAnimation,
    "typewriter": TypewriterAnimation,
}

FPS_DEFAULT = 30


def generate_video(
    lyrics_path: str | Path,
    audio_path: str | Path,
    output_path: str | Path,
    theme_path: str | Path | None = None,
    animation_name: str = "fade",
    fps: int = FPS_DEFAULT,
    preview: bool = False,
    background_path: str | Path | None = None,
) -> Path:
    """Generate a lyric video from lyrics JSON and an audio file.

    Args:
        lyrics_path: Path to lyrics JSON file.
        audio_path: Path to audio file.
        output_path: Path for the output MP4.
        theme_path: Path to theme JSON (None for default theme).
        animation_name: One of 'fade', 'slide', 'typewriter'.
        fps: Frames per second (default 30).
        preview: If True, only generate the first 30 seconds.
        background_path: Path to background video (None for solid color).

    Returns:
        The output file path.
    """
    # Load inputs
    lyrics_data = parse_lyrics(lyrics_path)
    audio = load_audio(audio_path)
    theme = load_theme(theme_path)
    renderer = TextRenderer(theme)

    if animation_name not in ANIMATIONS:
        raise ValueError(f"Unknown animation '{animation_name}'. Choose from: {', '.join(ANIMATIONS)}")
    animation = ANIMATIONS[animation_name]()

    lines = lyrics_data["lines"]
    total_duration = audio.duration
    if preview:
        total_duration = min(total_duration, 30.0)
        lines = [l for l in lines if l.start_time < total_duration]

    print(f"Generating video: {lyrics_data['title']} by {lyrics_data['artist']}")
    print(f"Animation: {animation_name} | FPS: {fps} | Duration: {total_duration:.1f}s")
    print(f"Lyric lines: {len(lines)}")

    # Build line timing lookup (no pre-rendering — frames generated on demand)
    line_lookup = []
    for line in lines:
        end_time = min(line.end_time, total_duration) if preview else line.end_time
        duration = end_time - line.start_time
        if duration > 0:
            line_lookup.append((line.start_time, end_time, duration, line.text))

    # Blank background frame for instrumental gaps
    blank_frame = np.array(renderer.render_frame("").convert("RGB"), dtype=np.uint8)

    # Cache: store frames for the current line only to avoid re-rendering
    cache = {"line_idx": -1, "frames": []}

    def make_frame(t: float) -> np.ndarray:
        """Render the video frame at time t on demand."""
        for i, (start, end, duration, text) in enumerate(line_lookup):
            if start <= t < end:
                # Render this line's frames on first access, cache for reuse
                if cache["line_idx"] != i:
                    pil_frames = animation.generate_frames(text, duration, fps, renderer)
                    cache["frames"] = [
                        np.array(f.convert("RGB"), dtype=np.uint8) for f in pil_frames
                    ]
                    cache["line_idx"] = i

                frames = cache["frames"]
                if len(frames) > 0:
                    progress = (t - start) / (end - start)
                    idx = min(int(progress * len(frames)), len(frames) - 1)
                    return frames[idx]
        return blank_frame

    # Build video clip
    video = VideoClip(
        frame_function=make_frame,
        duration=total_duration,
    )
    video = video.with_fps(fps)
    video = video.with_audio(audio.subclipped(0, total_duration))

    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Export
    print(f"Exporting to {output_path}...")
    video.write_videofile(
        str(output_path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        logger="bar",
    )

    print(f"Done! Video saved to {output_path}")
    return output_path
