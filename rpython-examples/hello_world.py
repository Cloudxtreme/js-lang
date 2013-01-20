# -*- encoding: utf-8 -*-


def debug(msg):
    print msg

# __________  Entry point  __________

def entry_point(argv):
    debug('Hello, World!')
    return 0

# _____ Define and setup target ___

def target(*args):
    return entry_point, None

