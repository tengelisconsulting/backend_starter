from types import SimpleNamespace

from ez import EzRequester


class App(SimpleNamespace):
    ez: EzRequester


app = App()
