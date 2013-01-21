# -*- encoding: utf-8 -*-

from jss_interp import parser
from jss_interp import bytecode
from jss_interp.types import W_FloatObject, OperationalError
from jss_interp.builtins import BUILTINS


class Frame(object):
    def __init__(self, bc):
        self.valuestack = []
        self.names = bc.names
        self.vars = [None] * len(self.names)

    def push(self, v):
        self.valuestack.append(v)
    
    def pop(self):
        return self.valuestack.pop()


def execute(frame, bc):
    code = bc.code
    pc = 0
    while True:
        c = ord(code[pc])
        arg = ord(code[pc + 1])
        pc += 2

        if c == bytecode.LOAD_CONSTANT:
            frame.push(W_FloatObject(bc.constants[arg]))

        elif c == bytecode.LOAD_VAR:
            # TODO - maybe move this logic to some other place?
            value = frame.vars[arg]
            if value is None:
                name = frame.names[arg]
                value = BUILTINS.get(name)
                if value is None:
                    raise OperationalError(
                            'Variable "%s" is not defined' % name)
            frame.push(value)

        elif c == bytecode.ASSIGN:
            frame.vars[arg] = frame.pop()

        elif c == bytecode.DISCARD_TOP:
            frame.pop()

        elif c == bytecode.BINARY_ADD:
            right = frame.pop()
            left = frame.pop()
            w_res = left.add(right)
            frame.push(w_res)

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
            arg = frame.pop()
            fn = frame.pop()
            frame.push(fn.call(arg))

        elif c == bytecode.RETURN:
            return

        else:
            assert False


def main(source):
    try:
        ast = parser.parse(source)
    except parser.LexerError as e:
        print 'LexerError', e
        return 1
    except parser.ParseError as e: 
        print 'ParseError', e
        return 1
    else:
        bc = bytecode.compile_ast(ast)
        interpret(bc)
        return 0


def interpret(bc):
    frame = Frame(bc)
    execute(frame, bc)
    return frame
