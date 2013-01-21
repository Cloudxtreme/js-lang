# -*- encoding: utf-8 -*-

from jss_interp.types import W_Root


class W_BuilinFn(W_Root):
    def call(self, arg):
        raise NotImplementedError


class W_PrintFn(W_BuilinFn):
    def call(self, arg):
        print arg 


BUILTINS = {
        'print': W_PrintFn,
        #'assert': W_AssertFn,
        }
