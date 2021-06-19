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
dnfdbus.backend.repo module
"""


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
