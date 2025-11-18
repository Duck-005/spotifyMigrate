import json
import os

from spotM.core import spotify as sp
from spotM.cli import download as dl
from spotM.core.utils import song_filename, Song, canonical_metadata, hash_metadata

def sync(url, output_dir, delete_stale=False):
    sync_path = os.path.join(output_dir, ".spotifyMigrate.json")
    
    if os.path.exists(sync_path):
        with open(sync_path, "r") as f:
            data = json.load(f)
    else:
        data = {}
    
    if 'playlist' not in url:
        print("Sync only works for Spotify playlists.")
        return
    
    songs = sp.loadPlaylist(url)
    song_files = set()
    
    for song in songs:
        song_files.add(song_filename(song=song, output_dir=output_dir, dir=False))
        song_hash = hash_metadata(song)
        
        entry = data.get(song.spotifyURI)

        if entry is None or entry["hash"] != song_hash:
            print(f"Downloading or updating: {song.name}", end="")

            dl.download(
                url=f"https://open.spotify.com/track/{song.spotifyURI}",
                outputDir=output_dir
            )

            data[song.spotifyURI] = {
                "metadata": canonical_metadata(song),
                "hash": song_hash,
                "filename": song_filename(song, dir=False)
            }
        
    if delete_stale:
        local_files = {
            f for f in os.listdir(output_dir) 
            if f.lower().endswith(".mp3")
        }
        
        stale_files = local_files - song_files
        delete_stale_files(output_dir, stale_files)
        
        for track_uri, entry in list(data.items()):
            if entry[song_filename(song, dir=False)] in stale_files:
                del data[track_uri]
        
    save_sync_file(data, output_dir)
    
def save_sync_file(data: dict, output_dir):
    sync_path = os.path.join(output_dir, ".spotifyMigrate.json")
    
    with open(sync_path, "w") as f:
        json.dump(data, f, indent=4)

def delete_stale_files(output_dir, stale_files):
    for file in stale_files:
        path = os.path.join(output_dir, file)
        
        try:
            os.remove(path)
            print(f"Removed stale file: {file}")
        except Exception as e:
            print(f"Failed to delete '{file}': {e}")
