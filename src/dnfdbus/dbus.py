from dasbus.server.interface import dbus_interface
from dasbus.typing import Str

VERSION = "1.0"

@dbus_interface("dk.rasmil.DnfDbus")
class DnfDbus(object):

    def Version(self) -> Str:
        return f'Version : {VERSION}'

if __name__ == "__main__":
    print(DnfDbus.__dbus_xml__)

