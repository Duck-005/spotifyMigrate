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
            for song in playlist['items']:
                songs.append(Song(
                    name=song["track"]["name"],
                    artist=song["track"]["artists"][0]["name"],
                    duration=math.floor(song["track"]["duration_ms"]/(1000))
                ))
            
            if playlist['next']:
                playlist = sp.next(playlist)
            else:
                break
            
    except Exception as err:
        print("error occurred: ", err)
    
    return songs

def loadSong(spotifyURI):
    try:
        sp = loadCredentials()
        
        track = sp.track(track_id=spotifyURI)
        song = Song(
            name=track['name'],
            artist=track['artists'][0]['name'],
            duration=track["duration_ms"]/(1000)
        )
        
        return song
        
    except Exception as err:
        print('an error occurred: ', err)