#!/usr/bin/env python3

import requests
import os

def fetch_filter_urls():
    url = "https://raw.githubusercontent.com/brave/adblock-resources/refs/heads/master/filter_lists/list_catalog.json"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes

    data = response.json()
    filter_urls = []

    for item in data:
        sources = item.get("sources", [])
        for source in sources:
            filter_urls.append(source.get("url"))

    return filter_urls

def download_filter(url, dir_path):
    """Download a filter file from the given URL and save it to the specified path."""
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    filename = os.path.basename(url)
    path = os.path.join(dir_path, filename)
    with open(path, "wb") as file:
        file.write(response.content)

    print(f"Downloaded filter from {url} to {path}")

if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "filters")
    os.makedirs(output_dir, exist_ok=True)
    urls = fetch_filter_urls()
    for url in urls:
        download_filter(url, output_dir)
