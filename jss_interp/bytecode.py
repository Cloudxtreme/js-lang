# -*- encoding: utf-8 -*-


old_globals = dict(globals())

LOAD_CONSTANT, LOAD_VAR, ASSIGN, \
DISCARD_TOP, RETURN, JUMP_IF_FALSE, JUMP_ABSOLUTE, \
BINARY_ADD, BINARY_SUB, BINARY_EQ, BINARY_LT, \
PRINT \
= range(12)

bytecodes = dict((globals()[f], f) for f in globals() 
        if f not in old_globals and f != 'old_globals')


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


def dis(code):
    ''' Disassemble code - for debugging
    '''
    dump = []
    for i in xrange(0, len(code), 2):
        c, arg = map(ord, code[i:i+2])
        dump.append('%s %s' % (bytecodes[c], arg))
    return '\n'.join(dump)


def to_code(*bytecode_list):
    return ''.join(map(chr, bytecode_list))


def compile_ast(astnode):
    ''' Create bytecode object from an ast node
    '''
    c = CompilerContext()
    astnode.compile(c)
    c.emit(RETURN, 0)
    return c.create_bytecode()

