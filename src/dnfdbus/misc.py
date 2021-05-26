import logging
import sys

log = logging.getLogger('dnfdbus.common')


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


def do_log_setup(logroot='dnfdnus', logfmt='%(asctime)s: %(message)s',
                      loglvl=logging.INFO):
    """Setup Python logging."""
    log = logging.getLogger(logroot)
    log.setLevel(loglvl)
    formatter = logging.Formatter(logfmt, "%H:%M:%S")
    handler = logging.StreamHandler(stream=sys.stdout)
    handler .setFormatter(formatter)
    handler.propagate = False
    log.addHandler(handler)
