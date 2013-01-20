# -*- encoding: utf-8 -*-


LOAD_CONSTANT, LOAD_VAR, ASSIGN, \
DISCARD_TOP, RETURN, JUMP_IF_FALSE, JUMP_BACKWARD, \
BINARY_ADD, BINARY_SUB, BINARY_EQ, BINARY_LT, \
PRINT \
= range(12)


BINOP = {'+': BINARY_ADD, '-': BINARY_SUB, '==': BINARY_EQ, '<': BINARY_LT}


class CompilerContext(object):
    def __init__(self):
        self.data = []
        self.constants = []
        self.names = []
        self.names_to_numbers = {}

    def register_constant(self, v):
        self.constants.append(v)
        return len(self.constants) - 1

    def register_var(self, name):
        try:
            return self.names_to_numbers[name]
        except KeyError:
            self.names_to_numbers[name] = len(self.names)
            self.names.append(name)
            return len(self.names) - 1

    def emit(self, bc, arg=0):
        self.data.append(chr(bc))
        self.data.append(chr(arg))

    def create_bytecode(self):
        return ByteCode(''.join(self.data), self.constants[:], len(self.names))


class ByteCode(object):
    def __init__(self, code, constants, numvars):
        self.code = code
        self.constants = constants
        self.numvars = numvars


def compile_ast(astnode):
    c = CompilerContext()
    astnode.compile(c)
    c.emit(RETURN, 0)
    return c.create_bytecode()

