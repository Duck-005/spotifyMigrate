# spotifyMigrate
**spotifyMigrate** is a Python-based tool that allows you to download entire Spotify playlists using YouTube Music as the source. 
It fetches metadata from Spotify, finds matching tracks on YouTube Music via the YTMusic API, downloads them with yt-dlp, and embeds all metadata (artist, album, cover art, URLs) into the audio files automatically.

## Architecture Overview

### Modules:
- `spotify.py` – Handles Spotify API requests and playlist parsing.
- `youtube.py` – Performs YouTube Music searches using ytmusicapi.
- `download.py` – Coordinates downloading, metadata embedding, and parallel processing.
- `metadata.py` – Embeds ID3 tags, including custom fields (SourceURL, YouTubeURL).
- `song.py` – Defines the Song dataclass, representing metadata for each track.

### Workflow:
1. Retrieve playlist data from Spotify.
2. Build `Song` objects containing metadata.
3. For each song:
  - Search YouTube Music.
  - Select the best matching result.
  - Download using `yt-dlp`.
  - Embed metadata and cover image.
4. Save the processed file into your local output directory.

## Requirements
- Python 3.9 or later
- yt-dlp
- spotipy
- ytmusicapi
- mutagen

  Install Dependencies:
  ```python
  pip install requirements.txt
  ```

## Setup

1. Get Spotify API Credentials
Create a Spotify Developer app at developer.spotify.com and note your client ID and client secret.

2. Authenticate
Running the tool with your credentials in .env will prompt you to cache the token (copied from the browser).

4. Run the downloader
```python
python main.py
```

> **Important:** This project requires Spotify API credentials even for public playlists.

> **Important**: This project requires ffmpeg. Install it from [here](https://www.ffmpeg.org/download.html)
## Configuration

You can modify ydl_opts for yt-dlp to control output format, codec, and post-processing:
```python
ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
    "continuedl": False,
    "overwrites": True
}
```

## Metadata Embedding

Metadata is written using `mutagen.id3` frames:
- `TIT2`: Track title
- `TPE1`: Artist
- `TALB`: Album
- `APIC`: Album art (JPEG)
- `TXXX:SourceURL`: Spotify source URL
- `TXXX:YouTubeURL`: YouTube Music source URL

This ensures rich tagging and compatibility across media players.

## Parallel Downloads

Downloads are processed using ThreadPoolExecutor.
You can adjust the concurrency level:

```python
downloadPlaylist(songs, "downloads", ydl_opts, max_workers=4)
```
Recommended range: 4–6 threads for stability.

## Known Issues

- YouTube rate limits may trigger 403 or 416 errors on heavy parallel downloads.
- Region-restricted or unavailable tracks may not have valid YouTube matches.
- Some audio streams may fail postprocessing if ffmpeg or ffprobe is missing from PATH.
