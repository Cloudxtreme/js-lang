# -*- encoding: utf-8 -*-

from jss_interp.parser import ConstantNum, Variable, Assignment, Stmt, Block, \
        BinOp, Print, If, While
from jss_interp.bytecode import compile_ast, dis, \
        LOAD_CONSTANT, RETURN, LOAD_VAR, ASSIGN, DISCARD_TOP, BINARY_ADD, \
        BINARY_EQ, PRINT, JUMP_IF_FALSE, JUMP_ABSOLUTE


def to_code(*bytecode_list):
    return ''.join(map(chr, bytecode_list))


def test_dis():
    code = to_code(LOAD_CONSTANT, 1, RETURN, 0)
    assert dis(code) == 'LOAD_CONSTANT 1\nRETURN 0'


def test_const_num():
    bytecode = compile_ast(ConstantNum(10.0))
    assert bytecode.code == to_code(LOAD_CONSTANT, 0, RETURN, 0)
    assert bytecode.numvars == 0
    assert bytecode.constants == [10.0]


def test_variable():
    bytecode = compile_ast(Variable('x'))
    assert bytecode.code == to_code(LOAD_VAR, 0, RETURN, 0)
    assert bytecode.numvars == 1
    assert bytecode.constants == []


def test_stmt():
    bytecode = compile_ast(Stmt(Variable('x')))
    assert bytecode.code == to_code(LOAD_VAR, 0, DISCARD_TOP, 0, RETURN, 0)
    assert bytecode.numvars == 1
    assert bytecode.constants == []


def test_block():
    bytecode = compile_ast(Block([
        Stmt(Variable('x')), Stmt(ConstantNum(12.3))]))
    assert bytecode.code == to_code(
            LOAD_VAR, 0, DISCARD_TOP, 0, 
            LOAD_CONSTANT, 0, DISCARD_TOP, 0,
            RETURN, 0)
    assert bytecode.numvars == 1
    assert bytecode.constants == [12.3]


def test_binop():
    bytecode = compile_ast(BinOp('+', Variable('x'), Variable('y')))
    assert bytecode.code == to_code(
            LOAD_VAR, 0,
            LOAD_VAR, 1, 
            BINARY_ADD, 0,
            RETURN, 0)
    assert bytecode.numvars == 2
    assert bytecode.constants == []

    bytecode = compile_ast(BinOp('==', ConstantNum(2.0), Variable('y')))
    assert bytecode.code == to_code(
            LOAD_CONSTANT, 0,
            LOAD_VAR, 0, 
            BINARY_EQ, 0,
            RETURN, 0)
    assert bytecode.numvars == 1
    assert bytecode.constants == [2.0]


def test_assignment():
    bytecode = compile_ast(Assignment('x', Variable('y')))
    assert bytecode.code == to_code(LOAD_VAR, 0, ASSIGN, 1, RETURN, 0)
    assert bytecode.numvars == 2
    assert bytecode.constants == []

    bytecode = compile_ast(Assignment('x', ConstantNum(13.4)))
    assert bytecode.code == to_code(LOAD_CONSTANT, 0, ASSIGN, 0, RETURN, 0)
    assert bytecode.numvars == 1
    assert bytecode.constants == [13.4]


def test_print():
    bytecode = compile_ast(Print(ConstantNum(1.0)))
    assert bytecode.code == to_code(LOAD_CONSTANT, 0, PRINT, 0, RETURN, 0)
    assert bytecode.numvars == 0
    assert bytecode.constants == [1.0]


def test_if():
    bytecode = compile_ast(If(ConstantNum(1.0), Print(ConstantNum(1.0))))
    expected_code = to_code(
            LOAD_CONSTANT, 0,
            JUMP_IF_FALSE, 8,
            LOAD_CONSTANT, 1,
            PRINT, 0,
            RETURN, 0)
    assert bytecode.code == expected_code
    assert bytecode.numvars == 0
    assert bytecode.constants == [1.0, 1.0]


def test_while():
    bytecode = compile_ast(Block([
        Print(Variable('x')),
        While(ConstantNum(1.0), Print(ConstantNum(1.0)))]))
    expected_code = to_code(
            LOAD_VAR, 0,
            PRINT, 0,
            LOAD_CONSTANT, 0,
            JUMP_IF_FALSE, 14,
            LOAD_CONSTANT, 1,
            PRINT, 0,
            JUMP_ABSOLUTE, 4,
            RETURN, 0)
    assert bytecode.code == expected_code
    assert bytecode.numvars == 1
    assert bytecode.constants == [1.0, 1.0]
