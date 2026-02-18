"""Main video generation engine."""

from pathlib import Path

from moviepy import VideoClip

from src.animations.scroll import ScrollingAnimation
from src.core.audio_handler import load_audio
from src.core.lyrics_parser import parse_lyrics
from src.core.text_renderer import TextRenderer
from src.core.theme_loader import load_theme

FPS_DEFAULT = 30


def generate_video(
    lyrics_path: str | Path,
    audio_path: str | Path,
    output_path: str | Path,
    theme_path: str | Path | None = None,
    fps: int = FPS_DEFAULT,
    preview: bool = False,
    background_path: str | Path | None = None,
    lyric_position: str | None = None,
) -> Path:
    """Generate a lyric video from lyrics JSON and an audio file.

    Args:
        lyrics_path: Path to lyrics JSON file.
        audio_path: Path to audio file.
        output_path: Path for the output MP4.
        theme_path: Path to theme JSON (None for default theme).
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
    if lyric_position is not None:
        theme.lyric_position = lyric_position
    renderer = TextRenderer(theme)

    lines = lyrics_data["lines"]
    total_duration = audio.duration
    if preview:
        total_duration = min(total_duration, 30.0)
        lines = [line for line in lines if line.start_time < total_duration]

    print(f"Generating video: {lyrics_data['title']} by {lyrics_data['artist']}")
    print(f"FPS: {fps} | Duration: {total_duration:.1f}s | Lyric lines: {len(lines)}")

    # Build scrolling animation over all lines
    animation = ScrollingAnimation(
        lines=lines,
        fps=fps,
        line_height=theme.line_height,
        inactive_alphas=theme.inactive_alphas,
    )

    def make_frame(t: float):
        return animation.make_frame(t, renderer)

    # Build video clip
    video = VideoClip(frame_function=make_frame, duration=total_duration)
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
