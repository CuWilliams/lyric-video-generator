"""CLI entry point for lyric-video-generator."""

from pathlib import Path

import click

from src.core.song_resolver import resolve_song
from src.core.video_generator import generate_video

DEFAULT_THEME = Path(__file__).resolve().parent.parent.parent / "themes" / "durt_nurs.json"


@click.command()
@click.option("--song", default=None, help="Song name to auto-match from input/ folders.")
@click.option("--lyrics", default=None, type=click.Path(exists=True), help="Path to lyrics JSON file.")
@click.option("--audio", default=None, type=click.Path(exists=True), help="Path to audio file.")
@click.option("--background", default=None, type=click.Path(exists=True), help="Path to background video.")
@click.option("--no-background", is_flag=True, default=False, help="Force solid color background.")
@click.option("--theme", type=click.Path(exists=True), default=None, help="Path to theme JSON (default: durt_nurs).")
@click.option("--output", type=click.Path(), default=None, help="Output path (default: output/<title>.mp4).")
@click.option("--fps", type=int, default=30, help="Frame rate (default: 30).")
@click.option("--preview", is_flag=True, default=False, help="Generate only first 30 seconds.")
@click.option(
    "--lyric-position",
    type=click.Choice(["left", "center", "right"]),
    default=None,
    help="Horizontal lyric position: left, center, or right (overrides theme).",
)
def cli(song, lyrics, audio, background, no_background, theme, output, fps, preview, lyric_position):
    """Generate a lyric video from a lyrics JSON file and an audio track."""
    # Resolve input paths
    if song:
        resolved = resolve_song(
            song_name=song,
            lyrics_override=lyrics,
            audio_override=audio,
            background_override=background,
            no_background=no_background,
        )
        lyrics = str(resolved["lyrics"])
        audio = str(resolved["audio"])
        background_path = resolved["background"]
    elif lyrics and audio:
        background_path = Path(background) if background else None
    else:
        raise click.UsageError(
            "Provide either --song <name> or both --lyrics and --audio.\n"
            "  Auto-match: lyric-video --song my_song\n"
            "  Explicit:   lyric-video --lyrics path/to/lyrics.json --audio path/to/audio.mp3"
        )

    if no_background:
        background_path = None

    theme_path = theme if theme else str(DEFAULT_THEME)

    if output is None:
        if song:
            output = str(Path("output") / f"{song}.mp4")
        else:
            from src.core.lyrics_parser import parse_lyrics
            data = parse_lyrics(lyrics)
            title = data["title"].replace(" ", "_")
            output = str(Path("output") / f"{title}.mp4")

    generate_video(
        lyrics_path=lyrics,
        audio_path=audio,
        output_path=output,
        theme_path=theme_path,
        fps=fps,
        preview=preview,
        background_path=background_path,
        lyric_position=lyric_position,
    )


if __name__ == "__main__":
    cli()
