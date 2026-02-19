# Lyric Video Generator — M3 GitHub Issues

Use these with Claude Code to create issues:
`claude "read M3_ISSUES.md and create each issue as a GitHub issue on lyric-video-generator with the appropriate labels"`

---

## Issue #26: PyQt6 project setup and main window scaffolding

**Labels:** setup, M3

Add PyQt6 to the project and create the main application window with a tabbed/paneled layout.

**Dependencies:**
- Add `PyQt6` and `PyQt6-Qt6` to requirements.txt
- Add new entry point: `src/gui/main.py`

**Main window structure:**
- Application title: "Durt Nurs Lyric Video Generator"
- Menu bar: File (New, Open Theme, Save Theme, Quit), Help (About)
- Left sidebar: Song selector panel (Issue #27)
- Center area, top: Preview panel (Issue #31)
- Center area, bottom: Timeline editor (Issue #29)
- Right sidebar: Theme editor panel (Issue #30)
- Bottom bar: Export controls + progress bar (Issue #32)

**Requirements:**
- Resizable window with sensible minimum size (1280x800)
- Panels should be resizable via splitters
- macOS native look and feel where possible
- Placeholder widgets for each panel — actual implementations in subsequent issues
- New CLI entry point: `lyric-video-gui` launches the GUI
- GUI calls into the existing core engine — no duplication of rendering logic

---

## Issue #27: Song selector panel

**Labels:** gui, M3

Create the left sidebar panel for browsing and selecting songs from the `input/` folders.

**Requirements:**
- Scans `input/audio/`, `input/lyrics/`, `input/backgrounds/` on launch and on refresh
- Displays a list of discovered songs with auto-match status:
  - Song name (derived from filename)
  - Icons/indicators showing which files are present: audio ✓/✗, lyrics ✓/✗, background ✓/✗
- Selecting a song loads its lyrics JSON into the timeline editor, loads audio for playback, and detects background video
- Songs with missing required files (audio or lyrics) are visually flagged but still selectable (for partial editing)
- Refresh button to rescan folders
- Double-click or "Load" button to activate a song
- Display the currently loaded song name prominently at the top of the panel

---

## Issue #28: Audio playback engine

**Labels:** core, gui, M3

Create an audio playback service that the timeline editor and preview panel can share.

**Requirements:**
- Load MP3/WAV files for playback
- Play, pause, stop, seek controls
- Report current playback position in real-time (for timeline cursor sync)
- Use `QMediaPlayer` from PyQt6.QtMultimedia
- Expose a signal/slot interface so other panels can:
  - Request playback from a specific timestamp
  - Subscribe to position updates
  - Query total duration
- Transport controls widget (play/pause, stop, seek slider) — can be placed in the timeline panel or as a shared toolbar

---

## Issue #29: Visual timeline editor with draggable markers

**Labels:** gui, M3

Create the timeline editor panel for visually editing lyric timestamps.

**Layout:**
- Horizontal timeline bar representing the full song duration
- Playback cursor showing current audio position (synced to Issue #28)
- Vertical markers for each lyric line, positioned at their timestamp
- Lyric text displayed near or below each marker

**Marker interaction:**
- Markers are draggable horizontally to adjust timestamps
- Dragging a marker updates the corresponding timestamp in the lyrics data
- Snap-to behavior: optional grid snapping (e.g. nearest 0.1s)
- Click a marker to select it and see the lyric text in a detail/edit area
- Selected marker highlighted differently

**Detail/edit area (below timeline):**
- Shows the selected lyric line text (editable)
- Shows start time (editable numerically as well as via drag)
- Shows calculated end time and duration
- Previous/Next buttons to step through lines

**Audio sync:**
- Click anywhere on the timeline to seek audio to that position
- Play button starts audio from current cursor position
- During playback, cursor moves and markers highlight as they're reached

**Zoom/scroll:**
- Horizontal zoom in/out on the timeline (for precise editing)
- Scroll/pan along the timeline when zoomed in

**Data flow:**
- Timeline reads from and writes to the lyrics JSON data model
- Changes to timestamps are reflected immediately
- Unsaved changes indicator
- Save button writes updated timestamps back to the lyrics JSON file

---

## Issue #30: Theme editor panel

**Labels:** gui, M3

Create the right sidebar panel with visual controls for all theme properties.

**Controls (mapped to theme JSON properties):**

Background section:
- `background_color` — color picker
- `text_overlay_opacity` — slider (0–100) with numeric display
- `text_overlay_color` — color picker

Text section:
- `text_color` — color picker
- `font_family` — dropdown (populated from system fonts)
- `font_size` — slider with numeric input (24–144)
- `line_spacing` — slider (1.0–3.0, step 0.1)

Active line section:
- `active_text_color` — color picker
- `active_text_bold` — checkbox
- `active_text_glow` — checkbox
- `active_glow_color` — color picker (enabled only when glow is on)

Inactive lines section:
- `inactive_text_opacity_gradient` — three sliders for lines 1, 2, 3 away from active (0.0–1.0)

Layout section:
- `lyric_position` — dropdown: left / center / right
- `highlight_mode` — dropdown: line / word / character

**Requirements:**
- All controls update the in-memory theme immediately
- Changes do not auto-save to disk — explicit Save Theme button
- Load Theme button to load a different theme JSON
- Save Theme / Save Theme As in File menu and in panel
- Reset to Defaults button
- Theme name displayed at top of panel
- Controls should be grouped in collapsible sections for organization

---

## Issue #31: Preview panel with embedded video player

**Labels:** gui, M3

Create the preview panel that generates and plays back a preview clip.

**Preview generation:**
- "Generate Preview" button triggers a preview render
- Preview renders the first 30 seconds of the video at half resolution (960x540)
- Uses the current theme settings, lyrics, audio, and background
- Calls into the existing core rendering engine — no separate render path
- Progress indicator during generation (can reuse or mirror the export progress bar)
- Preview clip saved to a temp file

**Playback:**
- Embedded `QVideoWidget` + `QMediaPlayer` for playback
- Play/pause controls within the preview panel
- Scrub bar for seeking within the preview

**Behavior:**
- Preview automatically regenerates if theme, timestamps, or other settings change — or at minimum, a visual indicator that the preview is stale and a "Regenerate" button
- Preview uses the currently loaded song's audio, lyrics, and background
- If no song is loaded, the preview panel shows a placeholder message

**Preview options:**
- Start time input — preview 30 seconds starting from a custom timestamp (not just the beginning)
- This helps preview specific sections like choruses or bridges

---

## Issue #32: Export controls and progress bar

**Labels:** gui, M3

Create the bottom bar with export settings and a progress bar.

**Export settings:**
- Output filename — auto-populated from song name, editable
- Output directory — defaults to `output/`, browse button to change
- FPS dropdown: 24 / 30 / 60 (default 30)
- Resolution display: 1920x1080 (fixed for now, shown as label)

**Export button:**
- "Export Video" button starts full render
- Disabled when no song is loaded or required files are missing
- Confirmation if output file already exists (overwrite prompt)

**Progress bar:**
- Shows render progress as percentage
- Estimated time remaining
- Cancel button to abort export
- Status text: "Rendering frame X of Y" or similar

**Behavior:**
- Export runs in a background thread so the GUI remains responsive
- On completion: success message with option to open the output folder or play the video
- On error: error dialog with details
- Export uses all current settings (theme, timestamps, background, position, highlight mode, overlay)

---

## Issue #33: Save/load workflow and unsaved changes handling

**Labels:** gui, M3

Implement proper save/load behavior and unsaved changes detection across the GUI.

**Lyrics changes:**
- Track when timestamps or lyric text have been modified via the timeline editor
- Unsaved changes indicator in the window title (e.g. "• Song Name — Durt Nurs Lyric Video Generator")
- Save writes updated lyrics back to the JSON file in `input/lyrics/`
- Prompt to save unsaved changes when: switching songs, closing the app, or starting an export

**Theme changes:**
- Track when theme properties have been modified via the theme editor
- Separate save flow: Save Theme writes to current theme file, Save Theme As prompts for new path
- Prompt to save unsaved theme changes when: loading a different theme, closing the app

**Keyboard shortcuts (macOS standard):**
- ⌘S — Save lyrics
- ⌘⇧S — Save Theme As
- ⌘Z — Undo (timestamp/lyric changes)
- ⌘⇧Z — Redo
- Space — Play/pause audio

**Undo/redo:**
- Undo stack for timeline edits (marker drags, text edits)
- Standard undo/redo behavior
