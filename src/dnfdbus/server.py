#    Copyright (C) 2021 Tim Lauridsen < tla[at]rasmil.dk >
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to
#    the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

""" Module for DBus Backend Daemon """

import json

from dasbus.server.interface import dbus_interface, dbus_signal
from dasbus.connection import SystemMessageBus
from dasbus.identifier import DBusServiceIdentifier
from dasbus.server.template import InterfaceTemplate
from dasbus.server.publishable import Publishable
from dasbus.error import ErrorMapper, get_error_decorator, DBusError
from dasbus.loop import EventLoop
from dasbus.typing import Str

from dnfdbus.backend import DnfBackend
from dnfdbus.misc import log
from dnfdbus.polkit import check_permission, DBUS_SENDER

# Constants
SYSTEM_BUS = SystemMessageBus()

DNFDBUS_NAMESPACE = ("dk", "rasmil", "DnfDbus")

DNFDBUS = DBusServiceIdentifier(
    namespace=DNFDBUS_NAMESPACE,
    message_bus=SYSTEM_BUS
)

VERSION = "1.0"

# Create an error mapper.
ERROR_MAPPER = ErrorMapper()

# Create a decorator for DBus errors and use it to map
# the class ExampleError to the name my.example.Error.
dbus_error = get_error_decorator(ERROR_MAPPER)


@dbus_error("AccessDeniedError", namespace=DNFDBUS_NAMESPACE)
class AccessDeniedError(DBusError):
    pass

# DBus interface
# Only contains the CamelCase method there is published to DBus


@dbus_interface(DNFDBUS.interface_name)
class DnfDbusInterface(InterfaceTemplate):

    @property
    def Version(self) -> Str:
        ''' Get Version of DBUS Daemon'''
        return self.implementation.version()

    def Quit(self) -> None:
        ''' Quit the DBUS Daemon'''
        return self.implementation.quit()

    def GetRepositories(self) -> Str:
        ''' Get Repositories'''
        return self.implementation.get_repositories()

    def GetPackagesByKey(self, key: Str) -> Str:
        ''' Get Backages by key '''
        return self.implementation.get_packages_by_key(key)

    @dbus_signal
    def Message(msg: Str):  # type: ignore
        pass

    @dbus_signal
    def Progress(msg: Str, fraction: float):  # type: ignore
        pass


# Implementation of the DnfDbusInterface


class DnfDbus(Publishable):

    def __init__(self, loop) -> None:
        super().__init__()
        self.authorized_sender_read = set()
        self.authorized_sender_write = set()
        self._is_working = False
        self.loop = loop
        self.backend = DnfBackend()

    def for_publication(self):
        return DnfDbusInterface(self)

# ========================= Interface Implementation ===================================
    def version(self) -> Str:
        ''' Get Version of DBUS Daemon'''
        log.debug(f"Starting Version ")
        return f'Version : {VERSION}'

    def quit(self) -> None:
        ''' Quit the DBUS Daemon'''
        self.working_start(write=False)
        log.info("Quiting dk.rasmil.DnfDbus")
        self.loop.quit()
        self.working_ended()

    def get_repositories(self) -> Str:
        ''' Get Repositories'''
        self.working_start(write=False)
        log.debug("Starting GetRepository")
        repos = self.backend.get_repositories()
        return self.working_ended(json.dumps([repo.dump for repo in repos]))

    def get_packages_by_key(self, key: Str) -> Str:
        ''' Get Backages by key '''
        self.working_start(write=False)
        log.debug("Starting GetPackagesByKey")
        pkgs = self.backend.packages.by_key(key)
        return self.working_ended(json.dumps([pkg.dump for pkg in pkgs]))

# ======================= Helpers ====================================

    def working_start(self,  write=True):
        ''' Check permission and set work is being done flag '''
        if write:
            self.check_permission_write()
        else:
            self.check_permission_read()
        self._is_working = True

    def working_ended(self, value=None):
        ''' Release work is being done flag and return the passed value '''
        self._is_working = False
        return value

    def check_permission_write(self):
        """ Check for senders permission to update system packages"""
        if DBUS_SENDER in self.authorized_sender_write:
            return
        else:
            permission = 'dk.rasmil.DnfDbus.write'
            granted = check_permission(permission)
            log.debug(
                f'PolicyKit1 {permission} : granted : {granted} sender: {DBUS_SENDER}')
            if granted:
                self.authorized_sender_write.add(DBUS_SENDER)
            else:
                raise AccessDeniedError

    def check_permission_read(self):
        """ Check for senders permission to read system packages"""
        if DBUS_SENDER in self.authorized_sender_read:
            return
        else:
            permission = 'dk.rasmil.DnfDbus.read'
            granted = check_permission(permission)
            log.debug(
                f'PolicyKit1 {permission} : granted : {granted} sender: {DBUS_SENDER}')
            if granted:
                self.authorized_sender_read.add(DBUS_SENDER)
            else:
                raise AccessDeniedError
