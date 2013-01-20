# -*- encoding: utf-8 -*-

''' Execute ./jss-c <filename>
'''

import sys
from pypy.rlib.streamio import open_file_as_stream

from jss_interp.parser import parse


def main(argv):
    if not len(argv) == 2:
        print __doc__
        return 1
    f = open_file_as_stream(argv[1])
    data = f.readall()
    f.close()
    print parse(data)
    return 0


def target(driver, args):
    return main, None


if __name__ == '__main__':
    main(sys.argv)

