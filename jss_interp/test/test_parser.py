# -*- encoding: utf-8 -*-

import pytest

from jss_interp import parser
from jss_interp.parser import Block, Stmt, Variable, ConstantNum, While, \
        Assignment, If, Call, BinOp, FnDef, Return


def test_parse_variable():
    for var_name in ('x', 'X', '_', 'foo', 'Fo', '_123'):
        result = parser.parse('%s;' % var_name) 
        assert result == Block([Stmt(Variable(var_name))])
    for invalid_var_name in ('0x', '123ss'):
        with pytest.raises(parser.ParseError):
            parser.parse('%s;' % invalid_var_name) 
    for invalid_var_name in ('%',):
        with pytest.raises(parser.LexerError):
            parser.parse('%s;' % invalid_var_name) 
    for not_var_name in ('123',):
        assert result != Block([Stmt(Variable(not_var_name))])


def test_parse_number():
    for num, value in [
            ('0', 0.0), ('1', 1.0), 
            ('.1', .1), ('+0.', 0.), ('-10.3', -10.3)]:
        result = parser.parse('%s;' % num) 
        assert result == Block([Stmt(ConstantNum(value))])


def test_paser_assignment():
    result = parser.parse('x_y = x;')
    assert result == \
            Block([Assignment('x_y', Variable('x'))])
    result = parser.parse('PI = 3.14;')
    assert result == \
            Block([Assignment('PI', ConstantNum(3.14))])
    with pytest.raises(parser.ParseError):
        parser.parse('1.0 = x;')


def test_parse_while():
    result = parser.parse('while (1) { a = 3; }')
    assert result == Block([While(ConstantNum(1.0), 
        Block([Assignment('a', ConstantNum(3))]))])
    result = parser.parse('while (1) { }')
    assert result == Block([While(ConstantNum(1.0), Block([]))])


def test_parse_if():
    result = parser.parse('if (y) { x = 10; }')
    assert result == Block([If(Variable('y'), 
        Block([Assignment('x', ConstantNum(10.0))]))])

    result = parser.parse('if (y) { x = 10; } else { x = 12; }')
    assert result == Block([If(Variable('y'), 
        Block([Assignment('x', ConstantNum(10.0))]),
        Block([Assignment('x', ConstantNum(12.0))]))])


def test_parse_fn_call():
    result = parser.parse('foo();')
    assert result == Block([Stmt(Call(Variable('foo'), []))])

    result = parser.parse('print(x);')
    assert result == Block([Stmt(Call(Variable('print'), [Variable('x')]))])

    result = parser.parse('foo(1);')
    assert result == Block([Stmt(Call(Variable('foo'), [ConstantNum(1.0)]))])

    result = parser.parse('foo(1 + 2);')
    assert result == Block([Stmt(Call(Variable('foo'), 
        [BinOp('+', ConstantNum(1.0), ConstantNum(2.0))]))])

    result = parser.parse('foo(x + y);')
    assert result == Block([Stmt(Call(Variable('foo'), 
        [BinOp('+', Variable('x'), Variable('y'))]))])

    result = parser.parse('foo(f(x) + y);')
    assert result == Block([Stmt(Call(Variable('foo'), 
        [BinOp('+', Call(Variable('f'), [Variable('x')]), Variable('y'))]))])
    result = parser.parse('foo(f(x), y);')
    assert result == Block([Stmt(Call(Variable('foo'), 
        [Call(Variable('f'), [Variable('x')]), Variable('y')]))])

    result = parser.parse('foo(1, f(x), y);')
    assert result == Block([Stmt(Call(Variable('foo'), [
        ConstantNum(1.0), 
        Call(Variable('f'), [Variable('x')]), 
        Variable('y')]))])

    result = parser.parse('foo(1, f(x), y, z, y);')
    assert result == Block([Stmt(Call(Variable('foo'), [
        ConstantNum(1.0), 
        Call(Variable('f'), [Variable('x')]), 
        Variable('y'),
        Variable('z'),
        Variable('y'),
        ]))])


def test_parse_binop():
    result = parser.parse('x = 1 + 2;')
    assert result == Block([Assignment('x', 
        BinOp('+', ConstantNum(1.0), ConstantNum(2.0)))])
    result = parser.parse('x = x - 2;')
    assert result == Block([Assignment('x', 
        BinOp('-', Variable('x'), ConstantNum(2.0)))])
    result = parser.parse('while (x == y) { }')
    assert result == Block([While(
        BinOp('==', Variable('x'), Variable('y')), Block([]))])


def test_parse_arithmetic():
    result = parser.parse('x * (y + z);')
    assert result == Block([Stmt(BinOp('*', Variable('x'),
        BinOp('+', Variable('y'), Variable('z'))))])

    result = parser.parse('z + x * y;')
    assert result == Block([Stmt(BinOp('+', Variable('z'),
        BinOp('*', Variable('x'), Variable('y'))))])

    result = parser.parse('z * x + y;')
    assert result == Block([Stmt(BinOp('+', 
        BinOp('*', Variable('z'), Variable('x')), Variable('y')))])

    result = parser.parse('x > z + x * y;')
    assert result == Block([Stmt(BinOp('>', Variable('x'), 
        BinOp('+', Variable('z'),
            BinOp('*', Variable('x'), Variable('y')))))])

    result = parser.parse('(x + y) / x + 3;')
    assert result == Block([Stmt(BinOp('+', 
        BinOp('/', BinOp('+', Variable('x'), Variable('y')), Variable('x')),
        ConstantNum(3.0)))])


def test_parse_fn_def():
    result = parser.parse('function foo() { };')
    assert result == Block([Stmt(FnDef('foo', [], Block([]), None, 0))])

    result = parser.parse('''

    function foo(x) { x + y; };
    ''', filename='foo.js')
    assert result == Block([Stmt(FnDef('foo', ['x'], 
        Block([Stmt(BinOp('+', Variable('x'), Variable('y')))]),
        'foo.js', 2))])

    result = parser.parse('function foo(x){};')
    assert result == Block([Stmt(FnDef('foo', ['x'], Block([]), None, 0))])

    result = parser.parse('function foo(){x;};')
    assert result == Block([Stmt(FnDef('foo', [], Block([
        Stmt(Variable('x'))]), None, 0))])

    result = parser.parse('function foo(x, y, z) { x + y; };')
    assert result == Block([Stmt(FnDef('foo', ['x', 'y', 'z'], 
        Block([Stmt(BinOp('+', Variable('x'), Variable('y')))]), None, 0))])


def test_parse_return():
    result = parser.parse('function foo(x, y, z) { return; };')
    assert result == Block([Stmt(FnDef('foo', ['x', 'y', 'z'], 
        Block([Return()]), None, 0))])

    result = parser.parse('function foo(x, y, z) { return x + y; };')
    assert result == Block([Stmt(FnDef('foo', ['x', 'y', 'z'], 
        Block([Return(BinOp('+', Variable('x'), Variable('y')))]), None, 0))])


