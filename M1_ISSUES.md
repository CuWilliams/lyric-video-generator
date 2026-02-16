# Lyric Video Generator — M1 GitHub Issues

Use these with Claude Code to create the repo and issues.
You can run: `claude "read ISSUES.md and create a new GitHub repo called lyric-video-generator, then create each issue as a GitHub issue with the appropriate labels"`

---

## Issue #1: Project setup and repo scaffolding

**Labels:** setup, M1

Initialize the `lyric-video-generator` Python project with the following structure:

```
lyric-video-generator/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── video_generator.py    # main video generation engine
│   │   ├── text_renderer.py      # text/font rendering with Pillow
│   │   └── audio_handler.py      # audio file loading
│   ├── animations/
│   │   ├── __init__.py
│   │   ├── base.py               # base animation class
│   │   ├── fade.py               # fade in/out
│   │   ├── slide.py              # slide up/down
│   │   └── typewriter.py         # typewriter effect
│   └── cli/
│       ├── __init__.py
│       └── main.py               # CLI entry point
├── themes/
│   └── durt_nurs.json            # default Durt Nurs theme (colors, fonts)
├── input/
│   └── lyrics/
│       └── disciples-of-dysfunction.json  # sample lyrics file
├── output/                       # generated videos go here (gitignored)
├── requirements.txt              # moviepy, Pillow, click
├── README.md
├── .gitignore
└── pyproject.toml
```

Dependencies: `moviepy`, `Pillow`, `click` (for CLI), `numpy`

Include the sample lyrics JSON (now at `input/lyrics/disciples-of-dysfunction.json`).

---

## Issue #2: Define lyrics JSON schema and parser

**Labels:** core, M1

Create a lyrics parser that loads and validates the JSON lyrics format:

```json
{
  "title": "Song Title",
  "artist": "Artist Name",
  "lyrics": [
    { "time": 21.53, "text": "First line of lyrics" },
    { "time": 25.01, "text": "Second line" }
  ]
}
```

Requirements:
- Load JSON file and validate structure
- `time` is in seconds (float), `text` is the lyric line
- Calculate duration for each line (time until next line starts)
- Handle the final line (empty text = end marker)
- Return a list of LyricLine objects with: text, start_time, end_time, duration
- Raise clear errors for malformed input

---

## Issue #3: Text renderer with Pillow

**Labels:** core, M1

Create a text renderer that generates frames with styled text on a background.

Requirements:
- Render a single lyric line as a PIL Image (1920x1080)
- Support configurable: font family, font size, text color, background color, text position (center default)
- Handle text wrapping for long lines
- Load theme settings from a JSON theme file
- Default Durt Nurs theme: dark background (#1a1a1a), bold white text, large font

The renderer should produce individual frames that the animation system can use.

---

## Issue #4: Base animation class and fade animation

**Labels:** animation, M1

Create the animation system:

**Base class (`animations/base.py`):**
- Abstract base class with method: `generate_frames(text, duration, fps, renderer) -> list of PIL Images`
- Takes a LyricLine and produces the sequence of frames for that line's duration

**Fade animation (`animations/fade.py`):**
- Text fades in over ~0.3s, holds, fades out over ~0.3s
- Configurable fade duration
- This is the default animation style

---

## Issue #5: Slide-up and typewriter animations

**Labels:** animation, M1

**Slide-up (`animations/slide.py`):**
- Text slides up from below frame into center position
- Slide-in over ~0.3s, hold, slide-out upward over ~0.3s

**Typewriter (`animations/typewriter.py`):**
- Characters appear one at a time, evenly spaced across the line's duration
- Cursor blink optional

---

## Issue #6: Video generator engine

**Labels:** core, M1

Create the main video generation pipeline that ties everything together.

Requirements:
- Takes: lyrics JSON path, audio file path, theme path, animation style, output path
- Parses lyrics into timed lines
- For each lyric line, generates animated frames using the selected animation
- For gaps between lines (instrumental sections), generates blank/background frames
- Composites all frames into a video with moviepy
- Overlays the audio track
- Exports as 1080p MP4 (H.264 video, AAC audio)
- Show progress during generation (print percentage or progress bar)
- Target: 30 FPS

---

## Issue #7: CLI interface

**Labels:** cli, M1

Create a CLI using `click`:

```bash
lyric-video --lyrics input/lyrics/disciples-of-dysfunction.json \
            --audio path/to/song.mp3 \
            --theme themes/durt_nurs.json \
            --animation fade \
            --output output/video.mp4
```

Options:
- `--lyrics` (required): path to lyrics JSON
- `--audio` (required): path to audio file
- `--theme` (optional): path to theme JSON, defaults to durt_nurs
- `--animation` (optional): fade|slide|typewriter, defaults to fade
- `--output` (optional): output path, defaults to `output/<title>.mp4`
- `--fps` (optional): frame rate, defaults to 30
- `--preview` (optional flag): generate only first 30 seconds for quick preview

---

## Issue #8: Durt Nurs default theme

**Labels:** theme, M1

Create the default theme file `themes/durt_nurs.json`:

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

The theme loader should support all these properties with sensible fallbacks.
