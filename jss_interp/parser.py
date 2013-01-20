# -*- encoding: utf-8 -*-

from pypy.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from pypy.rlib.parsing.deterministic import LexerError
from pypy.rlib.parsing.parsing import ParseError
from pypy.rlib.parsing.tree import Symbol

from jss_interp import bytecode


grammar = r'''

IGNORE: "[ \t\n]";
FLOAT_NUMBER: "[-+]?0\.?[0-9]*|[-+]?[1-9][0-9]*\.?[0-9]*|[-+]?\.[0-9]+";
ADD_SYMBOL: "(==)|[-+<]";
VARIABLE: "[a-zA-Z_][a-zA-Z0-9_]*";

main: statement* [EOF];

statement: expr ";" 
    | VARIABLE "=" expr ";" 
    | "while" "(" expr ")" "{" statement* "}" 
    | "if" "(" expr ")" "{" statement* "}" 
    | "print" "(" expr ")" ";";

expr: atom ADD_SYMBOL expr | atom;

atom: FLOAT_NUMBER | VARIABLE;
'''

regexs, rules, ToAST = parse_ebnf(grammar)
_parse = make_parse_function(regexs, rules, eof=True)


class AstNode(object):
    ''' Abstract syntax tree node
    '''
    _fields = ()

    def __eq__(self, other):
        return type(self) == type(other) and \
                self.__dict__ == other.__dict__

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__,
                '; '.join('%s: %r' % (field, getattr(self, field))
                    for field in self._fields) 
                if len(self._fields) > 1 else 
                repr(getattr(self, self._fields[0])))


class Block(AstNode):
    ''' List of statements
    '''
    _fields = ('stmts',)

    def __init__(self, stmts):
        self.stmts = stmts

    def compile(self, ctx):
        for stmt in self.stmts:
            stmt.compile(ctx)


class Stmt(AstNode):
    ''' Single statement
    '''
    _fields = ('expr',)

    def __init__(self, expr):
        self.expr = expr

    def compile(self, ctx):
        self.expr.compile(ctx)
        ctx.emit(bytecode.DISCARD_TOP)


class ConstantNum(AstNode):
    ''' Numeric constant
    '''
    _fields = ('floatval',)
    
    def __init__(self, floatval):
        self.floatval = floatval

    def compile(self, ctx):
        ctx.emit(bytecode.LOAD_CONSTANT, ctx.register_constant(self.floatval))


class BinOp(AstNode):
    ''' Binary operation
    '''
    _fields = ('op', 'left', 'right')

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def compile(self, ctx):
        self.left.compile(ctx)
        self.right.compile(ctx)
        ctx.emit(bytecode.BINOP[self.op])


class Variable(AstNode):
    ''' Variable reference
    '''
    _fields = ('varname',)

    def __init__(self, varname):
        self.varname = varname

    def compile(self, ctx):
        ctx.emit(bytecode.LOAD_VAR, ctx.register_var(self.varname))


class Assignment(AstNode):
    ''' Assign to a variable
    '''
    _fields = ('varname', 'expr')

    def __init__(self, varname, expr):
        self.varname = varname
        self.expr = expr

    def compile(self, ctx):
        self.expr.compile(ctx)
        ctx.emit(bytecode.ASSIGN, ctx.register_var(self.varname))


class Print(AstNode):
    ''' Print something TODO - remove after functions are ready?
    '''
    _fields = ('expr',)

    def __init__(self, expr):
        self.expr = expr

    def compile(self, ctx):
        self.expr.compile(ctx)
        ctx.emit(bytecode.PRINT)


class If(AstNode):
    ''' If expression without the else part
    '''
    _fields = ('cond', 'body')

    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def compile(self, ctx):
        raise NotImplementedError


class While(AstNode):
    ''' While loop
    '''
    _fields = ('cond', 'body')

    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def compile(self, ctx):
        raise NotImplementedError


class Transformer(object):
    ''' Transforms AST from the obscure format given to us by the ebnfparser
    to something easier to work with
    '''
    def _grab_stmts(self, star):
        stmts = []
        if isinstance(star, Symbol) and star.additional_info == '}':
            return stmts
        while len(star.children) == 2:
            stmts.append(self.visit_stmt(star.children[0]))
            star = star.children[1]
        stmts.append(self.visit_stmt(star.children[0]))
        return stmts
    
    def visit_main(self, node):
        stmts = self._grab_stmts(node.children[0])
        return Block(stmts)

    def visit_stmt(self, node):
        if len(node.children) == 2:
            return Stmt(self.visit_expr(node.children[0]))
        if len(node.children) == 4:
            return Assignment(node.children[0].additional_info,
                              self.visit_expr(node.children[2]))
        if node.children[0].additional_info == 'while':
            cond = self.visit_expr(node.children[2])
            stmts = self._grab_stmts(node.children[5])
            return While(cond, Block(stmts))
        if node.children[0].additional_info == 'if':
            cond = self.visit_expr(node.children[2])
            stmts = self._grab_stmts(node.children[5])
            return If(cond, Block(stmts))
        if node.children[0].additional_info == 'print':
            return Print(self.visit_expr(node.children[2]))
        raise NotImplementedError

    def visit_expr(self, node):
        if len(node.children) == 1:
            return self.visit_atom(node.children[0])
        return BinOp(node.children[1].additional_info,
                     self.visit_atom(node.children[0]),
                     self.visit_expr(node.children[2]))

    def visit_atom(self, node):
        chnode = node.children[0]
        if chnode.symbol == 'FLOAT_NUMBER':
            return ConstantNum(float(chnode.additional_info))
        if chnode.symbol == 'VARIABLE':
            return Variable(chnode.additional_info)
        raise NotImplementedError


transformer = Transformer()


def parse(source):
    ''' Parse the source code and produce an AST
    '''
    try:
        return transformer.visit_main(_parse(source))
    except (LexerError, ParseError):
        raise

