# Lyric Video Generator — M2 GitHub Issues

Use these with Claude Code to create issues:
`claude "read M2_ISSUES.md and create each issue as a GitHub issue on lyric-video-generator with the appropriate labels"`

---

## Issue #9: Restructure input/output folders and auto-matching

**Labels:** setup, M2

Add a defined folder structure for input feedstock and update the CLI to auto-discover matching files by filename.

**Folder structure:**
```
lyric-video-generator/
├── input/
│   ├── audio/          # MP3/WAV song files
│   ├── lyrics/         # lyrics JSON files
│   └── backgrounds/    # looping MP4 background videos
├── output/             # generated lyric videos
```

**Auto-matching logic:**
- Given a song name (e.g. `disciples_of_dysfunction`), the tool looks for:
  - `input/audio/disciples_of_dysfunction.mp3` (or .wav)
  - `input/lyrics/disciples_of_dysfunction.json`
  - `input/backgrounds/disciples_of_dysfunction.mp4` (optional)
- CLI accepts just `--song <name>` and resolves all paths automatically
- Clear error messages if required files (audio, lyrics) are missing
- Background is optional — falls back to solid color if not found

**Gitignore:**
- Gitignore contents of `input/audio/`, `input/lyrics/`, `input/backgrounds/`, and `output/`
- Keep the folder structure via `.gitkeep` files
- Move the existing `examples/sample_lyrics.json` into `examples/` (keep as reference, separate from working input)

**Updated CLI usage:**
```bash
# Auto-match mode
lyric-video --song disciples_of_dysfunction

# Still allow explicit overrides
lyric-video --song disciples_of_dysfunction --background /path/to/custom_bg.mp4
```

---

## Issue #10: Remove M1 animation system, create scrolling lyric engine

**Labels:** core, M2

Replace the M1 per-line animation system (fade, slide, typewriter) with a continuous scrolling lyric renderer.

**Remove:**
- `src/animations/fade.py`
- `src/animations/slide.py`
- `src/animations/typewriter.py`
- `src/animations/base.py` (replace with new scrolling base)
- Remove `--animation` CLI flag

**Scrolling behavior:**
- All lyrics scroll vertically through the frame as a continuous stream
- At any given moment, up to 7 lines are visible: 3 upcoming lines below the active line, the active line in the center region, and 3 past lines above
- Scrolling is smooth and continuous — lines glide upward between positions
- Scroll speed is driven by timestamps: each line reaches the active/center position at its timestamp
- New lines enter from the bottom of the visible area; old lines exit off the top

**Active line highlighting:**
- The currently sung line is visually distinct: brighter color, bold weight, and/or glow effect (driven by theme settings)
- Non-active lines are dimmed — opacity decreases with distance from the active line (e.g. adjacent lines at 60% opacity, next at 40%, furthest at 20%)

**Instrumental breaks:**
- When there is a gap between lyric lines (no upcoming lyrics), hold the last sung line in its current position
- Do not scroll to empty space — the scroller pauses until the next lyric's timestamp approaches, then resumes scrolling

**Line spacing:**
- Even vertical spacing between lines
- Configurable line height in theme

---

## Issue #11: Horizontal lyric positioning (left/center/right)

**Labels:** core, M2

Add configurable horizontal positioning for the lyrics scroll column.

**Three positions:**
- `left` — lyrics aligned to the left 1/3 of the screen
- `center` — lyrics centered horizontally (default)
- `right` — lyrics aligned to the right 1/3 of the screen

**Requirements:**
- Text alignment follows the position (left-aligned text for left position, centered for center, right-aligned for right)
- The lyrics column occupies roughly 1/3 of the screen width in all positions, leaving 2/3 clear for background visibility
- Configurable via CLI: `--lyric-position left|center|right`
- Also settable in the theme JSON as `"lyric_position": "left"`
- CLI flag overrides theme setting

---

## Issue #12: Word-level and character-level highlighting

**Labels:** core, M2

Add optional word-by-word or character-by-character highlighting within the active line.

**Word-level highlighting:**
- Words in the active line highlight progressively across the line's duration
- Highlighting is evenly distributed: if a line has 5 words and lasts 3 seconds, each word highlights for 0.6s
- Highlighted words use the active color; not-yet-sung words use a mid-opacity color
- Already-sung words remain in active color

**Character-level highlighting:**
- Same concept but per-character instead of per-word
- Characters highlight progressively across the line duration

**Configuration:**
- CLI flag: `--highlight-mode line|word|character` (default: `line`)
- Theme JSON: `"highlight_mode": "line"`
- `line` = entire line highlights at once (current M2 default behavior)
- `word` = word-by-word progressive highlight
- `character` = character-by-character progressive highlight

---

## Issue #13: Video background support

**Labels:** core, M2

Add support for an MP4 video file as the background instead of a solid color.

**Requirements:**
- Accept an MP4 file as background input
- If background video is shorter than the song, seamlessly loop it (crossfade or hard loop at the cut point)
- If background video is longer than or equal to the song, trim to song length
- If no background video is provided, fall back to solid color from theme
- Background video is rendered at 1920x1080; scale/crop input video to fit if dimensions differ
- Background renders behind the lyrics layer

**Auto-matching:**
- Integrates with Issue #9 auto-matching: looks for `input/backgrounds/<song_name>.mp4`
- Can be overridden with `--background /path/to/file.mp4`
- Can be explicitly disabled with `--no-background` to force solid color

---

## Issue #14: Configurable text overlay strip for readability

**Labels:** core, M2

Add an optional semi-transparent overlay behind the lyrics area to ensure text readability over busy video backgrounds.

**Requirements:**
- A vertical strip matching the width of the lyrics column (left/center/right 1/3)
- Semi-transparent dark overlay rendered between the background layer and the lyrics layer
- Configurable opacity: 0 (fully transparent / off) to 100 (fully opaque)
- Default: 0 (off) — user enables when needed for readability over video backgrounds

**Configuration:**
- CLI flag: `--text-overlay 50` (opacity percentage)
- Theme JSON: `"text_overlay_opacity": 0`
- Overlay color from theme: `"text_overlay_color": "#000000"`

---

## Issue #15: Update theme schema for M2 features

**Labels:** theme, M2

Update the Durt Nurs theme and theme schema to support all new M2 settings.

**New theme properties:**
```json
{
  "name": "Durt Nurs",
  "background_color": "#1a1a1a",
  "text_color": "#ffffff",
  "active_text_color": "#ffcc00",
  "active_text_bold": true,
  "active_text_glow": true,
  "active_glow_color": "#ffcc00",
  "inactive_text_opacity_gradient": [0.6, 0.4, 0.2],
  "font_family": "Arial Bold",
  "font_size": 72,
  "line_spacing": 1.5,
  "lyric_position": "center",
  "highlight_mode": "line",
  "text_overlay_opacity": 0,
  "text_overlay_color": "#000000"
}
```

**Requirements:**
- All new properties have sensible defaults so existing themes still work
- `inactive_text_opacity_gradient` is an array of opacities for lines 1, 2, 3 away from active
- Validate theme on load with clear error messages for invalid values
- Update README with full theme property documentation

---

## Issue #16: Update CLI for M2 features

**Labels:** cli, M2

Update the CLI to support all M2 features and the new auto-match workflow.

**New/changed flags:**
```bash
lyric-video --song <name>                    # auto-match from input/ folders
            --lyrics <path>                  # explicit override
            --audio <path>                   # explicit override
            --background <path>              # explicit override
            --no-background                  # force solid color
            --lyric-position left|center|right
            --highlight-mode line|word|character
            --text-overlay <0-100>
            --theme <path>
            --output <path>
            --fps <int>
            --preview                        # first 30 seconds only
```

**Removed flags:**
- `--animation` (M1 animation styles removed)

**Behavior:**
- `--song` is the primary interface; resolves audio, lyrics, and background from `input/` folders
- Explicit path flags override auto-matched files
- All style flags override theme settings
- Helpful error messages when files not found (suggest correct folder and naming)
