# -*- encoding: utf-8 -*-

from jss_interp.bytecode import to_code, ByteCode, \
        LOAD_CONSTANT, RETURN, LOAD_VAR, ASSIGN, DISCARD_TOP, BINARY_ADD, \
        BINARY_EQ, BINARY_LT, JUMP_IF_FALSE, JUMP_ABSOLUTE, CALL
from jss_interp.interpreter import Frame, interpret, interpret_source
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
    frame = interpret_source('x = 2.71;')
    assert frame.valuestack == []
    assert frame.vars == [W_FloatObject(2.71)]


def test_load_variable():
    frame = interpret_source('''
    x = 2.71;
    y = x;
    ''')
    assert frame.valuestack == []
    assert frame.names == ['x', 'y']
    assert frame.vars == [W_FloatObject(2.71), W_FloatObject(2.71)]


def test_dicard_top():
    frame = interpret_source('2.71;')
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


def test_if():
    frame = interpret_source('''
    if (0) {
        x = 10;
    }''')
    assert frame.names == ['x']
    assert frame.vars == [None]
    assert frame.valuestack == []

    frame = interpret_source('''
    if (1) {
        x = 10;
    }''')
    assert frame.names == ['x']
    assert frame.vars == [W_FloatObject(10.0)]
    assert frame.valuestack == []


def test_while():
    frame = interpret_source('''
    while (0) {
        x = 10;
    }''')
    assert frame.names == ['x']
    assert frame.vars == [None]
    assert frame.valuestack == []

    frame = interpret_source('''
    x = 1;
    y = 10;
    while (x) {
        x = 0;
        y = 100;
    }''')
    assert frame.names == ['x', 'y']
    assert frame.vars == [W_FloatObject(0.0), W_FloatObject(100.0)]
    assert frame.valuestack == []


def test_binary_add():
    frame = interpret_source('''
    x = 1 + 2.5;
    ''')
    assert frame.names == ['x']
    assert frame.vars == [W_FloatObject(3.5)]
    assert frame.valuestack == []


def test_binary_bool():
    for binary_op, check_fn in [
            ('<', lambda x, y: x < y),
            ('==', lambda x, y: x == y),
            ]:
        for x, y in [(1.0, 2.5), (1.0, 1.0), (1.0, -1.0)]:
            frame = interpret_source('''
            x = %s;
            y = %s;
            res = x %s y;
            ''' % (x, y, binary_op))
            assert frame.names == ['x', 'y', 'res']
            assert frame.vars == [
                    W_FloatObject(x), W_FloatObject(y),
                    W_BoolObject(check_fn(x, y))]
            assert frame.valuestack == []


def test_print(capfd):
    frame = interpret_source('print(3.78);')
    out, _ = capfd.readouterr()
    assert out == '3.78\n'
    assert frame.valuestack == []
    
