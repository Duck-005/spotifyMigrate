from dotenv import load_dotenv
import os
import re
import math

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import yt_dlp

class Song:
    def __init__(self, name, artist, duration):
        self.name = clean_song_title(name)
        self.duration = duration
        self.artist = artist
    
    def searchQuery(self):
        return "track: " + self.name + ", artist: " + self.artist

def clean_song_title(rawTitle):
    # remove all () and [] groups
    # ex. Bekhayali (Arijit Singh Version) [From "Kabir Singh"]
    cleaned = re.sub(r"[\(\[].*?[\)\]]", "", rawTitle)
    return cleaned.strip()

def spotifyLoad():
    load_dotenv()

    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REDIRECT_URI = "https://google.com"

    scope = "user-read-private playlist-read-private playlist-read-collaborative"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=scope
    ))

    playlist = sp.playlist(playlist_id="4T7fvz2Mhhr342aoOvcU55")
    
    songs = []

    for song in playlist["tracks"]['items']:
        songs.append(Song(
            song["track"]["name"],
            song["track"]["artists"][0]["name"],
            math.floor(song["track"]["duration_ms"]/(1000))
        ))
    
    return songs

def filter(info, song, max_duration_diff=5):
    try:
        if info and 'entries' in info:
            for entry in info['entries']:
                print(f"Title: {entry.get('title')}")
                print(f"Uploader: {entry.get('uploader')}")
                print(f"URL: {entry.get('webpage_url')}\n")
                
                title = entry.get('title').lower()
                
                if song.name.lower() not in title:
                    continue
                
                excluded_keywords = ["remix", "live", "cover", "karaoke", "slowed", "reverb", "vocals", "flute", "instrumental", "8D"]
                if any(word in title for word in excluded_keywords):
                    continue
                
                duration = entry.get('duration')
                if duration is None or abs(duration - song.duration) > max_duration_diff:
                    continue
                
                return True, entry.get('webpage_url')
            else:
                return False, ""              
        else:
            print(f"No results found for song - {song.name}")
            return False, ""
            
    except Exception as err:
        print("error occurred ", err)

        
def ytDownload(songs):  
    for song in songs:
        search_term = song.searchQuery()
        
        ydl_opts = {
            'format': 'bestaudio/best',                     
            'outtmpl': f"./downloads/{song.name.replace(" ", "-")}.%(ext)s", # Output file naming template
            'quiet': True, 
            'no_warnings': True,
            'noplaylist': True, # Download only one video if playlist
            'ignoreerrors': True,
            'restrictfilenames': True, # avoid invalid characters
            'postprocessors': [{ # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch{10}:{search_term}", download=False)
                print("-"*40)
                print("search term: ", search_term)
                
                flag, video_url = filter(info, song)
                print(video_url)
                
                if flag:
                    ydl.download([video_url])
                    print(f"downloaded song: {song.name}")
                else:
                    print(f"couldn't find a match for the song - {song.name}")
                
            except Exception as err:
                print("an error occurred ", err)     
        
def main():
    songs = spotifyLoad()
    ytDownload(songs)

if __name__ == "__main__":
    main()