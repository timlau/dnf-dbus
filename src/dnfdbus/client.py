""" Client Module"""

from dasbus.connection import SystemMessageBus
from dasbus.identifier import DBusServiceIdentifier
from gi.repository import GLib

# Constants
DNFDBUS = DBusServiceIdentifier(
    namespace=("dk", "rasmil", "DnfDbus"),
    message_bus=SystemMessageBus()
)

# Classes
class DnfDbusClient:
    """Wrapper class for the dk.rasmil.DnfDbus Dbus object"""
    def __init__(self):
        self.proxy = DNFDBUS.get_proxy()

    def get_version(self) -> str:
        """ Read a Xfconf property"""
        return self.proxy.Version()

if __name__ == "__main__":
    client = DnfDbusClient()
    print(client.get_version())
