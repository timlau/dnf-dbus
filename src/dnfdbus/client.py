""" Client API Module"""
import json
from typing import List, Dict

from dasbus.connection import SystemMessageBus
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

from dasbus.identifier import DBusServiceIdentifier

from dnfdbus.misc import to_nevra
from dnfdbus.server import SYSTEM_BUS, DNFDBUS


class DnfRepo:
    """ Wrapper class for a dnf repository"""
    def __init__(self, attr: Dict) -> None:
        self.id:str = None
        self.name: str = None
        self.enabled:bool = None
        self.__dict__.update(attr)

class DnfPkg:
    """ Wrapper class for a dnf package"""
    def __init__(self, pkg: str) -> None:
        self.n,self.e,self.v,self.r,self.a = to_nevra(pkg)

    def __repr__(self) -> str:
        if self.e == '0':
            return f'{self.n}-{self.v}-{self.r}.{self.a}'
        else:
            return f'{self.n}-{self.e}:{self.v}-{self.r}.{self.a}'

    @property
    def name(self)-> str:
        return self.n

    @property
    def version(self)-> str:
        return self.v

    @property
    def release(self)-> str:
        return self.r

    @property
    def arch(self)-> str:
        return self.a

    @property
    def epoch(self)-> str:
        return self.e

# Classes
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

    def get_repositories(self) -> List:
        """ Get all configured repositories """
        repos = json.loads(self.proxy.GetRepositories())
        return [DnfRepo(repo) for repo in repos]

    def get_packages_by_key(self, key: str) -> List:
        """ Get packages that matches a key """
        pkgs = json.loads(self.proxy.GetPackagesByKey(key))
        return [DnfPkg(pkg) for pkg in pkgs]


