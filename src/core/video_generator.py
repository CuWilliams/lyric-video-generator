"""Main video generation engine."""

import sys
from pathlib import Path

import numpy as np
from moviepy.editor import AudioFileClip, VideoClip

from src.animations.base import BaseAnimation
from src.animations.fade import FadeAnimation
from src.animations.slide import SlideAnimation
from src.animations.typewriter import TypewriterAnimation
from src.core.audio_handler import load_audio
from src.core.lyrics_parser import LyricLine, parse_lyrics
from src.core.text_renderer import TextRenderer
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

    # Pre-render all frames for each lyric line
    print(f"Generating video: {lyrics_data['title']} by {lyrics_data['artist']}")
    print(f"Animation: {animation_name} | FPS: {fps} | Duration: {total_duration:.1f}s")

    line_frames = _prerender_lines(lines, animation, fps, renderer, total_duration)

    # Build a blank background frame (as numpy array) for gaps
    blank_frame = np.array(renderer.render_frame("").convert("RGB"))

    # Create frame lookup: for each line, store (start_time, end_time, frames)
    frame_lookup = []
    for line, frames in zip(lines, line_frames):
        end_time = min(line.end_time, total_duration) if preview else line.end_time
        frame_lookup.append((line.start_time, end_time, frames))

    def make_frame(t: float) -> np.ndarray:
        """Return the video frame at time t."""
        for start, end, frames in frame_lookup:
            if start <= t < end:
                # Map t to a frame index within this line's frames
                progress = (t - start) / (end - start)
                idx = min(int(progress * len(frames)), len(frames) - 1)
                return np.array(frames[idx].convert("RGB"))
        return blank_frame

    # Build video clip
    video = VideoClip(make_frame, duration=total_duration)
    video = video.set_fps(fps)
    video = video.set_audio(audio.subclip(0, total_duration))

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


def _prerender_lines(
    lines: list[LyricLine],
    animation: BaseAnimation,
    fps: int,
    renderer: TextRenderer,
    total_duration: float,
) -> list[list]:
    """Pre-render animated frames for each lyric line with progress output."""
    total_lines = len(lines)
    all_frames = []

    for i, line in enumerate(lines):
        duration = min(line.duration, total_duration - line.start_time)
        if duration <= 0:
            all_frames.append([])
            continue

        frames = animation.generate_frames(line.text, duration, fps, renderer)
        all_frames.append(frames)

        pct = int((i + 1) / total_lines * 100)
        sys.stdout.write(f"\rPre-rendering lines: {pct}% ({i + 1}/{total_lines})")
        sys.stdout.flush()

    print()  # newline after progress
    return all_frames
