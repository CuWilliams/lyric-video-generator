# Lyric Video Generator

Generate lyric videos with timed text animations from a JSON lyrics file and an audio track. Outputs YouTube-ready 1080p MP4 videos (H.264 video, AAC audio).

## Requirements

- Python 3.10+
- FFmpeg (required by moviepy for video encoding)

## Setup

```bash
# Clone the repo
git clone https://github.com/CuWilliams/lyric-video-generator.git
cd lyric-video-generator

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install as an editable package (installs deps + registers the lyric-video command)
pip install -e .
```

> **Note:** On macOS, use `pip3` instead of `pip` if you are not in a virtual environment.

### FFmpeg

moviepy requires FFmpeg to be installed on your system:

- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt install ffmpeg`
- **Windows:** Download from https://ffmpeg.org/download.html and add to PATH

## Usage

```bash
lyric-video --lyrics examples/sample_lyrics.json \
            --audio path/to/song.mp3 \
            --theme themes/durt_nurs.json \
            --animation fade \
            --output output/video.mp4
```

### Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--lyrics` | Yes | — | Path to lyrics JSON file |
| `--audio` | Yes | — | Path to audio file (mp3, wav, etc.) |
| `--theme` | No | `themes/durt_nurs.json` | Path to theme JSON |
| `--animation` | No | `fade` | Animation style: `fade`, `slide`, or `typewriter` |
| `--output` | No | `output/<title>.mp4` | Output file path |
| `--fps` | No | `30` | Frame rate |
| `--preview` | No | off | Generate only first 30 seconds |

### Examples

```bash
# Quick preview with default settings (first 30 seconds)
lyric-video --lyrics examples/sample_lyrics.json --audio song.mp3 --preview

# Full video with slide animation
lyric-video --lyrics examples/sample_lyrics.json --audio song.mp3 --animation slide

# Custom output path and theme
lyric-video --lyrics my_lyrics.json --audio my_song.wav \
            --theme my_theme.json --output my_video.mp4

# Audio path with spaces (use quotes)
lyric-video --lyrics examples/sample_lyrics.json \
            --audio "/path/to/My Song.mp3"
```

You can also run the CLI directly without installing the package:

```bash
python -m src.cli.main --lyrics examples/sample_lyrics.json --audio song.mp3
```

### Notes

- The `--preview` flag is useful for quickly testing your lyrics/theme before generating a full-length video.
- Generated videos are saved to the `output/` directory by default. This directory is gitignored.
- If lyrics start after 0:00 (e.g. an instrumental intro), the video will show a blank background until the first lyric line.

## Lyrics Format

```json
{
  "title": "Song Title",
  "artist": "Artist Name",
  "lyrics": [
    { "time": 21.53, "text": "First line of lyrics" },
    { "time": 25.01, "text": "Second line" },
    { "time": 30.00, "text": "" }
  ]
}
```

- `time` — when the line appears, in seconds (float)
- `text` — the lyric text to display
- An empty `text` field marks the end of lyrics (used for timing the final line)

See `examples/sample_lyrics.json` for a complete example.

## Animations

- **fade** — text fades in over ~0.3s, holds, then fades out (default)
- **slide** — text slides up from below into center, holds, then slides out upward
- **typewriter** — characters appear one at a time, evenly spaced across the line duration

## Themes

Themes are JSON files that control the visual style. The default theme is `themes/durt_nurs.json`:

```json
{
  "name": "Durt Nurs",
  "background_color": "#1a1a1a",
  "text_color": "#ffffff",
  "font_family": "Arial Bold",
  "font_size": 72,
  "text_position": "center",
  "text_shadow": true,
  "text_shadow_color": "#000000",
  "text_shadow_offset": [3, 3],
  "default_animation": "fade"
}
```

| Property | Description | Default |
|----------|-------------|---------|
| `background_color` | Hex background color | `#1a1a1a` |
| `text_color` | Hex text color | `#ffffff` |
| `font_family` | Font name (falls back to system fonts) | `Arial` |
| `font_size` | Font size in pixels | `72` |
| `text_position` | `top`, `center`, or `bottom` | `center` |
| `text_shadow` | Enable text shadow | `false` |
| `text_shadow_color` | Hex shadow color | `#000000` |
| `text_shadow_offset` | Shadow offset `[x, y]` in pixels | `[3, 3]` |
| `default_animation` | Default animation style | `fade` |

## Project Structure

```
lyric-video-generator/
├── src/
│   ├── core/
│   │   ├── lyrics_parser.py      # lyrics JSON parsing and validation
│   │   ├── text_renderer.py      # text/font rendering with Pillow
│   │   ├── video_generator.py    # main video generation pipeline
│   │   ├── audio_handler.py      # audio file loading
│   │   └── theme_loader.py       # theme JSON loading with defaults
│   ├── animations/
│   │   ├── base.py               # base animation class
│   │   ├── fade.py               # fade in/out
│   │   ├── slide.py              # slide up/down
│   │   └── typewriter.py         # typewriter effect
│   └── cli/
│       └── main.py               # CLI entry point
├── themes/
│   └── durt_nurs.json            # default theme
├── examples/
│   └── sample_lyrics.json        # sample lyrics
├── output/                       # generated videos (gitignored)
├── requirements.txt
└── pyproject.toml
```
