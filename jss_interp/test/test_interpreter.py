# -*- encoding: utf-8 -*-

from jss_interp.bytecode import compile_ast, dis, to_code, ByteCode, \
        LOAD_CONSTANT, RETURN, LOAD_VAR, ASSIGN, DISCARD_TOP, BINARY_ADD, \
        BINARY_EQ, PRINT, JUMP_IF_FALSE, JUMP_ABSOLUTE
from jss_interp.interpreter import Frame, interpret, W_FloatObject


def test_frame():
    bc = ByteCode('', [], 2)
    frame = Frame(bc)
    assert len(frame.vars) == 2
    assert len(frame.valuestack) == 0
    x, y = object(), object()
    frame.push(x)
    assert len(frame.valuestack) == 1
    res = frame.pop()
    assert res is x
    assert len(frame.valuestack) == 0
    frame.push(x)
    frame.push(y)
    assert len(frame.valuestack) == 2
    res = frame.pop()
    assert res is y
    assert len(frame.valuestack) == 1


def test_load_constant():
    bc = ByteCode(to_code([
        LOAD_CONSTANT, 0,
        RETURN, 0]), 
        [12.2], 0)
    frame = interpret(bc)
    assert frame.valuestack == [W_FloatObject(12.2)]
    assert frame.vars == []


def test_load_variable():
    bc = ByteCode(to_code([
        LOAD_VAR, 0,
        RETURN, 0]), 
        [], 1)
    frame = interpret(bc)
    assert frame.valuestack == [None]
    assert frame.vars == [None]


def test_assignment():
    bc = ByteCode(to_code([
        LOAD_CONSTANT, 0,
        ASSIGN, 0,
        RETURN, 0]), 
        [2.71], 1)
    frame = interpret(bc)
    assert frame.valuestack == []
    assert frame.vars == [W_FloatObject(2.71)]


def test_dicard_top():
    bc = ByteCode(to_code([
        LOAD_CONSTANT, 0,
        DISCARD_TOP, 0,
        RETURN, 0]), 
        [2.71], 0)
    frame = interpret(bc)
    assert frame.valuestack == []
    assert frame.vars == []
