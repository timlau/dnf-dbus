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

from dasbus.connection import SystemMessageBus
from dasbus.error import DBusError, ErrorMapper, get_error_decorator
from dasbus.identifier import DBusServiceIdentifier
from dasbus.server.interface import dbus_interface, dbus_signal
from dasbus.server.publishable import Publishable
from dasbus.server.template import InterfaceTemplate
from dasbus.signal import Signal
from dasbus.typing import Str, Double

from dnfdbus.backend import DnfBackend
from dnfdbus.misc import log
from dnfdbus.polkit import DBUS_SENDER, check_permission

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


# noinspection PyPep8Naming
@dbus_interface(DNFDBUS.interface_name)
class DnfDbusInterface(InterfaceTemplate):

    def connect_signals(self):
        """Connect the signals."""
        self.implementation.signal_message.connect(self.Message)
        self.implementation.signal_progress.connect(self.Progress)
        self.implementation.signal_quitting.connect(self.Quitting)

    @property
    def Version(self) -> Str:
        """ Get Version of DBUS Daemon"""
        return self.implementation.version()

    def Quit(self) -> None:
        """ Quit the DBUS Daemon"""
        return self.implementation.quit()

    def GetRepositories(self) -> Str:
        """ Get Repositories"""
        return self.implementation.get_repositories()

    def GetPackagesByKey(self, key: Str) -> Str:
        """ Get Backages by key """
        return self.implementation.get_packages_by_key(key)

    def TestSignals(self) -> None:
        return self.implementation.test_signals()

    @dbus_signal
    def Message(self, msg: Str):  # type: ignore
        pass

    @dbus_signal
    def Progress(self, msg: Str, fraction: Double):  # type: ignore
        pass

    @dbus_signal
    def Quitting(self):  # type: ignore
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
        self._signal_message = Signal()
        self._signal_progress = Signal()
        self._signal_quitting = Signal()

    def for_publication(self):
        return DnfDbusInterface(self)

    @property
    def signal_message(self):
        return self._signal_message

    @property
    def signal_progress(self):
        return self._signal_progress

    @property
    def signal_quitting(self):
        return self._signal_quitting

# ========================= Interface Implementation ===================================
    def version(self) -> Str:
        """ Get Version of DBUS Daemon"""
        log.debug(f"Starting Version ")
        return f'Version : {VERSION}'

    def quit(self) -> None:
        """ Quit the DBUS Daemon"""
        self.working_start(write=False)
        log.info("Quiting dk.rasmil.DnfDbus")
        self.signal_quitting.emit()
        self.loop.quit()
        self.working_ended()

    def get_repositories(self) -> Str:
        """ Get Repositories"""
        self.working_start(write=False)
        log.debug("Starting GetRepository")
        repos = self.backend.get_repositories()
        return self.working_ended(json.dumps([repo.dump for repo in repos]))

    def get_packages_by_key(self, key: Str) -> Str:
        """ Get Packages by key """
        self.working_start(write=False)
        log.debug("Starting GetPackagesByKey")
        pkgs = self.backend.packages.by_key(key)
        return self.working_ended(json.dumps([pkg.dump for pkg in pkgs]))

    def test_signals(self):
        log.debug(f"Starting TestSignals")
        self.signal_progress.emit("progress", .5)
        self.signal_message.emit("some message")

# ======================= Helpers ====================================
    def working_start(self,  write=True):
        """ Check permission and set work is being done flag """
        if write:
            self.check_permission_write()
        else:
            self.check_permission_read()
        self._is_working = True

    def working_ended(self, value=None):
        """ Release work is being done flag and return the passed value """
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
