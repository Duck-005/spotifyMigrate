from ytmusicapi import YTMusic

import re
from dataclasses import dataclass, field

@dataclass
class Song:
    name: str
    artist: str
    duration: float
    cleaned_name: str = field(init=False)
    cover_url: str
    album: str
    source_url: str
    youtube_url: str
    
    def __post_init__(self):
        self.cleaned_name = clean_song_title(self.name)
    
    def searchQuery(self):
        return self.name + ", artist: " + self.artist
    
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
                
                if matchScore(song_title=song.name, video_title=title) < 0.6:
                    continue
                
                excluded_keywords = ["remix", "live", "cover", "karaoke", "slowed", "reverb", "vocals", "8D"]
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