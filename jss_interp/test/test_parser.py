# -*- encoding: utf-8 -*-

from jss_interp import parser
from jss_interp.parser import Block, Stmt, Variable, ConstantNum


def test_parse_variable():
    for var_name in ('x', 'X', '_', 'foo', 'Fo', '_123'):
        result = parser.parse('%s;' % var_name) 
        assert result == Block([Stmt(Variable(var_name))])


def test_parse_number():
    x = 00
    for num, value in [
            ('0', 0.0), ('1', 1.0), 
            ('.1', .1), ('+0.', 0.), ('-10.3', -10.3)]:
        result = parser.parse('%s;' % num) 
        assert result == Block([Stmt(ConstantNum(value))])
