# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python CLI tool that generates YouTube-ready 1080p lyric videos from a JSON lyrics file and audio track, with configurable text animations and themes. Output is MP4 (libx264/AAC).

## Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -e .

# Run via CLI entry point
lyric-video --lyrics examples/sample_lyrics.json --audio song.mp3

# Run directly
python -m src.cli.main --lyrics examples/sample_lyrics.json --audio song.mp3

# CLI options
lyric-video --lyrics FILE --audio FILE [--theme FILE] [--animation fade|slide|typewriter] [--output PATH] [--fps 30] [--preview]
```

FFmpeg must be installed on the system (required by moviepy).

No test suite or linting is currently configured.

## Architecture

**Pipeline flow:** CLI (`src/cli/main.py`) → `generate_video()` (`src/core/video_generator.py`) → on-demand frame rendering via moviepy's `VideoClip(make_frame)`.

**Core modules** (`src/core/`):
- `video_generator.py` — Main pipeline. Builds frames on-demand with per-line caching (only current line's frames in memory). The `make_frame(t)` closure maps time → lyric line → animation frame.
- `lyrics_parser.py` — Parses lyrics JSON into `LyricLine` dataclass (`text`, `start_time`, `end_time`, `duration`). Empty text `""` marks the end.
- `text_renderer.py` — PIL-based rendering at 1920x1080. Handles font loading (with fallback chain), hex colors, shadows, text alpha blending.
- `audio_handler.py` — Loads audio via moviepy `AudioFileClip`.
- `theme_loader.py` — Loads theme JSON merged with hardcoded defaults.

**Animation system** (`src/animations/`):
- `base.py` — Abstract `BaseAnimation` with `generate_frames(text, duration, fps, renderer) -> list[PIL.Image]`.
- Three implementations: `fade.py`, `slide.py`, `typewriter.py`. Each controls how a single lyric line animates over its duration.

**Data formats:**
- Lyrics: JSON with `title`, `artist`, `lyrics[]` (each entry has `time` in seconds and `text`).
- Themes: JSON with 9 properties (colors, fonts, shadows, animation settings). See `themes/durt_nurs.json`.

## Key Conventions

- moviepy v2.0+ API: use `with_fps()`, `with_audio()`, `VideoClip(frame_function)` — not the deprecated v1 methods.
- Python 3.10+ required. Dependencies: moviepy, Pillow, click, numpy.
- Preview mode renders first 30 seconds only.
- Output directory is `output/` (gitignored).
