# -*- encoding: utf-8 -*-

from jss_interp.parser import ConstantNum, Variable, Assignment, Stmt, Block, \
        BinOp, Call, If, While, FnDef
from jss_interp.bytecode import compile_ast, dis, to_code, \
        LOAD_CONSTANT, RETURN, LOAD_VAR, ASSIGN, DISCARD_TOP, \
        BINARY_ADD, BINARY_EQ, BINARY_LT, BINARY_MUL, BINARY_SUB, BINARY_DIV, \
        JUMP_IF_FALSE, JUMP_ABSOLUTE, CALL, MAKE_FN


def test_dis():
    code = to_code([LOAD_CONSTANT, 1, RETURN, 0])
    assert dis(code) == 'LOAD_CONSTANT 1\nRETURN 0'


def test_const_num():
    bytecode = compile_ast(ConstantNum(10.0))
    assert bytecode.code == to_code([LOAD_CONSTANT, 0, RETURN, 0])
    assert bytecode.names == []
    assert bytecode.constants == [10.0]


def test_variable():
    bytecode = compile_ast(Variable('x'))
    assert bytecode.code == to_code([LOAD_VAR, 0, RETURN, 0])
    assert bytecode.names == ['x']
    assert bytecode.constants == []

    bytecode = compile_ast(Block([
        Variable('zzz'), Variable('y'), Variable('zzz')]))
    assert bytecode.code == to_code([
        LOAD_VAR, 0, LOAD_VAR, 1, LOAD_VAR, 0, RETURN, 0])
    assert bytecode.names == ['zzz', 'y']
    assert bytecode.constants == []


def test_stmt():
    bytecode = compile_ast(Stmt(Variable('x')))
    assert bytecode.code == to_code([LOAD_VAR, 0, DISCARD_TOP, 0, RETURN, 0])
    assert bytecode.names == ['x']
    assert bytecode.constants == []


def test_block():
    bytecode = compile_ast(Block([
        Stmt(Variable('xyz')), Stmt(ConstantNum(12.3))]))
    assert bytecode.code == to_code([
            LOAD_VAR, 0, DISCARD_TOP, 0, 
            LOAD_CONSTANT, 0, DISCARD_TOP, 0,
            RETURN, 0])
    assert bytecode.names == ['xyz']
    assert bytecode.constants == [12.3]


def test_binop():
    for op, bc in [
            ('+', BINARY_ADD), 
            ('==', BINARY_EQ),
            ('<', BINARY_LT),
            ('-', BINARY_SUB),
            ('*', BINARY_MUL),
            ('/', BINARY_DIV),
            ]:
        bytecode = compile_ast(BinOp(op, Variable('x'), Variable('y')))
        assert bytecode.code == to_code([
                LOAD_VAR, 0,
                LOAD_VAR, 1, 
                bc, 0,
                RETURN, 0])
        assert bytecode.names == ['x', 'y']
        assert bytecode.constants == []

        bytecode = compile_ast(BinOp(op, ConstantNum(2.0), Variable('y')))
        assert bytecode.code == to_code([
                LOAD_CONSTANT, 0,
                LOAD_VAR, 0, 
                bc, 0,
                RETURN, 0])
        assert bytecode.names == ['y']
        assert bytecode.constants == [2.0]


def test_assignment():
    bytecode = compile_ast(Assignment('x', Variable('y')))
    assert bytecode.code == to_code([LOAD_VAR, 0, ASSIGN, 1, RETURN, 0])
    assert bytecode.names == ['y', 'x']
    assert bytecode.constants == []

    bytecode = compile_ast(Assignment('x', ConstantNum(13.4)))
    assert bytecode.code == to_code([LOAD_CONSTANT, 0, ASSIGN, 0, RETURN, 0])
    assert bytecode.names == ['x']
    assert bytecode.constants == [13.4]


def test_call():
    bytecode = compile_ast(Call(Variable('fn'), []))
    assert bytecode.code == to_code([
        LOAD_VAR, 0,
        CALL, 0,
        RETURN, 0])
    assert bytecode.names == ['fn']
    assert bytecode.constants == []

    bytecode = compile_ast(Call(Variable('fn'), [ConstantNum(1.0)]))
    assert bytecode.code == to_code([
        LOAD_VAR, 0,
        LOAD_CONSTANT, 0, 
        CALL, 1,
        RETURN, 0])
    assert bytecode.names == ['fn']
    assert bytecode.constants == [1.0]

    bytecode = compile_ast(Call(Variable('fn'), [
        Variable('z'), ConstantNum(1.0)]))
    assert bytecode.code == to_code([
        LOAD_VAR, 0,
        LOAD_VAR, 1,
        LOAD_CONSTANT, 0, 
        CALL, 2,
        RETURN, 0])
    assert bytecode.names == ['fn', 'z']
    assert bytecode.constants == [1.0]

    bytecode = compile_ast(Call(Variable('fn'), [
        Call(Variable('z'), []), ConstantNum(1.0)]))
    assert bytecode.code == to_code([
        LOAD_VAR, 0,
        LOAD_VAR, 1,
        CALL, 0,
        LOAD_CONSTANT, 0, 
        CALL, 2,
        RETURN, 0])
    assert bytecode.names == ['fn', 'z']
    assert bytecode.constants == [1.0]

def test_if():
    bytecode = compile_ast(If(ConstantNum(1.0), ConstantNum(2.0)))
    expected_code = to_code([
            LOAD_CONSTANT, 0,
            JUMP_IF_FALSE, 6,
            LOAD_CONSTANT, 1,
            RETURN, 0])
    assert bytecode.code == expected_code
    assert bytecode.names == []
    assert bytecode.constants == [1.0, 2.0]


def test_while():
    bytecode = compile_ast(Block([
        Variable('x'),
        While(ConstantNum(1.0), ConstantNum(1.0))]))
    expected_code = to_code([
            LOAD_VAR, 0,
            LOAD_CONSTANT, 0,
            JUMP_IF_FALSE, 10,
            LOAD_CONSTANT, 1,
            JUMP_ABSOLUTE, 2,
            RETURN, 0])
    assert bytecode.code == expected_code
    assert bytecode.names == ['x']
    assert bytecode.constants == [1.0, 1.0]
    

def test_fn_def():
    bytecode = compile_ast(FnDef('foo', [], Block([])))
    expected_code = to_code([
        LOAD_CONSTANT, 0,
        MAKE_FN, 0,
        ASSIGN, 0,
        RETURN, 0])
    expected_inner_bytecode = to_code([RETURN, 0])

    assert bytecode.code == expected_code
    assert bytecode.names == ['foo']
    assert len(bytecode.constants) == 1
    inner = bytecode.constants[0]
    assert inner.code == expected_inner_bytecode
    assert inner.names == []
    assert inner.constants == []
