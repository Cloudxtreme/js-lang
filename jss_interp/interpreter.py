# -*- encoding: utf-8 -*-

from jss_interp import parser
from jss_interp import bytecode
from jss_interp.base_objects import OperationalError, \
        W_FloatObject, W_Function, W_BuilinFunction
from jss_interp.builtins import BUILTINS


class Frame(object):
    def __init__(self, bc, parent=None):
        self.valuestack = []
        self.names = bc.names
        self.vars = [None] * len(self.names)
        self.parent = parent

    def push(self, v):
        self.valuestack.append(v)
    
    def pop(self):
        return self.valuestack.pop()

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
        try:
            return self.vars[self.names.index(name)]
        except ValueError:
            if self.parent:
                return self.parent.lookup_by_name(name)

    def call(self, fn, arg_list):
        frame = Frame(fn.bytecode, parent=fn.parent_frame)
        for i, value in enumerate(arg_list):
            frame.vars[i] = value
        return execute(frame, fn.bytecode)


def execute(frame, bc):
    #print '\n', bytecode.dis(bc.code), '\n'
    code = bc.code
    pc = 0
    while True:
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

        elif c == bytecode.JUMP_IF_FALSE:
            if not frame.pop().is_true():
                pc = arg

        elif c == bytecode.JUMP_ABSOLUTE:
            pc = arg

        elif c == bytecode.CALL:
            arg_list = []
            for _ in xrange(arg):
                arg_list.append(frame.pop())
            fn = frame.pop()
            if isinstance(fn, W_BuilinFunction):
                frame.push(fn.call(arg_list))
            else:
                frame.push(frame.call(fn, arg_list))

        elif c == bytecode.RETURN:
            if arg:
                return frame.pop()
            else:
                return None # TODO - undefined

        else:
            assert False


def interpret(bc):
    frame = Frame(bc)
    execute(frame, bc)
    return frame


def interpret_source(source):
    ast = parser.parse(source)
    bc = bytecode.CompilerContext.compile_ast(ast)
    return interpret(bc)


def main(source):
    try:
        interpret_source(source)
    except parser.LexerError as e:
        print 'LexerError', e
        return 1
    except parser.ParseError as e: 
        print 'ParseError', e
        return 1
    else:
        return 0
