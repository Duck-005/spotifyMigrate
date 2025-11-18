import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from dotenv import load_dotenv
import os
import math

from spotM.core.utils import Song, clean_song_title

def loadCredentials():
    load_dotenv()
    
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    auth_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    
    return spotipy.Spotify(auth_manager=auth_manager)

def loadPlaylist(spotifyURI):
    songs = []
    
    try:
        sp = loadCredentials()
        playlist = sp.playlist_items(playlist_id=spotifyURI)

        while playlist:
            for item in playlist['items']:
                track = item.get('track')
                if not track:
                    continue

                album = track.get('album', {})
                artists = track.get('artists', [])

                songs.append(Song(
                    name=track.get('name', 'Unknown Title'),
                    artists=", ".join([a.get('name', 'Unknown Artist') for a in artists]),
                    duration=math.floor(track.get('duration_ms', 0) / 1000),
                    cover_url=album['images'][0]['url'] if album.get('images') else "",
                    album=album.get('name', 'Unknown Album'),
                    spotifyURI=track.get('id', ''),
                    youtube_url=f"https://music.youtube.com/watch?v={track.get('id', '')}",
                ))

            # handle pagination
            if playlist.get('next'):
                playlist = sp.next(playlist)
            else:
                break

    except Exception as err:
        print("error occurred:", err)
    
    return songs

def loadSong(spotifyURI):
    try:
        sp = loadCredentials()
        
        track = sp.track(track_id=spotifyURI)
        album = track.get('album', {})
        artists = track.get('artists', [])
        
        song = Song(
            name=track.get('name', 'Unknown Title'),
            artists=", ".join([a.get('name', 'Unknown Artist') for a in artists]),
            duration=math.floor(track.get('duration_ms', 0) / 1000),
            cover_url=album['images'][0]['url'] if album.get('images') else "",
            album=album.get('name', 'Unknown Album'),
            spotifyURI=track.get('id', ''),
            youtube_url=f"https://music.youtube.com/watch?v={track.get('id', '')}",
        )
        
        return song
        
    except Exception as err:
        print('an error occurred: ', err)