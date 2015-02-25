# -*- encoding: utf-8 -*-

from js.base_objects import W_BuilinFunction, W_StringObject


class W_PrintFn(W_BuilinFunction):

    def call(self, arg_list):
        print arg_list[0].to_string()


class W_TypeOf(W_BuilinFunction):

    def call(self, arg_list):
        return W_StringObject(type(arg_list[0]).__name__.replace("W_", ""))


BUILTINS = {
    'print': W_PrintFn(),
    'typeof': W_TypeOf(),
    #'assert': W_AssertFn,
}
