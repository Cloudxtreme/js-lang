# -*- encoding: utf-8 -*-

from jss_interp import parser
from jss_interp import bytecode


class OperationalError(Exception):
    pass


class W_Root(object):
    def is_true(self):
        raise NotImplementedError

    def lt(self, other):
        raise NotImplementedError

    def eq(self, other):
        raise NotImplementedError

    def add(self, other):
        raise NotImplementedError


class W_BoolObject(W_Root):
    def __init__(self, boolval):
        self.boolval = bool(boolval)

    def is_true(self):
        return self.boolval

    def eq(self, other):
        if isinstance(other, W_BoolObject):
            return W_BoolObject(self.boolval == other.boolval)
        elif isinstance(other, W_FloatObject):
            return W_BoolObject(float(self.boolval) == other.floatval)
        else:
            return W_BoolObject(False)

    def __eq__(self, other):
        ''' NOT_RPYTHON '''
        return type(self) == type(other) and self.boolval == other.boolval


class W_FloatObject(W_Root):
    def __init__(self, floatval):
        self.floatval = floatval

    def _assert_float(self, other):
        if not isinstance(other, W_FloatObject):
            raise OperationalError(
                    'Expected a number, got %s' % type(other).__name__) 

    def is_true(self):
        return bool(self.floatval)

    def lt(self, other):
        self._assert_float(other)
        return W_BoolObject(self.floatval < other.floatval)

    def eq(self, other):
        self._assert_float(other)
        return W_BoolObject(self.floatval == other.floatval)

    def add(self, other):
        self._assert_float(other)
        return W_FloatObject(self.floatval + other.floatval)

    def __eq__(self, other):
        ''' NOT_RPYTHON '''
        return type(self) == type(other) and self.floatval == other.floatval


class Frame(object):
    def __init__(self, bc):
        self.valuestack = []
        self.vars = [None] * bc.numvars

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
        elif c == bytecode.DISCARD_TOP:
            frame.pop()
        elif c == bytecode.RETURN:
            return
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
        elif c == bytecode.PRINT:
            item = frame.pop()
            print item
        elif c == bytecode.ASSIGN:
            frame.vars[arg] = frame.pop()
        elif c == bytecode.LOAD_VAR:
            frame.push(frame.vars[arg])
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
