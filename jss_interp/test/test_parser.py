# -*- encoding: utf-8 -*-

import pytest

from jss_interp import parser
from jss_interp.parser import Block, Stmt, Variable, ConstantNum, While, \
        Assignment


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
