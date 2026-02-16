# Lyric Video Generator

Generate lyric videos with timed text animations from a JSON lyrics file and an audio track.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
lyric-video --lyrics examples/sample_lyrics.json \
            --audio path/to/song.mp3 \
            --theme themes/durt_nurs.json \
            --animation fade \
            --output output/video.mp4
```

### Options

- `--lyrics` (required): path to lyrics JSON
- `--audio` (required): path to audio file
- `--theme` (optional): path to theme JSON (default: `themes/durt_nurs.json`)
- `--animation` (optional): `fade` | `slide` | `typewriter` (default: `fade`)
- `--output` (optional): output path (default: `output/<title>.mp4`)
- `--fps` (optional): frame rate (default: 30)
- `--preview` (optional): generate only first 30 seconds

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

An empty `text` field marks the end of lyrics.

## Animations

- **fade** — text fades in and out (default)
- **slide** — text slides up from below
- **typewriter** — characters appear one at a time
