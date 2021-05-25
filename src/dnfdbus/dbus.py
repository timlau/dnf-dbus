from dasbus.server.interface import dbus_interface
from dasbus.typing import Str

VERSION = "1.0"

@dbus_interface("dk.rasmil.DnfDbus")
class DnfDbus(object):

    def __init__(self, loop) -> None:
        super().__init__()
        self.loop = loop

    def Version(self) -> Str:
        return f'Version : {VERSION}'

    def Quit(self) -> None:
        self.loop.quit()

if __name__ == "__main__":
    print(DnfDbus.__dbus_xml__)

