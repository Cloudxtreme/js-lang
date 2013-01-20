# -*- encoding: utf-8 -*-


def fib(n):
    if n <= 2:
        return n
    else:
        return fib(n - 1) + fib(n - 2)


# __________  Entry point  __________

def entry_point(argv):
    if len(argv) == 2:
        print fib(int(argv[1]))
    else:
        print 'usage: fib-c <number>'
    return 0

# _____ Define and setup target ___

def target(*args):
    return entry_point, None


def test():
    assert fib(3) == 3
    assert fib(5) == 8


if __name__ == '__main__':
    import sys
    entry_point(sys.argv)
