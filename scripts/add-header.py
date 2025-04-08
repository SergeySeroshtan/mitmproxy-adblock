"""Add an HTTP header to each response."""
import mitmproxy_adblock

class Person:
    def __init__(self, name):
        self.name = name

class AddHeader:
    def __init__(self):
        self.num = 0

    def response(self, flow):
        self.num = self.num + 1
        flow.response.headers["count"] = mitmproxy_adblock.__version__
        person = Person("John Doe")
        flow.response.headers["x-mitmproxy"] = mitmproxy_adblock.print_name(person)


addons = [AddHeader()]
