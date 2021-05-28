"""
Example for using DnfBackend.packages.by_key

Run with sudo
"""

import os
import sys
import dnf
from dnfdbus.backend import DnfBackend

# check for root
if os.geteuid() != 0:
    print(f"must be run as root, Use : \n    sudo python {sys.argv[0]}")
    sys.exit(-1)

b = DnfBackend(dnf.Base())
pkgs = b.packages
res = pkgs.by_key("*qt6*")
for pkg in res:
    print(f'    "{str(pkg)}",')
