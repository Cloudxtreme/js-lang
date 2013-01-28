# -*- encoding: utf-8 -*-

from jss_interp import parser
from jss_interp import bytecode
from jss_interp.base_objects import OperationalError, \
        W_FloatObject, W_Function, W_BuilinFunction
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

        if c == bytecode.LOAD_CONSTANT_FLOAT:
            frame.push(W_FloatObject(bc.constants_float[arg]))

        elif c == bytecode.LOAD_CONSTANT_FN:
            frame.push(W_Function(bc.constants_fn[arg]))

        elif c == bytecode.LOAD_VAR:
            # TODO - maybe move this logic to some other place?
            value = frame.vars[arg]
            if value is None:
                name = frame.names[arg]
                value = BUILTINS.get(name, None)
                if value is None:
                    raise OperationalError(
                            'Variable "%s" is not defined' % name)
            frame.push(value)

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
                frame.push(call_fn(fn, arg_list))

        elif c == bytecode.RETURN:
            if arg:
                return frame.pop()
            else:
                return None # TODO - undefined

        else:
            assert False


def call_fn(fn, arg_list):
    # TODO - pass arg_list - set names and vars
    frame = Frame(fn.bytecode)
    return execute(frame, fn.bytecode)


def interpret(bc):
    #print bytecode.dis(bc.code)
    frame = Frame(bc)
    execute(frame, bc)
    return frame


def interpret_source(source):
    ast = parser.parse(source)
    bc = bytecode.compile_ast(ast)
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
