"""Add an HTTP header to each response."""
import mitmproxy_adblock
from mitmproxy import http
import os
import re
import hashlib
from pymediainfo import MediaInfo
import tempfile

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


def parse_binary_media_content(binary_data: bytes):
    with tempfile.NamedTemporaryFile(delete=True, suffix=".webm") as tmp:
        tmp.write(binary_data)
        tmp.flush()  # Make sure all data is written
        media_info = MediaInfo.parse(tmp.name)
        return [track.to_data() for track in media_info.tracks]

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

    def block_request(self, flow):
        flow.response = http.Response.make(
            403,  # (200 OK)
            b"", # (content)
            {},  # (headers)
        )
        flow.response.headers["x-adblock"] = "true"

    def is_youtube_short_media(self, flow):
        url = flow.request.url
        # if host is googlevideo.com
        if "googlevideo.com" not in url:
            return False

        media_info = parse_binary_media_content(flow.response.content)
        video_tracks = [track for track in media_info if track.track_type == "Video"]
        if len(video_tracks) == 0:
            return False
        for track in video_tracks:
            track_width = track.get("width")
            track_height = track.get("height")
            if track_width and track_height:
                if track_width < track_height:
                    return True
        return False

    def request(self, flow):
        print("Apply AbBlocker blocking rules")
        result = self.ad_blocker.check_network_request(flow.request.url, "http://localhost")
        if result.matched:
            print(f"AdBlocker detected: {flow.request.url}")
            self.block_request(flow)

    def response(self, flow):
        dump_response_to_file(flow)

        if self.is_youtube_short_media(flow):
            print(f"AdBlocker detected: {flow.request.url}")
            self.block_request(flow)
            return

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
