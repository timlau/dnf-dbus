""" Client Module"""

from typing import List
from dasbus.connection import SystemMessageBus
from dasbus.identifier import DBusServiceIdentifier
from dasbus.typing import Str
from gi.repository import GLib
import json

from dnfdbus.misc import to_nevra

# Constants
DNFDBUS = DBusServiceIdentifier(
    namespace=("dk", "rasmil", "DnfDbus"),
    message_bus=SystemMessageBus()
)

class DnfRepo:
    def __init__(self, attr) -> None:
        self.id:str = None
        self.name: str = None
        self.enabled:bool = None
        self.__dict__.update(attr)

class DnfPkg:
    def __init__(self, pkg) -> None:
        self.n,self.e,self.v,self.r,self.a = to_nevra(pkg)

    def __repr__(self) -> str:
        if self.e == '0':
            return f'{self.n}-{self.v}-{self.r}.{self.a}'
        else:
            return f'{self.n}-{self.e}:{self.v}-{self.r}.{self.a}'

    @property
    def name(self):
        return self.n

    @property
    def version(self):
        return self.v

    @property
    def release(self):
        return self.r

    @property
    def arch(self):
        return self.a

    @property
    def epoch(self):
        return self.e

# Classes
class DnfDbusClient:
    """Wrapper class for the dk.rasmil.DnfDbus Dbus object"""
    def __init__(self):
        self.proxy = DNFDBUS.get_proxy()

    def get_version(self) -> str:
        """ Read a Xfconf property"""
        return self.proxy.Version()

    def quit(self) -> None:
        """ Read a Xfconf property"""
        self.proxy.Quit()

    def get_repositories(self) -> List:
        repos = json.loads(self.proxy.GetRepositories())
        return [DnfRepo(repo) for repo in repos]

    def get_packages_by_key(self, key: Str) -> List:
        pkgs = json.loads(self.proxy.GetPackagesByKey(key))
        return [DnfPkg(pkg) for pkg in pkgs]


