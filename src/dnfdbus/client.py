""" Client Module"""

from typing import List
from dasbus.connection import SystemMessageBus
from dasbus.identifier import DBusServiceIdentifier
from gi.repository import GLib
import json

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


if __name__ == "__main__":
    client = DnfDbusClient()
    print(client.get_version())
    repos = client.get_repositories()
    for repo in repos:
        if repo.enabled:
            print(f'{repo.id:50} : {repo.name}')
    client.quit()

