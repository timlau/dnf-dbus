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
dnfdbus.backend module
"""

import dnf

from .groups import DnfComps
from .packages import DnfPackages
from .repo import DnfRepository
from dnfdbus.misc import log


class DnfBackend:

    def __init__(self, base=None) -> None:
        self.base = base or dnf.Base()
        self.is_setup = False
        self._changelogs = False
        self._packages = None
        self._groups = None
        self._repo_setup = False

    @property
    def groups(self):
        if not self._groups:
            self._groups = DnfComps(self)
        return self._groups
    
    @property
    def packages(self):
        """ Get tha package object"""
        if not self._packages:
            self._packages = DnfPackages(self)
        return self._packages

    def setup(self, changelogs=False, refresh=False, cache=False):
        """ Setup Dnf load repository info & fill the sack """
        if not self.is_setup or refresh:
            log.debug(f'setup: {refresh=} {cache=} {changelogs=}')
            if not self._repo_setup: # only setup repos once
                _ = self.base.read_all_repos()
                self._repo_setup = True
            if changelogs:
                for repo in self.base.repos.iter_enabled():
                    repo.load_metadata_other = True
                self._changelogs = True
            if cache:
                _ = self.base.fill_sack_from_repos_in_cache()
            else:
                _ = self.base.fill_sack()
            self.is_setup = True

    def get_repositories(self) -> list:
        """ Get list of repositories"""
        self.setup()
        return [DnfRepository(self.base.repos[repo]) for repo in self.base.repos]

    def get_attribute(self, pkg: str, reponame: str, attribute: str):
        """
        Get attribute from package(s)
        @param pkg: package key
        @param reponame: reponame ("" = all repos)
        @param attribute: attribute name to get from dnf package
        @return: list of (package, reponame, attribute values)
        """
        if attribute == 'changelog':
            if not self._changelogs:
                self.setup(changelogs=True, refresh=True)
        pkgs = self.packages.find_pkg(pkg, reponame)
        value_list = []
        for po in pkgs:
            if hasattr(po, attribute):
                value = getattr(po, attribute)
            else:
                value = None
            elem = (str(po), po.reponame, value)
            value_list.append(elem)

        return value_list
