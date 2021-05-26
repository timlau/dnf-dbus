from typing import List
from dasbus.server.interface import dbus_interface
from dasbus.typing import Str
from dnfdbus.backend import DnfBackend
from dnfdbus.misc import log
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
        log.debug("Starting Version")
        return f'Version : {VERSION}'

    def Quit(self) -> None:
        log.info("Quiting dk.rasmil.DnfDbus")
        self.loop.quit()

    def GetRepositories(self) -> Str:
        log.debug("Starting GetRepository")
        repos = self.backend.get_repositories()
        return json.dumps([repo.dump for repo in repos])

    def GetPackagesByKey(self, key: Str) -> Str:
        log.debug("Starting GetPackagesByKey")
        pkgs = self.backend.packages.by_key(key)
        return json.dumps([pkg.dump for pkg in pkgs])

if __name__ == "__main__":
    print(DnfDbus.__dbus_xml__)

