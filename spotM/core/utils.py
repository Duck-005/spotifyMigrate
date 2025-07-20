from ytmusicapi import YTMusic

import re

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

# filtration logic

def tokenize(text):
    # remove non-alphanumeric chars
    text = re.sub(r'[^\w\s]', '', text.lower())
    return set(text.split())

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
                
                print(f"Title: {entry['title']}")
                print(f"Artist: {entry['artists'][0]['name']}")
                print(f"URL: https://music.youtube.com/watch?v={entry['videoId']}\n")
                
                return True, entry['videoId']
            else:
                return False, ""              
        else:
            print(f"No results found for song - {song.name}")
            return False, ""
            
    except Exception as err:
        print("error occurred ", err)