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

""" Module with Misc. helper funtions and other stuff"""

import logging
import sys

log = logging.getLogger('dnfdbus.common')


def to_nevra(pkg):
    """ convert pkg string to NEVRA (Name, Epoch, Version, Release, Arch) """
    archIndex = pkg.rfind('.')
    a = pkg[archIndex + 1:]
    relIndex = pkg[:archIndex].rfind('-')
    r = pkg[relIndex + 1:archIndex]
    verIndex = pkg[:relIndex].rfind('-')
    v = pkg[verIndex + 1:relIndex]
    eIndex = v.find(':')
    if eIndex == -1:
        e = '0'
    else:
        e, v = v.split(':')
    n = pkg[:verIndex]
    return n, e, v, r, a


def logger(func):
    """
    This decorator that logs start of end of a called method or function
    """

    def newFunc(*args, **kwargs):
        log.debug("=> %s started args: %s " % (func.__name__, repr(args[1:])))
        rc = func(*args, **kwargs)
        log.debug("=> %s ended" % func.__name__)
        return rc

    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc


def do_log_setup(logroot='dnfdbus', logfmt='%(asctime)s: %(message)s',
                 loglvl=logging.INFO):
    """Setup Python logging."""
    log = logging.getLogger(logroot)
    log.setLevel(loglvl)
    formatter = logging.Formatter(logfmt, "%H:%M:%S")
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    log.propagate = False
    log.addHandler(handler)
