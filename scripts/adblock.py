"""Add an HTTP header to each response."""
import mitmproxy_adblock
from mitmproxy import http

class Person:
    def __init__(self, name):
        self.name = name

class AddHeader:
    def __init__(self):
        filter_set = mitmproxy_adblock.FilterSet()
        filter_set.add_filter("||example.org^")
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
        pass


addons = [AddHeader()]
