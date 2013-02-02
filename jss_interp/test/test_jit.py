# -*- encoding: utf-8 -*-

from jss_interp.bytecode import to_code, LOAD_VAR, LOAD_CONSTANT_FLOAT, CALL
from jss_interp.interpreter import get_printable_location


def test_get_location():
    code = to_code([
        LOAD_VAR, 0,
        LOAD_VAR, 1,
        LOAD_CONSTANT_FLOAT, 0, 
        CALL, 2])
    assert get_printable_location(0, code, None) == \
            ' || LOAD_VAR 0 || LOAD_VAR 1 | LOAD_CONSTANT_FLOAT 0 | CALL 2'  
    assert get_printable_location(2, code, None) == \
            'LOAD_VAR 0 || LOAD_VAR 1 || LOAD_CONSTANT_FLOAT 0 | CALL 2'  
    assert get_printable_location(4, code, None) == \
            'LOAD_VAR 0 | LOAD_VAR 1 || LOAD_CONSTANT_FLOAT 0 || CALL 2'  
