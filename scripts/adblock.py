"""Add an HTTP header to each response."""
import mitmproxy_adblock
from mitmproxy import http
import os
import re

def make_eligible_filename(url):
    return re.sub(r'[^\w\-_\.]', '_', url)

def dump_response_to_file(flow):
    if not os.path.exists("logs"):
        os.makedirs("logs")

    filename = make_eligible_filename(flow.request.url)
    with open(f"/var/log/mitmproxy-adblock/{filename}", "wb") as f:
        f.write(flow.response.content)


class AdBlocker:
    def __init__(self):
        filter_set = mitmproxy_adblock.FilterSet()
        for file in os.listdir("/etc/filters"):
            file_path = os.path.join("/etc/filters", file)
            if os.path.isfile(file_path):
                with open(file_path, "r") as f:
                    filter_set.add_filter_list(f.read().strip())
        self.ad_blocker = mitmproxy_adblock.Engine.from_filter_set(filter_set, True)

    def request(self, flow):
        result = self.ad_blocker.check_network_request(flow.request.url, "http://localhost")
        if result.matched:
            flow.response = http.Response.make(
                403,  # (200 OK)
                b"", # (content)
                {},  # (headers)
            )

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
