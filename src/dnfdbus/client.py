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

""" Module for client code to talk with the DBus Backend daemon"""


import json
from dataclasses import dataclass

from dasbus.connection import SystemMessageBus
from dasbus.identifier import DBusServiceIdentifier

from dnfdbus.misc import to_nevra
from dnfdbus.server import DNFDBUS, SYSTEM_BUS
from dasbus.loop import EventLoop


@dataclass(repr=True)
class DnfRepo:
    """ Wrapper class for a dnf repository"""
    id: str
    name: str
    enabled: bool

    def __init__(self, attr: dict) -> None:
        self.__dict__.update(attr)


@dataclass
class DnfPkg:
    """ Wrapper class for a dnf package"""
    name: str
    epoch: str
    version: str
    release: str
    arch: str

    def __init__(self, pkg: str) -> None:
        self.name, self.epoch, self.version, self.release, self.arch = to_nevra(
            pkg)

    def __repr__(self) -> str:
        if self.epoch == '0':
            return f'{self.name}-{self.version}-{self.release}.{self.arch}'
        else:
            return f'{self.name}-{self.epoch}:{self.version}-{self.release}.{self.arch}'

    def __str__(self) -> str:
        return self.__repr__()


# Classes

class DnfDbusSignals:
    SIGNALS = ['Message', 'Progress']

    def __init__(self, loop: EventLoop):
        self.proxy = DNFDBUS.get_proxy()
        self.proxy.Message.connect(self.message)
        self.proxy.Progress.connect(self.progress)
        self.proxy.Quitting.connect(self.quitting)
        self.loop = loop

    def message(self, msg: str):
        print(f'Message: {msg=}')

    def progress(self, msg: str, fraction: float):
        print(f'Progress: {msg=} {fraction=}')

    def quitting(self):
        self.loop.quit()


class DnfDbusClient:
    """Wrapper class for the dk.rasmil.DnfDbus Dbus object"""

    def __init__(self):
        self.proxy = DNFDBUS.get_proxy()

    @property
    def version(self) -> str:
        """ Get the version from dk.rasmil.DnfDbus daemon"""
        return self.proxy.Version

    def quit(self) -> None:
        """ Quit the dk.rasmil.DnfDbus daemon"""
        self.proxy.Quit()

    def get_repositories(self) -> list:
        """ Get all configured repositories """
        repos = json.loads(self.proxy.GetRepositories())
        return [DnfRepo(repo) for repo in repos]

    def get_packages_by_key(self, key: str) -> list:
        """ Get packages that matches a key """
        pkgs = json.loads(self.proxy.GetPackagesByKey(key))
        return [DnfPkg(pkg) for pkg in pkgs]
