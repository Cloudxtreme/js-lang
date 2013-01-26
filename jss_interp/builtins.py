# -*- encoding: utf-8 -*-

from jss_interp.base_objects import W_Root


class W_BuilinFn(W_Root):
    def call(self, arg_list):
        raise NotImplementedError


class W_PrintFn(W_BuilinFn):
    def call(self, arg_list):
        print arg_list[0].to_string()


BUILTINS = {
        'print': W_PrintFn(),
        #'assert': W_AssertFn,
        }
