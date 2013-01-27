# -*- encoding: utf-8 -*-

from jss_interp.base_objects import W_BuilinFunction


class W_PrintFn(W_BuilinFunction):
    def call(self, arg_list):
        print arg_list[0].to_string()


BUILTINS = {
        'print': W_PrintFn(),
        #'assert': W_AssertFn,
        }
