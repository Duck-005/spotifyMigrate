import argparse

from spotM.cli.download import download

def main():
    parser = argparse.ArgumentParser(description="program to download spotify playlists")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")
    
    download_parser = subparsers.add_parser("download", help="Download a Spotify playlist from YouTube")
    download_parser.add_argument("download", help="Spotify playlist URL or ID")
    download_parser.add_argument("-o", "--output", default="downloads/", help="Download directory")
    
    args = parser.parse_args()
    
    if args.command == "download":
        download(args.download, args.output)
           
if __name__ == "__main__":
    main()
