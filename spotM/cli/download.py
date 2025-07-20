import re

from spotM.core import spotify as sp
from spotM.core import youtube as yt
        
def download(url, outputDir):
    if 'track' in url:
        song = sp.loadSong(url)
        yt.downloadSong(song)
        
    elif 'playlist' in url:
        songs = sp.loadPlaylist(url)
        yt.downloadPlaylist(songs, outputDir)
        
    else:
        print("unsupported URL type")
    