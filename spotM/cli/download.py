import re
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TXXX, APIC
from mutagen.mp3 import MP3
import requests

from spotM.core import spotify as sp
from spotM.core import youtube as yt
        
def download(url, outputDir):
    if 'track' in url:
        song = sp.loadSong(url)
        yt.download_song(song, ".", yt.ydl_opts)
        
    elif 'playlist' in url:
        songs = sp.loadPlaylist(url)
        yt.downloadPlaylist(songs, outputDir)
        for song in songs:
            embed_metadata(f"./{outputDir}/{re.sub(r'[-\s]+', '-', song.name.strip())}.mp3", song)
        
    else:
        print("unsupported URL type")
        
def embed_metadata(filepath, song):
    audio = MP3(filepath, ID3=ID3)

    if audio.tags is None:
        audio.add_tags()
    
    audio.tags.add(TIT2(encoding=3, text=song.name))  
    audio.tags.add(TPE1(encoding=3, text=song.artist))
    audio.tags.add(TALB(encoding=3, text=song.album))
    
    audio.tags.add(TXXX(encoding=3, desc="SourceURL", text=song.source_url))
    audio.tags.add(TXXX(encoding=3, desc="YouTubeURL", text=song.youtube_url))
        
    if song.cover_url: 
        img_data = requests.get(song.cover_url).content
        audio.tags.add(APIC(
            encoding=3,
            mime='image/jpeg',
            type=3,
            desc='Cover',
            data=img_data
        ))

    audio.save()
    
    
    