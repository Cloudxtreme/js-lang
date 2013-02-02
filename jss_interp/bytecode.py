# -*- encoding: utf-8 -*-


old_globals = dict(globals())

LOAD_CONSTANT_FLOAT, LOAD_CONSTANT_FN, LOAD_VAR, ASSIGN, \
DISCARD_TOP, RETURN, JUMP_IF_FALSE, JUMP_ABSOLUTE, \
BINARY_ADD, BINARY_SUB, BINARY_MUL, BINARY_DIV, BINARY_EQ, BINARY_LT, \
CALL, MAKE_FN \
= range(16)

bytecodes = dict((globals()[f], f) for f in globals() 
        if f not in old_globals and f != 'old_globals')


BINOP = {
        '+': BINARY_ADD, 
        '-': BINARY_SUB, 
        '*': BINARY_MUL, 
        '/': BINARY_DIV, 
        '==': BINARY_EQ, 
        '<': BINARY_LT,
        }


class CompilerContext(object):
    def __init__(self, names=None):
        self.data = []
        self.constants_float = []
        self.constants_fn = []
        self.names = []
        self.names_to_numbers = {}
        if names is not None:
            for name in names:
                self.register_var(name)

    def register_constant_float(self, v):
        self.constants_float.append(v)
        return len(self.constants_float) - 1

    def register_constant_fn(self, v):
        self.constants_fn.append(v)
        return len(self.constants_fn) - 1

    def register_var(self, name):
        try:
            return self.names_to_numbers[name]
        except KeyError:
            self.names_to_numbers[name] = len(self.names)
            self.names.append(name)
            return len(self.names) - 1

    def emit(self, bc, arg=0):
        self.data.append(bc)
        self.data.append(arg)

    def create_bytecode(self):
        return ByteCode(
                to_code(self.data), 
                self.names[:], 
                self.constants_float[:], self.constants_fn[:])

    @staticmethod
    def compile_ast(astnode, names=None):
        ''' Create bytecode object from an ast node
        :names: initial names for CompilerContext
        '''
        c = CompilerContext(names=names)
        astnode.compile(c)
        if len(c.data) < 2 or c.data[-2] != RETURN:
            c.emit(RETURN, 0)
        return c.create_bytecode()



class ByteCode(object):
    def __init__(self, code, names, constants_float, constants_fn):
        self.code = code
        self.names = names
        self.constants_float = constants_float
        self.constants_fn = constants_fn


def dis_to_list(code):
    ''' Disassemble code - for debugging
    '''
    dump = []
    for i in xrange(0, len(code), 2):
        c = ord(code[i])
        arg = ord(code[i+1])
        dump.append('%s %s' % (bytecodes[c], arg))
    return dump


def dis(code):
    ''' Disassemble code - for debugging
    '''
    return '\n'.join(dis_to_list(code))


def dis_to_line(code):
    return ' | '.join(dis_to_list(code))


def to_code(bytecode_list):
    return ''.join([chr(c) for c in bytecode_list])


