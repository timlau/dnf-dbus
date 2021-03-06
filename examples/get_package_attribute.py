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
Example for using the GetPackageAtrribute
"""
import logging
from pprint import pprint

from dnfdbus.client import DnfDbusClient
from dnfdbus.misc import do_log_setup

if __name__ == "__main__":
    # Setup client to talk to the DnfDbus Backend
    do_log_setup(loglvl=logging.DEBUG)
    with DnfDbusClient() as client:
        print(client.version)
        pkg = 'dnf'
        print(f'\n====> get_package_attribute({pkg})\n')
        res = client.get_package_attribute(pkg, '@System', 'description')
        print("RESULT:")
        pprint(res)
        res = client.get_package_attribute(pkg, '@System', 'changelog')
        print("RESULT:")
        pprint(res)
        res = client.get_package_attribute(pkg, "", 'changelog')
        print("RESULT:")
        pprint(res)
        res = client.get_package_attribute(pkg, "", 'descriptiom')
        print("RESULT:")
        pprint(res)
