# -*- encoding: utf-8 -*-

from rpython.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from rpython.rlib.parsing.deterministic import LexerError
from rpython.rlib.parsing.parsing import ParseError
from rpython.rlib.parsing.tree import Symbol

from jss_interp import bytecode


grammar = r'''

IGNORE: "[ \t\n]";

FLOAT_NUMBER: "0\.?[0-9]*|[1-9][0-9]*\.?[0-9]*|\.[0-9]+";

ADD_OPER: "[+-]";
MULT_OPER: "[*/%]";
COMP_OPER: "(==)|(>=)|(<=)|>|<|(!=)";

VARIABLE: "[a-zA-Z_][a-zA-Z0-9_]*";

main: statement* [EOF];

statement: 
      expr ";" 
    | VARIABLE "=" expr ";" 
    | "while" "(" expr ")" "{" statement* "}" 
    | "if" "(" expr ")" "{" statement* "}" "else" "{" statement* "}"
    | "if" "(" expr ")" "{" statement* "}"
    | "return" expr ";"
    | "return" ";";

expr: 
    ADD_OPER expr | unary;
unary: 
    additive COMP_OPER unary | additive;
additive: 
    multitive ADD_OPER additive | multitive;
multitive: 
    call MULT_OPER multitive | call;

call: 
    fndef "(" csexpr ")" | fndef "(" ")" | fndef;
csexpr: 
    expr "," csexpr | expr;

fndef: 
      "function" VARIABLE "(" csvar ")" "{" statement* "}" 
    | "function" VARIABLE "(" ")" "{" statement* "}" 
    | primary;
csvar: 
    VARIABLE "," csvar | VARIABLE;

primary: 
      "(" expr ")" 
    | atom;
atom:
      FLOAT_NUMBER 
    | VARIABLE;

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
        ctx.emit(bytecode.LOAD_CONSTANT_FLOAT, 
                 ctx.register_constant_float(self.floatval))


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


class UnOp(AstNode):
    ''' Binary operation
    '''
    _fields = ('op', 'expr')

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def compile(self, ctx):
        self.expr.compile(ctx)
        ctx.emit(bytecode.UNOP[self.op])


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


class Call(AstNode):
    ''' Function call with a list of arguments 
    '''
    _fields = ('fn', 'args',)

    def __init__(self, fn, args):
        self.fn = fn
        self.args = args

    def compile(self, ctx):
        self.fn.compile(ctx)
        for arg in self.args:
            arg.compile(ctx)
        ctx.emit(bytecode.CALL, len(self.args))


class If(AstNode):
    ''' If expression with optional else part
    '''
    _fields = ('cond', 'body', 'else_block')

    def __init__(self, cond, body, else_block=None):
        self.cond = cond
        self.body = body
        self.else_block = else_block

    def compile(self, ctx):
        self.cond.compile(ctx)
        ctx.emit(bytecode.JUMP_IF_FALSE, 0) # to be patched later (1)
        jump_pos = len(ctx.data) - 1
        self.body.compile(ctx)
        jump_abs_pos = 0
        if self.else_block:
            ctx.emit(bytecode.JUMP_ABSOLUTE, 0) # to be patched later (2)
            jump_abs_pos = len(ctx.data) - 1
        ctx.data[jump_pos] = len(ctx.data) # patch (1)
        if self.else_block:
            self.else_block.compile(ctx)
            ctx.data[jump_abs_pos] = len(ctx.data) # patch (2)


class While(AstNode):
    ''' While loop
    '''
    _fields = ('cond', 'body')

    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def compile(self, ctx):
        cond_pos = len(ctx.data)
        self.cond.compile(ctx)
        ctx.emit(bytecode.JUMP_IF_FALSE, 0) # to be patched later
        jump_pos = len(ctx.data) - 1
        self.body.compile(ctx)
        ctx.emit(bytecode.JUMP_ABSOLUTE, cond_pos)
        ctx.data[jump_pos] = len(ctx.data) # patch


class FnDef(AstNode):
    ''' Function definition
    '''
    _fields = ('name', 'arg_list', 'body', 'co_filename', 'co_firstlineno')

    def __init__(self, name, arg_list, body, 
            co_filename, co_firstlineno):
        self.name = name
        self.arg_list = arg_list
        self.body = body
        self.co_filename = co_filename
        self.co_firstlineno = co_firstlineno

    def compile(self, ctx):
        arg = ctx.register_constant_fn(ctx.compile_ast(
            self.body, names=self.arg_list,
            co_name=self.name,
            co_filename=self.co_filename,
            co_firstlineno=self.co_firstlineno))
        ctx.emit(bytecode.LOAD_CONSTANT_FN, arg)
        ctx.emit(bytecode.ASSIGN, ctx.register_var(self.name))
        ctx.emit(bytecode.LOAD_CONSTANT_FN, arg) # case it is an expression


class Return(AstNode):
    ''' Return statement
    '''
    _fields = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def compile(self, ctx):
        arg = 0
        if self.expr:
            arg = 1
            self.expr.compile(ctx)
        ctx.emit(bytecode.RETURN, arg)


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
        if len(node.children) == 2 and node.children[0].symbol == 'expr':
            return Stmt(self.visit_expr(node.children[0]))
        head_info = node.children[0].additional_info
        if head_info == 'while':
            cond = self.visit_expr(node.children[2])
            stmts = self._grab_stmts(node.children[5])
            return While(cond, Block(stmts))
        elif head_info == 'if':
            cond = self.visit_expr(node.children[2])
            stmts = self._grab_stmts(node.children[5])
            if isinstance(node.children[6], Symbol):
                assert node.children[6].additional_info == '}'
                else_block = None
            else:
                else_block = Block(self._grab_stmts(
                    node.children[6].children[3]))
            return If(cond, Block(stmts), else_block)
        elif head_info == 'return':
            if len(node.children) == 2:
                return Return()
            elif len(node.children) == 3:
                return Return(self.visit_expr(node.children[1]))
            else:
                raise NotImplementedError
        elif len(node.children) == 4:
            return Assignment(head_info, self.visit_expr(node.children[2]))
        raise NotImplementedError

    def visit_expr(self, node):
        if len(node.children) == 1:
            if node.symbol == 'atom':
                return self.visit_atom(node)
            else:
                return self.visit_expr(node.children[0])
        elif node.symbol == 'call':
            fn = self.visit_expr(node.children[0])
            if len(node.children) == 4:
                args = self.visit_csexpr(node.children[2])
            else:
                assert len(node.children) == 3
                args = []
            return Call(fn, args)
        elif node.symbol == 'fndef':
            co_firstlineno = node.getsourcepos().lineno
            fn_name = node.children[1].additional_info
            if len(node.children) == 6: # foo() {};
                return FnDef(fn_name, [], Block([]), 
                    self.filename, co_firstlineno)
            elif len(node.children) == 7: # foo(x) {}; or foo() {x;}
                if node.children[3].symbol == 'csvar':
                    return FnDef(fn_name, self.visit_csvar(node.children[3]),
                            Block([]), self.filename, co_firstlineno)
                else:
                    stmts = self._grab_stmts(node.children[5])
                    return FnDef(fn_name, [], Block(stmts),
                        self.filename, co_firstlineno)
            elif len(node.children) == 8: # foo(x) {x;}
                stmts = self._grab_stmts(node.children[6])
                return FnDef(fn_name, self.visit_csvar(node.children[3]),
                        Block(stmts), self.filename, co_firstlineno)
            else:
                raise NotImplementedError
        elif len(node.children) == 2: # unary op
            op = node.children[0].additional_info
            expr = self.visit_expr(node.children[1])
            if isinstance(expr, ConstantNum):
                return ConstantNum(-expr.floatval) if op == '-' else expr
            else:
                return UnOp(op, expr)
        elif len(node.children) == 3: # binary op or (expr)
            is_par_expr = True
            for c, br in [(node.children[0], '('), (node.children[2], ')')]:
                if not (isinstance(c, Symbol) and c.additional_info == br):
                    is_par_expr = False
                    break
            if is_par_expr:
                return self.visit_expr(node.children[1])
            else:
                return BinOp(node.children[1].additional_info,
                            self.visit_expr(node.children[0]),
                            self.visit_expr(node.children[2]))
        else:
            raise NotImplementedError

    def visit_csexpr(self, node):
        ''' Return a list of nodes (comma-separated "expr")
        '''
        assert len(node.children) in (1, 3)
        expr_list = [self.visit_expr(node.children[0])]
        if len(node.children) == 3:
            expr_list.extend(self.visit_csexpr(node.children[2]))
        return expr_list

    def visit_csvar(self, node):
        ''' Return a list of variable names (comma-separated VARIABLE)
        '''
        assert len(node.children) in (1, 3)
        assert node.children[0].symbol == 'VARIABLE'
        name_list = [node.children[0].additional_info]
        if len(node.children) == 3:
            name_list.extend(self.visit_csvar(node.children[2]))
        return name_list

    def visit_atom(self, node):
        chnode = node.children[0]
        if chnode.symbol == 'FLOAT_NUMBER':
            return ConstantNum(float(chnode.additional_info))
        if chnode.symbol == 'VARIABLE':
            return Variable(chnode.additional_info)
        raise NotImplementedError



def parse(source, filename=None):
    ''' Parse the source code and produce an AST
    '''
    transformer = Transformer()
    transformer.filename = filename
    try:
        return transformer.visit_main(_parse(source))
    except (LexerError, ParseError):
        raise

