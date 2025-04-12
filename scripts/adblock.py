"""Add an HTTP header to each response."""
import mitmproxy_adblock
from mitmproxy import http
import os
import re
import hashlib
import yt_dlp

def make_eligible_filename(flow : http.HTTPFlow):
    hostname = flow.request.pretty_host
    hostname_as_filename = re.sub(r'[^\w\-_\.]', '_', hostname)
    url_hash = hashlib.sha256(flow.request.url.encode('utf-8')).hexdigest()
    filename = f"{hostname_as_filename}_{url_hash}"
    return filename

def dump_response_to_file(flow):
    if not flow.response.content:
        return

    if not os.path.exists("logs"):
        os.makedirs("logs")

    filename = make_eligible_filename(flow)
    with open(f"/var/log/mitmproxy-adblock/{filename}.request.txt", "w") as f:
        f.write(flow.request.url)

    with open(f"/var/log/mitmproxy-adblock/{filename}.response.bin", "wb") as f:
        f.write(flow.response.content)


class AdBlocker:
    def __init__(self):
        # Init AdBlocker
        filter_set = mitmproxy_adblock.FilterSet()
        for file in os.listdir("/etc/filters"):
            file_path = os.path.join("/etc/filters", file)
            if os.path.isfile(file_path):
                with open(file_path, "r") as f:
                    filter_set.add_filter_list(f.read().strip())
        self.ad_blocker = mitmproxy_adblock.Engine.from_filter_set(filter_set, True)
        print("AdBlocker initialized")

        # Init yt-dlp
        ydl_opts = {
            'skip_download': True,              # Don't download video
            'writeinfojson': True,              # Save info.json to file
            'quiet': False,                     # Optional: reduce output
        }

        self.ydl = yt_dlp.YoutubeDL(ydl_opts)
        print("yt-dlp initialized")


    def block_request(self, flow):
        flow.response = http.Response.make(
            403,  # (200 OK)
            b"", # (content)
            {},  # (headers)
        )

    def is_youtube_short_url(self, url):
        # if host is googlevideo.com
        if "googlevideo.com" not in url:
            return False

        info_dict = self.ydl.extract_info(url, download=False)
        for format in info_dict.get("formats", []):
            width = format.get("width")
            height = format.get("height")
            if width is None or height is None:
                continue
            if width < height:
                # This is a youtube short
                return True

        return False

    def request(self, flow):
        print("Apply AbBlocker blocking rules")
        result = self.ad_blocker.check_network_request(flow.request.url, "http://localhost")
        if result.matched:
            print(f"AdBlocker detected: {flow.request.url}")
            self.block_request(flow)

        # Check the url is a youtube short video
        print(f"Checking if url is a youtube short")
        if self.is_youtube_short_url(flow.request.url):
            print(f"Youtube short detected: {flow.request.url}")
            self.block_request(flow)

    def response(self, flow):
        dump_response_to_file(flow)
        flow.response.headers["x-adblock"] = "true"

        return
        if flow.response.status_code != 200:
            print(f"Skipping non-200 response: {flow.response.status_code}")
            return

        # Check if the response contains HTML content
        if not flow.response.headers.get("Content-Type", "").startswith("text/html"):
            print(f"Skipping non-HTML response: {flow.response.headers.get('Content-Type')}")
            return

        # Check if the response contains body
        if not flow.response.text:
            print("Skipping empty response body")
            return

        # Clean up the HTML content
        try:
            result_html = result = self.ad_blocker.cleanup_html(flow.request.url, flow.response.text)
            self.response.set_text(result_html)
        except Exception as e:
            print(f"Error processing request: {e}")
            print (f"Leaving response as is")
            return


addons = [AdBlocker()]
