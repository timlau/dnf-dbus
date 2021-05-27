""" Module with Misc. helper funtions and other stuff"""

import logging
import sys
import re

log = logging.getLogger('dnfdbus.common')

NEVRA_RE = re.compile(r'([a-z0-9_\-]*)(-([0-9]*):|-)([0-9\.]*)-([0-9a-z\.]*)\.([a-z0-9_]*)$',re.IGNORECASE)


def to_nevra(pkg):
    ''' convert pkg string to NEVRA (Name, Epoch, Version, Release, Arch) '''
    match = NEVRA_RE.search(pkg)
    n = match.group(1)
    if match.group(3):
        e = match.group(3)
    else:
        e = '0'
    v = match.group(4)
    r = match.group(5)
    a = match.group(6)
    #print(f'{n=} {e=} {v=} {r=} {a=}')
    return n,e,v,r,a


def logger(func):
    """
    This decorator that logs start of end of a called method or function
    """
    def newFunc(*args, **kwargs):
        log.debug("%s started args: %s " % (func.__name__, repr(args[1:])))
        rc = func(*args, **kwargs)
        log.debug("%s ended" % func.__name__)
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
    handler .setFormatter(formatter)
    handler.propagate = False
    log.addHandler(handler)
