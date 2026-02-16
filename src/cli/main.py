"""CLI entry point for lyric-video-generator."""

from pathlib import Path

import click

from src.core.video_generator import generate_video

DEFAULT_THEME = Path(__file__).resolve().parent.parent.parent / "themes" / "durt_nurs.json"


@click.command()
@click.option("--lyrics", required=True, type=click.Path(exists=True), help="Path to lyrics JSON file.")
@click.option("--audio", required=True, type=click.Path(exists=True), help="Path to audio file.")
@click.option("--theme", type=click.Path(exists=True), default=None, help="Path to theme JSON (default: durt_nurs).")
@click.option("--animation", type=click.Choice(["fade", "slide", "typewriter"]), default="fade", help="Animation style.")
@click.option("--output", type=click.Path(), default=None, help="Output path (default: output/<title>.mp4).")
@click.option("--fps", type=int, default=30, help="Frame rate (default: 30).")
@click.option("--preview", is_flag=True, default=False, help="Generate only first 30 seconds.")
def cli(lyrics, audio, theme, animation, output, fps, preview):
    """Generate a lyric video from a lyrics JSON file and an audio track."""
    theme_path = theme if theme else str(DEFAULT_THEME)

    if output is None:
        # Derive output name from lyrics title
        from src.core.lyrics_parser import parse_lyrics
        data = parse_lyrics(lyrics)
        title = data["title"].replace(" ", "_")
        output = str(Path("output") / f"{title}.mp4")

    generate_video(
        lyrics_path=lyrics,
        audio_path=audio,
        output_path=output,
        theme_path=theme_path,
        animation_name=animation,
        fps=fps,
        preview=preview,
    )


if __name__ == "__main__":
    cli()
