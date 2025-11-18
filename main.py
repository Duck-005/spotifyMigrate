import argparse

from spotM.cli.download import download
from spotM.cli.sync import sync

def main():
    parser = argparse.ArgumentParser(description="program to download spotify playlists")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # download command
    download_parser = subparsers.add_parser("download", help="Download a Spotify playlist from YouTube")
    download_parser.add_argument("url", help="Spotify playlist URL or ID")
    download_parser.add_argument("-o", "--output", default="downloads", help="Download directory")

    # sync command
    sync_parser = subparsers.add_parser("sync", help="Sync playlists")
    sync_parser.add_argument("url", help="Spotify playlist URL or ID")
    sync_parser.add_argument("-o", "--output", default="downloads", help="Output directory")
    sync_parser.add_argument("-d", "--delete-stale", action="store_true", help="Delete songs not in playlist but in local directory")

    args = parser.parse_args()

    if args.command == "download":
        download(args.url, args.output)

    elif args.command == "sync":
        sync(args.url, args.output, args.delete_stale)

if __name__ == "__main__":
    main()
