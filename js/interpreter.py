# -*- encoding: utf-8 -*-


from rpython.rlib import jit
from rpython.rlib.streamio import open_file_as_stream


import js
from js import bytecode
from js.bytecode import dis, CompilerContext
from js.parser import LexerError, ParseError, parse
from js .base_objects import OperationalError, \
        W_FloatObject, W_Function, W_BuilinFunction
from js .builtins import BUILTINS

from rlib.rreadline import readline


BANNER = "%s %s\n" % (js.__name__, js.__version__)
PS1 = ">>> "
PS2 = "... "


def get_printable_location(pc, code, bc):
    return '%s #%d %s' % (bc.get_repr(), pc, bytecode.dis_one(code[pc]))


jitdriver = jit.JitDriver(
    greens=['pc', 'code', 'bc'],
    reds=['frame'],
    virtualizables=['frame'],
    get_printable_location=get_printable_location)


class Frame(object):

    _virtualizable2_ = ['valuestack[*]', 'valuestack_pos', 'vars[*]',
                        'names[*]', 'parent']

    def __init__(self, bc, parent=None):
        self = jit.hint(self, fresh_virtualizable=True, access_directly=True)
        self.valuestack = [None] * 10  # TODO - get upper bound staticaly
        # TODO - or maybe have even smaller initial estimate and resize when
        # needed?
        self.valuestack_pos = 0
        self.names = bc.names
        self.vars = [None] * len(bc.names)
        self.parent = parent

    def push(self, v):
        pos = self.valuestack_pos
        assert pos >= 0
        self.valuestack[pos] = v
        self.valuestack_pos = pos + 1

    def pop(self):
        new_pos = self.valuestack_pos - 1
        assert new_pos >= 0
        v = self.valuestack[new_pos]
        self.valuestack_pos = new_pos
        return v

    def lookup(self, arg):
        value = self._lookup(arg)
        if value is None:
            name = self.names[arg]
            value = BUILTINS.get(name, None)
            if value is None:
                raise OperationalError('Variable "%s" is not defined' % name)
        return value

    def _lookup(self, arg):
        value = self.vars[arg]
        if value is not None:
            return value
        if self.parent is not None:
            name = self.names[arg]
            return self.parent.lookup_by_name(name)

    def lookup_by_name(self, name):
        # linear search
        for i, n in enumerate(self.names):
            if n == name:
                return self.vars[i]
        if self.parent:
            return self.parent.lookup_by_name(name)

    @jit.unroll_safe
    def call(self, fn, arg_list, interpreter):
        frame = Frame(fn.bytecode, parent=fn.parent_frame)
        for i, value in enumerate(arg_list):
            frame.vars[i] = value
        return interpreter.run(fn.bytecode, frame)

    @property
    def test_valuestack(self):
        ''' NOT_RPYTHON '''
        return self.valuestack[:self.valuestack_pos]


@jit.unroll_safe
def pop_args(frame, n_args):
    arg_list = []
    for _ in xrange(n_args):
        arg_list.append(frame.pop())
    return arg_list


class Interpreter(object):

    def __init__(
        self, debug=False, testing=False, banner=BANNER, ps1=PS1, ps2=PS2
    ):
        self.debug = debug
        self.testing = testing

        self.banner = banner
        self.ps1 = ps1
        self.ps2 = ps2

    def runstring(self, s, filename=None):
        ast = parse(s, filename=filename)

        bc = CompilerContext().compile_ast(ast)
        frame = Frame(bc)

        if self.debug:  # pragma: no cover
            print dis(bc.code)

        result = self.run(bc, frame)
        return frame if self.testing else result

    def runfile(self, filename):
        f = open_file_as_stream(filename)
        s = f.readall()
        f.close()

        return self.runstring(s, filename=filename)

    def repl(self, banner=None, ps1=None, ps2=None):  # pragma: no cover
        banner = banner or self.banner
        ps1 = ps1 or self.ps1
        ps2 = ps2 or self.ps2

        print banner

        while True:
            try:
                s = readline(ps1).strip()
            except EOFError:
                break

            try:
                self.runstring(s)
            except LexerError as e:
                print "LexerError: ", e
            except ParseError as e:
                print "ParseError: ", e
            except OperationalError as e:
                print e

    def run(self, bc, frame=None):  # noqa
        frame = frame or Frame(bc)
        code = bc.code
        pc = 0
        while True:

            jitdriver.jit_merge_point(
                    pc=pc, code=code, bc=bc, frame=frame)

            c = ord(code[pc])
            arg = ord(code[pc + 1])
            pc += 2

            if c == bytecode.LOAD_CONSTANT_FLOAT:
                frame.push(W_FloatObject(bc.constants_float[arg]))

            elif c == bytecode.LOAD_CONSTANT_FN:
                frame.push(W_Function(bc.constants_fn[arg], frame))

            elif c == bytecode.LOAD_VAR:
                frame.push(frame.lookup(arg))

            elif c == bytecode.ASSIGN:
                frame.vars[arg] = frame.pop()

            elif c == bytecode.DISCARD_TOP:
                frame.pop()

            # TODO - remove repition

            elif c == bytecode.BINARY_ADD:
                right = frame.pop()
                left = frame.pop()
                w_res = left.add(right)
                frame.push(w_res)

            elif c == bytecode.BINARY_SUB:
                right = frame.pop()
                left = frame.pop()
                frame.push(left.sub(right))

            elif c == bytecode.BINARY_MUL:
                right = frame.pop()
                left = frame.pop()
                frame.push(left.mul(right))

            elif c == bytecode.BINARY_DIV:
                right = frame.pop()
                left = frame.pop()
                frame.push(left.div(right))

            elif c == bytecode.BINARY_LT:
                right = frame.pop()
                left = frame.pop()
                frame.push(left.lt(right))

            elif c == bytecode.BINARY_EQ:
                right = frame.pop()
                left = frame.pop()
                frame.push(left.eq(right))

            elif c == bytecode.BINARY_MOD:
                right = frame.pop()
                left = frame.pop()
                frame.push(left.mod(right))

            elif c == bytecode.JUMP_IF_FALSE:
                if not frame.pop().is_true():
                    pc = arg

            elif c == bytecode.JUMP_ABSOLUTE:
                pc = arg

            elif c == bytecode.CALL:
                arg_list = pop_args(frame, arg)
                fn = frame.pop()
                if isinstance(fn, W_BuilinFunction):
                    frame.push(fn.call(arg_list))
                else:
                    frame.push(frame.call(fn, arg_list, self))

            elif c == bytecode.RETURN:
                if arg:
                    return frame.pop()
                else:
                    return None  # TODO - undefined

            else:
                assert False

        return frame
