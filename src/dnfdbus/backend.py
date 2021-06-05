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

"""
dnfdbus.dnf module
"""
import dnf


class DnfRepository:
    """
    Wrapper for the dnf.repo.Repo class
    """

    def __init__(self, repo) -> None:
        self.repo = repo

    @property
    def id(self):
        return self.repo.id

    @property
    def name(self):
        return self.repo.name

    @property
    def enabled(self):
        return self.repo.enabled

    @property
    def dump(self) -> dict:
        return {'id': self.id, 'name': self.name, 'enabled': self.enabled}


class DnfPkg:
    """ Wrapper for dnf po"""

    def __init__(self, pkg) -> None:
        self.pkg = pkg

    def __str__(self):
        return str(self.pkg)

    def __repr__(self):
        return f'DnfPkg({str(self.pkg)})'

    @property
    def name(self):
        return self.pkg.name

    @property
    def version(self):
        return self.pkg.version

    @property
    def release(self):
        return self.pkg.release

    @property
    def arch(self):
        return self.pkg.arch

    @property
    def epoch(self):
        return self.pkg.epoch

    @property
    def dump(self) -> str:
        return str(self.pkg)


class DnfPackages:

    def __init__(self, backend) -> None:
        self.backend = backend
        self.base = backend.base

    @property
    def installed(self):
        """ Get list of installed packages"""
        self.backend.setup()
        q = self.base.sack.query()
        q = q.installed()
        return [DnfPkg(pkg) for pkg in q]

    @property
    def available(self):
        """ Get list of lastest available packages"""
        self.backend.setup()
        q = self.base.sack.query().available().latest()
        return [DnfPkg(pkg) for pkg in q]

    @property
    def available_all(self):
        """ Get list of all available packages"""
        self.backend.setup()
        q = self.base.sack.query()
        q = q.available()
        return [DnfPkg(pkg) for pkg in q]

    @property
    def updates(self):
        """ Get list of all available packages"""
        self.backend.setup()
        q = self.base.sack.query()
        q = q.upgrades().latest()
        return [DnfPkg(pkg) for pkg in q]

    def by_key(self, key):
        """ find packages the match a key (Ex. '*qt6*') """
        self.backend.setup()
        subject = dnf.subject.Subject(key)  # type: ignore
        q = subject.get_best_query(self.base.sack)
        return [DnfPkg(pkg) for pkg in q]

    def by_filter(self, flt):
        """ find packages the match a key (Ex. '*qt6*') """
        self.backend.setup()
        if flt == 'installed':
            return self.installed
        if flt == 'available':
            return self.available
        if flt == 'updates':
            return self.updates
        else:
            return []


class DnfBackend:

    def __init__(self, base=None) -> None:
        self.base = base or dnf.Base()
        self.is_setup = False
        self._packages = None

    @property
    def packages(self):
        """ Get tha package object"""
        if not self._packages:
            self._packages = DnfPackages(self)
        return self._packages

    def setup(self):
        """ Setup Dnf load repository info & fill the sack """
        if not self.is_setup:
            _ = self.base.read_all_repos()
            _ = self.base.fill_sack_from_repos_in_cache()
            self.is_setup = True

    def get_repositories(self) -> list:
        """ Get list of repositories"""
        self.setup()
        return [DnfRepository(self.base.repos[repo]) for repo in self.base.repos]
