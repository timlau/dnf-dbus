""" testing dnfdbus.DnfBackend.groups

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
categories = b.groups.categories
print(f'#  of categories : {len(categories)}')
# for cat in categories:
#     print(f'{cat.id=} {cat.name=} {cat.ui_name=} {cat.ui_description=}')
groups = b.groups.groups
print(f'#  of groups : {len(groups)}')
# for grp in groups:
#     print(f'{grp.id=} {grp.name=} {grp.ui_name=} {grp.ui_description=}')

print("========================================================================")
grp = groups[0]
print(grp.name)
print("========================================================================")
for pkg in grp.packages:
    print(f' --> {pkg.name=} : {pkg.option_type}')
    
cat = categories[0]
print("========================================================================")
print(cat.name)
print("========================================================================")
grps = b.get_group_by_category(cat.id)
pprint(grps)