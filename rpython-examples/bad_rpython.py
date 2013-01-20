# -*- encoding: utf-8 -*-


def do_add(a, b):
    return a + b


import asyncore

def make_adder():
    print asyncore
    def do_add(a, b):
        return a + b
    return do_add


string_adder = make_adder()
int_adder = make_adder()


# __________  Entry point  __________

class A(object):
    pass

def entry_point(argv):
    b = A()
    d = {'1': 1, 'b': 2}
    for k, v in d.iteritems():
        print k, v
    # class A(object): pass
    #a = [b, None]
    #a = ['a', None]
    #a = [1, 'a']
    #a = ['a', 'aaa']
    a = [(1, 'a'), (1, 'a')]
    for x in a:
        print x
    print int_adder(1, 2)
    print string_adder('a', 'b')
    return 0

# _____ Define and setup target ___

def target(*args):
    return entry_point, None

