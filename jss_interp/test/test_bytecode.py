# -*- encoding: utf-8 -*-

from jss_interp.parser import ConstantNum
from jss_interp.bytecode import compile_ast, \
        LOAD_CONSTANT, DISCARD_TOP, RETURN


def test_const_num():
    bytecode = compile_ast(ConstantNum(10.0))
    assert bytecode.code == ''.join(map(chr, [LOAD_CONSTANT, 0, RETURN, 0]))
    assert bytecode.numvars == 0
    assert bytecode.constants == [10.0]
