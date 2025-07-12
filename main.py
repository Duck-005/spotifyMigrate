from dotenv import load_dotenv
import os
import re
import math
import argparse

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import yt_dlp
from ytmusicapi import YTMusic

class Song:
    def __init__(self, name, artist, duration):
        self.name = clean_song_title(name)
        self.duration = duration
        self.artist = artist
    
    def searchQuery(self):
        return "track: " + self.name + ", artist: " + self.artist
    
    def searchInfo(self):
        try:
            ytmusic = YTMusic()
            info = ytmusic.search(query=self.searchQuery(), filter="songs", limit=10)
        except Exception as err:
            print("an error occurred: ", err)
            
        return info 

def clean_song_title(rawTitle):
    # remove all () and [] groups
    # ex. Bekhayali (Arijit Singh Version) [From "Kabir Singh"]
    cleaned = re.sub(r"[\(\[].*?[\)\]]", "", rawTitle)
    return cleaned.strip()

def tokenize(text):
    # remove non-alphanumeric chars
    text = re.sub(r'[^\w\s]', '', text.lower())
    return set(text.split())

def spotifyLoad(spotifyURI):
    try:
        load_dotenv()

        CLIENT_ID = os.getenv("CLIENT_ID")
        CLIENT_SECRET = os.getenv("CLIENT_SECRET")

        auth_manager = SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)

        playlist = sp.playlist_items(playlist_id=spotifyURI)
        
        songs = []

        while playlist:
            for song in playlist['items']:
                songs.append(Song(
                    song["track"]["name"],
                    song["track"]["artists"][0]["name"],
                    math.floor(song["track"]["duration_ms"]/(1000))
                ))
            
            if playlist['next']:
                playlist = sp.next(playlist)
            else:
                break
            
    except Exception as err:
        print("error occurred: ", err)
    
    return songs

def matchScore(song_title, video_title):
    song_tokens = tokenize(song_title)
    video_tokens = tokenize(video_title)

    if not song_tokens:
        return 0.0

    matched = song_tokens.intersection(video_tokens)
    return len(matched) / len(song_tokens)

def filter(song, info, max_duration_diff=8):
    try:
        if info:
            for entry in info:
                print(f"Title: {entry['title']}")
                print(f"Artist: {entry['artists'][0]['name']}")
                print(f"URL: https://music.youtube.com/watch?v={entry['videoId']}\n")
                
                title = entry['title'].lower()
                
                if score := matchScore(song_title=song.name, video_title=title) < 0.6:
                    print("score: ", score)
                    continue
                
                excluded_keywords = ["remix", "live", "cover", "karaoke", "slowed", "reverb", "vocals", "flute", "instrumental", "8D"]
                if any(word in title for word in excluded_keywords):
                    continue
                
                duration = entry['duration_seconds']
                if duration is None or abs(duration - song.duration) > max_duration_diff:
                    continue
                
                return True, entry['videoId']
            else:
                return False, ""              
        else:
            print(f"No results found for song - {song.name}")
            return False, ""
            
    except Exception as err:
        print("error occurred ", err)

        
def ytDownload(songs):  
    for song in songs:
        
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
                print("-"*50)
                print("search term: ", song.searchQuery())
                
                flag, videoId = filter(song, info=song.searchInfo())
                
                if flag:
                    print(f"song link: https://music.youtube.com/watch?v={videoId}")
                    
                    ydl.download([f"https://music.youtube.com/watch?v={videoId}"])
                    print(f"downloaded song: {song.name}")
                else:
                    print(f"couldn't find a match for the song - {song.name}")
                
            except Exception as err:
                print("an error occurred ", err)     
          
def main():
    parser = argparse.ArgumentParser(description="program to download spotify playlists")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")
    
    download_parser = subparsers.add_parser("download", help="Download a Spotify playlist from YouTube")
    download_parser.add_argument("download", help="Spotify playlist URL or ID")
    
    args = parser.parse_args()
    
    if args.command == "download":
        songs = spotifyLoad(args.download)
        ytDownload(songs)
        
if __name__ == "__main__":
    main()
