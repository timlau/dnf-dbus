from typing import List
from dasbus.server.interface import dbus_interface
from dasbus.typing import Str
from dnfdbus.backend import DnfBackend
from dnf import Base

import json

VERSION = "1.0"

@dbus_interface("dk.rasmil.DnfDbus")
class DnfDbus(object):

    def __init__(self, loop) -> None:
        super().__init__()
        self.loop = loop
        self.backend = DnfBackend(Base())

    def Version(self) -> Str:
        return f'Version : {VERSION}'

    def Quit(self) -> None:
        self.loop.quit()

    def GetRepositories(self) -> Str:
        repos = self.backend.get_repositories()
        return json.dumps([repo.dump for repo in repos])

if __name__ == "__main__":
    print(DnfDbus.__dbus_xml__)

