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
dnfdbus.backend.packages module
"""

import dnf


class DnfPkg:
    """ Wrapper for dnf po"""

    def __init__(self, pkg) -> None:
        self.pkg = pkg

    def __str__(self):
        if self.epoch == '0':
            return f'{self.name}-{self.version}-{self.release}.{self.arch}'
        else:
            return f'{self.name}-{self.epoch}:{self.version}-{self.release}.{self.arch}'

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
    def reponame(self):
        return self.pkg.reponame

    @property
    def summary(self):
        return self.pkg.summary

    @property
    def description(self):
        return self.pkg.description

    @property
    def size(self):
        return self.pkg.downloadsize or self.pkg.installsize

    @property
    def changelog(self) -> dict:
        return self.pkg.changelogs

    @property
    def dump_list(self):
        return [str(self.pkg), self.reponame, self.summary, self.size]

    @property
    def dump(self) -> str:
        return [str(self.pkg), self.reponame]


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

    def find_pkg(self, nevra, reponame):
        """ find packages the match a nevra and reponame """
        self.backend.setup()
        if reponame == "":
            reponame = None
        subject = dnf.subject.Subject(nevra)  # type: ignore
        q = subject.get_best_selector(
            self.base.sack, reponame=reponame).matches()
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
