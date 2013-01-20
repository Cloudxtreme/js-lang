# -*- encoding: utf-8 -*-

''' Execute ./jss-c <filename>
'''

import sys
from pypy.rlib.streamio import open_file_as_stream

from jss_interp.interpreter import main


def entry_point(argv):
    if not len(argv) == 2:
        print __doc__
        return 1
    f = open_file_as_stream(argv[1])
    source = f.readall()
    f.close()
    return main(source)


def target(driver, args):
    return entry_point, None


if __name__ == '__main__':
    entry_point(sys.argv)

