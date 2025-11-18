# spotifyMigrate

**spotifyMigrate** is a Python-based tool that allows you to download entire Spotify playlists using YouTube Music as the source. It fetches metadata from Spotify, finds matching tracks on YouTube Music via the YTMusic API, downloads them with yt-dlp, and embeds all metadata (artist, album, cover art, URLs) into the audio files automatically.

---

## Architecture Overview

### Modules:

* `spotify.py` - Handles Spotify API requests and playlist parsing.
* `youtube.py` - Performs YouTube Music searches using ytmusicapi.
* `download.py` - Coordinates downloading, metadata embedding, and parallel processing.
* `metadata.py` - Embeds ID3 tags, including custom fields (SourceURL, YouTubeURL).
* `song.py` - Defines the Song dataclass, representing metadata for each track.
* `sync.py` - Syncs the offline directory to the spotify playlist and optionally deletes stale songs from offline playlist.

### Workflow:

1. Retrieve playlist data from Spotify.
2. Build `Song` objects containing metadata.
3. For each song:

   * Search YouTube Music.
   * Select the best matching result.
   * Download using `yt-dlp`.
   * Embed metadata and cover image.
4. Save the processed file into your local output directory.

---

## Requirements

* Python 3.9 or later
* yt-dlp
* spotipy
* ytmusicapi
* mutagen
* ffmpeg (mandatory)

---

# Setup

---

## 1. Install ffmpeg

This tool cannot function without ffmpeg.

### Windows

Download from [here](https://www.ffmpeg.org/download.html). Extract and add the `/bin` folder to PATH.

### Linux

```
sudo apt install ffmpeg
```

### macOS

```
brew install ffmpeg
```

Verify installation:

```
ffmpeg -version
```

---

## 2. Set up Spotify API Credentials

Create a Spotify Developer app and retrieve your **CLIENT_ID** and **CLIENT_SECRET**.

Create a `.env` file:

```
CLIENT_SECRET="REDACTED"
CLIENT_ID="REDACTED"
```

During first run, authentication will prompt you to paste a redirected URL to generate a token cache.

---

## 3. Environment Setup Options

You may use **Poetry** (recommended) or the classic `requirements.txt`.

## A. Using Poetry (recommended)

### Install locked dependencies

```
poetry install
```

### Run the app

```
poetry run python main.py
```

## B. Using requirements.txt (legacy-compatible)

Install dependencies:

```
pip install -r requirements.txt
```

Run the program:

```
python main.py
```

---

## 4. Run the Downloader

After setup and authentication:

```
python main.py
```

Or if using Poetry:

```
poetry run python main.py
```

Important notes:

> * This project requires Spotify API credentials even for public playlists.
> * ffmpeg must be installed, the download is handled solely by ffmpeg.
> * yt-dlp should be kept updated since youtube updates their site to deter scrapers.

---

## Configuration

Modify `ydl_opts` in the code to control output format, codec, and post-processing:

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

---

## Metadata Embedding

Metadata is written using `mutagen.id3` frames:

* `TIT2`: Track title
* `TPE1`: Artist
* `TALB`: Album
* `APIC`: Album art (JPEG)
* `TXXX:SpotifyURI`: Spotify source URI
* `TXXX:YouTubeURL`: YouTube Music source URL

---

## Parallel Downloads

Processed using ThreadPoolExecutor:

```python
downloadPlaylist(songs, "downloads", ydl_opts, max_workers=4)
```

Recommended worker count: 4–6, otherwise youtube may throttle download speeds.

---

Command-Line Usage
Download a playlist
```python
python main.py download <playlist_url> -o <output_dir>
```

Arguments:

url — Spotify playlist URL or ID

`-o`, `--output` — Directory to save downloaded files (default: downloads)

Sync a playlist
```python
python main.py sync <playlist_url> -o <output_dir> [--delete-stale]
```

Arguments:

url — Spotify playlist URL or ID

`-o`, `--output` — Output directory (default: downloads)

`-d`, `--delete-stale` — Remove local songs that are no longer in the Spotify playlist

---

## Known Issues

* YouTube rate limits may cause 403 or 416 errors under high parallelism.
* Region-locked or unavailable tracks may not return valid matches.
* Some streams may fail if ffmpeg/ffprobe are not in PATH.
