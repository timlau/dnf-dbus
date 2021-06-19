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

from dnfdbus.misc import to_nevra
from dnfdbus.server import DNFDBUS
from dasbus.loop import EventLoop


@dataclass(repr=True)
class Repository:
    """ Wrapper class for a dnf repository"""
    id: str
    name: str
    enabled: bool

    def __init__(self, attr: dict) -> None:
        self.__dict__.update(attr)


@dataclass
class Package:
    """ Wrapper class for a dnf package"""
    name: str
    epoch: str
    version: str
    release: str
    arch: str
    reponame: str
    summary: str = ""
    size: int = 0

    def __init__(self, pkg: str, reponame: str) -> None:
        self.reponame = reponame
        self.name, self.epoch, self.version, self.release, self.arch = to_nevra(
            pkg)

    def __repr__(self) -> str:
        return f'Package({str(self)})'

    def __str__(self) -> str:
        if self.epoch == '0':
            return f'{self.name}-{self.version}-{self.release}.{self.arch}'
        else:
            return f'{self.name}-{self.epoch}:{self.version}-{self.release}.{self.arch}'


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
        print('Daemon is quitting')
        self.loop.quit()


class AsyncDbusCaller:
    def __init__(self):
        self.res = None
        self.loop = None

    def callback(self, call):
        self.res = call()
        self.loop.quit()

    def call(self, mth, *args, **kwargs):
        self.loop = EventLoop()
        mth(*args, **kwargs, callback=self.callback)
        self.loop.run()
        return self.res


class DnfDbusClient:
    """Wrapper class for the dk.rasmil.DnfDbus Dbus object"""

    def __init__(self):
        self.proxy = DNFDBUS.get_proxy()
        self.async_dbus = AsyncDbusCaller()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print(f'{exc_type=} {exc_value=} {exc_traceback=}')
        self.quit()

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
        return [Repository(repo) for repo in repos]

    def get_packages_by_key(self, key: str) -> list:
        """ Get packages that matches a key

        Args:
            key: key with wildcards for packages to matck

        Returns:
            list of packages
        """
        pkgs = json.loads(self.async_dbus.call(
            self.proxy.GetPackagesByKey, key))
        return [Package(elem[0], elem[1]) for elem in pkgs]

    def get_packages_by_filter(self, flt: str, extra: bool = False) -> list:
        """ Get packages that matches a filter

        Args:
            flt: package filter ('installed', 'updates')
            extra: get extra info on packages flag (summary & size)

        Returns:
            list of packages
        """
        pkgs = json.loads(self.async_dbus.call(
            self.proxy.GetPackagesByFilter, flt, extra))
        if extra:
            res = []
            for elem in pkgs:
                pkg, repo, summary, size = elem
                po = Package(pkg, repo)
                po.summary = summary
                po.size = size
                res.append(po)
            return res
        else:
            return [Package(elem[0], elem[1]) for elem in pkgs]

    def get_package_attribute(self, pkg: str, reponame: str, attribute: str):
        """ Get Atrributes for a package filter

        Args:
            pkg: package filter (can include wildcards)
            reponame: reponame to limit to a given repo ("" = all repos)
            attribute: attribute to return

        Returns:
            list with (packagename, reponame, list of attribute values) pairs
        """
        res: str = self.async_dbus.call(
            self.proxy.GetPackageAttribute, pkg, reponame, attribute)
        res = json.loads(res)
        return res
