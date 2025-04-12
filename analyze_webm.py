#!/usr/bin/env python

import sys
import json
from pymediainfo import MediaInfo

def main(filepath):
    media_info = MediaInfo.parse(filepath)
    metadata = [track.to_data() for track in media_info.tracks]
    print(json.dumps(metadata, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python media_info_json.py <path_to_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    main(file_path)
