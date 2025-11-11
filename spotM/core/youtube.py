import yt_dlp

from spotM.core.utils import Song, filter

import concurrent.futures
import threading
import re

ydl_opts = {
    'format': 'bestaudio/best',                     
    'outtmpl': None, # Output file naming template
    'quiet': True, 
    'no_warnings': True,
    'noplaylist': True, # Download only one video if playlist
    'ignoreerrors': True,
    'restrictfilenames': True, # avoid invalid characters
    'postprocessors': [{ # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }],
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }
}

print_lock = threading.Lock()

def safe_print(text):
    with print_lock:
        print(text, flush=True)

def download_song(song, outputDir, ydl_opts):
    log_lines = []
    try:
        filename = re.sub(r'[-\s]+', '-', song.name.strip())
        ydl_opts['outtmpl'] = f"./{outputDir}/{filename}.%(ext)s"

        log_lines.append("-" * 60)
        log_lines.append(f"Search term: {song.searchQuery()}")

        flag, videoId = filter(song, info=song.searchInfo())
        if not flag:
            log_lines.append(f"Couldn't find a match for the song - {song.name}")
            return

        yt_url = f"https://music.youtube.com/watch?v={videoId}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt_url])

        log_lines.append(f"Youtube URL: {yt_url}")
        log_lines.append(f"Downloaded song: {song.name}")

    except Exception as err:
        log_lines.append(f"Error downloading {song.name}: {err}")

    safe_print("\n".join(log_lines))

def downloadPlaylist(songs: list, outputDir, max_workers=3):
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(download_song, song, outputDir, ydl_opts.copy())
            for song in songs
        ]
        for future in concurrent.futures.as_completed(futures):
            # trigger exception printing early
            try:
                future.result()
            except Exception as e:
                safe_print(f"Worker error: {e}")
                
    print("-" * 60)