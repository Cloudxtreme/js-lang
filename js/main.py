#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""Usage: js <filename>"""


import sys


from rpython.rlib.streamio import open_file_as_stream


from js.interpreter import run


def main(argv):
    if not len(argv) == 2:
        print __doc__
        return 1

    filename = argv[1]
    f = open_file_as_stream(filename)
    source = f.readall()
    f.close()

    return run(source, filename=filename)


def entrypoint():
    main(sys.argv)


if __name__ == "__main__":
    main(sys.argv)
