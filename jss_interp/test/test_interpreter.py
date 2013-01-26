# -*- encoding: utf-8 -*-

from jss_interp.bytecode import to_code, ByteCode, \
        LOAD_CONSTANT, RETURN, LOAD_VAR, ASSIGN, DISCARD_TOP, BINARY_ADD, \
        BINARY_EQ, BINARY_LT, JUMP_IF_FALSE, JUMP_ABSOLUTE, CALL
from jss_interp.interpreter import Frame, interpret
from jss_interp.types import W_FloatObject, W_BoolObject


def test_frame():
    bc = ByteCode('', [], ['x', 'y'])
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
        [12.2], [])
    frame = interpret(bc)
    assert frame.valuestack == [W_FloatObject(12.2)]
    assert frame.vars == []


def test_assignment():
    bc = ByteCode(to_code([
        LOAD_CONSTANT, 0,
        ASSIGN, 0,
        RETURN, 0]), 
        [2.71], ['x'])
    frame = interpret(bc)
    assert frame.valuestack == []
    assert frame.vars == [W_FloatObject(2.71)]


def test_load_variable():
    bc = ByteCode(to_code([
        LOAD_CONSTANT, 0,
        ASSIGN, 0,
        LOAD_VAR, 0,
        RETURN, 0]), 
        [2.71], ['x'])
    frame = interpret(bc)
    assert frame.valuestack == [W_FloatObject(2.71)]
    assert frame.vars == [W_FloatObject(2.71)]


def test_dicard_top():
    bc = ByteCode(to_code([
        LOAD_CONSTANT, 0,
        DISCARD_TOP, 0,
        RETURN, 0]), 
        [2.71], [])
    frame = interpret(bc)
    assert frame.valuestack == []
    assert frame.vars == []


def test_jumps():
    bc = ByteCode(to_code([
        LOAD_CONSTANT, 0,
        JUMP_IF_FALSE, 8,
        LOAD_CONSTANT, 1,
        JUMP_ABSOLUTE, 10,
        LOAD_CONSTANT, 2,
        RETURN, 0]),
        [0.0, -1.0, 1.0], [])
    frame = interpret(bc)
    assert frame.valuestack == [W_FloatObject(1.0)]

    bc = ByteCode(to_code([
        LOAD_CONSTANT, 0,
        JUMP_IF_FALSE, 8,
        LOAD_CONSTANT, 1,
        JUMP_ABSOLUTE, 10,
        LOAD_CONSTANT, 2,
        RETURN, 0]),
        [1.0, -1.0, 2.0], [])
    frame = interpret(bc)
    assert frame.valuestack == [W_FloatObject(-1.0)]


def test_binary_add():
    bc = ByteCode(to_code([
        LOAD_CONSTANT, 0,
        LOAD_CONSTANT, 1,
        BINARY_ADD, 0,
        RETURN, 0]),
        [1.0, 2.5], [])
    frame = interpret(bc)
    assert frame.valuestack == [W_FloatObject(3.5)]


def test_binary_bool():
    for binary_op, check_fn in [
            (BINARY_LT, lambda x, y: x < y),
            (BINARY_EQ, lambda x, y: x == y),
            ]:
        for x, y in [(1.0, 2.5), (1.0, 1.0), (1.0, -1.0)]:
            bc = ByteCode(to_code([
                LOAD_CONSTANT, 0,
                LOAD_CONSTANT, 1,
                binary_op, 0,
                RETURN, 0]),
                [x, y], [])
            frame = interpret(bc)
            assert frame.valuestack == [W_BoolObject(check_fn(x, y))]


def test_print(capfd):
    bc = ByteCode(to_code([
        LOAD_VAR, 0,
        LOAD_CONSTANT, 0,
        CALL, 1,
        DISCARD_TOP, 0,
        RETURN, 0]), [3.78], ['print'])
    frame = interpret(bc)
    out, _ = capfd.readouterr()
    assert out == '3.78\n'
    assert frame.valuestack == []
    
