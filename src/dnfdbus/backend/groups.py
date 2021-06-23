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
dnfdbus.backend.groups module
"""

import dnf.comps

CONDITIONAL = dnf.comps.CONDITIONAL
DEFAULT = dnf.comps.DEFAULT
MANDATORY = dnf.comps.MANDATORY
OPTIONAL = dnf.comps.OPTIONAL


class DnfCategory:

    def __init__(self, category: dnf.comps.Category):
        self._category = category
        self._groups = {}

    def __repr__(self) -> str:
        return f'DnfCategory({self.id}, {self.name})'

    def __str__(self) -> str:
        return f'{self.name}'

    @property
    def id(self) -> str:
        return self._category.id

    @property
    def name(self) -> str:
        return self._category.name

    @property
    def ui_name(self) -> str:
        return self._category.ui_name

    @property
    def ui_description(self) -> str:
        return self._category.ui_description

    @property
    def groups(self) -> list:
        if not self._groups:
            self._load()
        return list(self._groups.values())

    def _load(self):
        for grp in self._category.groups_iter():
            group = DnfGroup(self.id, grp)
            self._groups[group.id] = group


class DnfGrpPackage:

    def __init__(self, pkg: dnf.comps.Package):
        self._pkg = pkg

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'DnfGrpPackage({self.name})'

    @property
    def name(self):
        return self._pkg.name

    @property
    def option_type(self):
        return self._pkg.option_type


class DnfGroup:
    """ Dnf group wrapper """

    def __init__(self, category: DnfCategory, group: dnf.comps.Group):
        self._category = category
        self._group = group
        self._packages = []

    def __repr__(self) -> str:
        return f'DnfGroup({self.id}, {self.name})'

    def __str__(self) -> str:
        return f'{self.name}'

    @property
    def id(self) -> str:
        return self._group.id

    @property
    def name(self) -> str:
        return self._group.name

    @property
    def ui_name(self) -> str:
        return self._group.ui_name

    @property
    def ui_description(self) -> str:
        return self._group.ui_description
    
    @property
    def packages(self) -> list:
        if not self._packages:
            self._load()
        return self._packages

    def _load(self):
        for pkg in self._group.packages_iter():
            package = DnfGrpPackage(pkg)
            self._packages.append(package)


class DnfComps:
    """ Wrapper for dnf comps """

    def __init__(self, backend):
        self._backend = backend
        self._base = backend.base
        self._categories = {}
        self._groups = {}
        self.setup()

    def setup(self):
        self._backend.setup()
        self._base.read_comps()

    @property
    def comps(self) -> dnf.comps.Comps:
        return self._base.comps

    def _load(self):
        for cat in self.comps.categories_iter():
            category = DnfCategory(cat)
            self._categories[category.id] = category
            for grp in category.groups:
                self._groups[grp.id] = grp

    @property
    def catagories(self) -> list:
        if not self._categories:
            self._load()
        return list(self._categories.values())

    @property
    def groups(self) -> list:
        if not self._groups:
            self._load()
        return list(self._groups.values())
