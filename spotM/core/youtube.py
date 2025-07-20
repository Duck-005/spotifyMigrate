import yt_dlp

from spotM.core.utils import Song, filter

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
            }]
        }

def downloadPlaylist(songs: list[Song]):  
    for song in songs:
        
        ydl_opts['outtmpl'] = f"./downloads/{re.sub(' +', '-', song.name)}.%(ext)s"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print("-"*50)
                print("search term: ", song.searchQuery())
                
                flag, videoId = filter(song, info=song.searchInfo())
                
                if flag:
                    ydl.download([f"https://music.youtube.com/watch?v={videoId}"])
                    print(f"downloaded song: {song.name}")
                else:
                    print(f"couldn't find a match for the song - {song.name}")
                
            except Exception as err:
                print("an error occurred: ", err) 

def downloadSong(song):
    ydl_opts['outtmpl'] = f"./{re.sub(' +', '-', song.name)}.%(ext)s"
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try: 
            print("search term: ", song.searchQuery())
            
            flag, videoId = filter(song, info=song.searchInfo())
            if flag:
                print(f"song link: https://music.youtube.com/watch?v={videoId}")
                    
                ydl.download([f"https://music.youtube.com/watch?v={videoId}"])
                print(f"downloaded song: {song.name}")
            else:
                print(f"couldn't find a match for the song - {song.name}")
                    
        except Exception as err:
            print("an error occurred: ", err)