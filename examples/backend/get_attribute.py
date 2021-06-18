"""
Example for using DnfBackend.get_attribute()

Run with sudo
"""

import os
import sys
from pprint import pprint

import dnf
from dnfdbus.backend import DnfBackend

# check for root
if os.geteuid() != 0:
    print(f"must be run as root, Use : \n    sudo python {sys.argv[0]}")
    sys.exit(-1)

b = DnfBackend(dnf.Base())

pkg = 'qt6-assistant-6.1.0-2.fc34.x86_64'
print(f'\n====> get_attribute({pkg})\n')
res = b.get_attribute(pkg,"", 'description')
print("RESULT:")
pprint(res)
pkg = 'qt6-assistant-6.1.0-2.fc34.x86_64'
print(f'\n====> get_attribute({pkg})\n')
res = b.get_attribute(pkg, "", 'description')
print("RESULT:")
pprint(res)
