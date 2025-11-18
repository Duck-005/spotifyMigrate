import re
import os
import json
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TXXX, APIC
from mutagen.mp3 import MP3
import requests

from spotM.core import spotify as sp
from spotM.core import youtube as yt
from spotM.core.utils import song_filename, canonical_metadata, hash_metadata
        
def download(url, outputDir):
    if 'track' in url:
        song = sp.loadSong(url)
        
        yt.download_song(song, outputDir, yt.ydl_opts)
        
    elif 'playlist' in url:
        songs = sp.loadPlaylist(url)
        yt.downloadPlaylist(songs, outputDir)
        
        for song in songs:
            embed_metadata(song_filename(song=song, output_dir=outputDir), song)
            
        create_tracking_file(songs, output_dir=outputDir)
        
    else:
        print("unsupported URL type")
        
def embed_metadata(filepath, song):
    audio = MP3(filepath, ID3=ID3)

    if audio.tags is None:
        audio.add_tags()
    
    audio.tags.add(TIT2(encoding=3, text=song.name))  
    audio.tags.add(TPE1(encoding=3, text=song.artists))
    audio.tags.add(TALB(encoding=3, text=song.album))
    
    audio.tags.add(TXXX(encoding=3, desc="SpotifyURI", text=song.spotifyURI))
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
    
def create_tracking_file(songs, output_dir):
    sync_path = os.path.join(output_dir, ".spotifyMigrate.json")
    data = {}
    
    for song in songs:
        data[song.spotifyURI] = {
                "metadata": canonical_metadata(song),
                "hash": hash_metadata(song),
                "filename": song_filename(song=song, dir=False)
            }
    
    with open(sync_path, 'w') as f:
        json.dump(data, f, indent=4)
            
    