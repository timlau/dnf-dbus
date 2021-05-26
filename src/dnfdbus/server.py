from typing import List

from dasbus.server.interface import dbus_interface
from dasbus.connection import SystemMessageBus
from dasbus.identifier import DBusServiceIdentifier
from dasbus.error import ErrorMapper, get_error_decorator, DBusError
from dasbus.loop import EventLoop
from dasbus.typing import Str
from dnf import Base

from dnfdbus.backend import DnfBackend
from dnfdbus.misc import log
from dnfdbus.polkit import check_permission, DBUS_SENDER


import json

VERSION = "1.0"

# Create an error mapper.
error_mapper = ErrorMapper()

# Create a decorator for DBus errors and use it to map
# the class ExampleError to the name my.example.Error.
dbus_error = get_error_decorator(error_mapper)

@dbus_error("dk.rasmil.DnfDbus.Error")
class AccessDeniedError(DBusError):
    pass

@dbus_interface("dk.rasmil.DnfDbus")
class DnfDbus(object):

    def __init__(self, loop) -> None:
        super().__init__()
        self.authorized_sender_read = set()
        self.authorized_sender_write = set()
        self._is_working = False
        self.loop = loop
        self.backend = DnfBackend(Base())

    def Version(self) -> Str:
        log.debug("Starting Version")
        return f'Version : {VERSION}'

    def Quit(self) -> None:
        self.working_start(write=False)
        log.info("Quiting dk.rasmil.DnfDbus")
        self.loop.quit()
        self.working_ended()

    def GetRepositories(self) -> Str:
        self.working_start(write=False)
        log.debug("Starting GetRepository")
        repos = self.backend.get_repositories()
        return self.working_ended(json.dumps([repo.dump for repo in repos]))

    def GetPackagesByKey(self, key: Str) -> Str:
        self.working_start(write=False)
        log.debug("Starting GetPackagesByKey")
        pkgs = self.backend.packages.by_key(key)
        return self.working_ended(json.dumps([pkg.dump for pkg in pkgs]))

# ======================= Helpers ====================================

    def working_start(self,  write=True):
        if write:
            self.check_permission_write()
        else:
            self.check_permission_read()
        self._is_working = True

    def working_ended(self, value=None):
        self._is_working = False
        return value

    def check_permission_write(self):
        """ Check for senders permission to update system packages"""
        if DBUS_SENDER in self.authorized_sender_write:
            return
        else:
            permission = 'dk.rasmil.DnfDbus.write'
            granted = check_permission(permission)
            log.debug(f'PolicyKit1 {permission} : granted : {granted} sender: {DBUS_SENDER}')
            if granted:
                self.authorized_sender_write.add(DBUS_SENDER)

    def check_permission_read(self):
        """ Check for senders permission to read system packages"""
        if DBUS_SENDER in self.authorized_sender_read:
            return
        else:
            permission = 'dk.rasmil.DnfDbus.read'
            granted = check_permission(permission)
            log.debug(f'PolicyKit1 {permission} : granted : {granted} sender: {DBUS_SENDER}')
            if granted:
                self.authorized_sender_read.add(DBUS_SENDER)

