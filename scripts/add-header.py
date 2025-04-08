"""Add an HTTP header to each response."""
import mitmproxy_adblock

class Person:
    def __init__(self, name):
        self.name = name

class AddHeader:
    def __init__(self):
        self.ad_blocker = mitmproxy_adblock.Engine()

    def response(self, flow):
        flow.response.headers["x-shall-pass"] = str(self.ad_blocker.check("11111111"))


addons = [AddHeader()]
