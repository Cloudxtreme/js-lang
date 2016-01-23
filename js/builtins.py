# -*- encoding: utf-8 -*-


from js.base_objects import W_BuilinFunction, W_StringObject


class W_PrintFn(W_BuilinFunction):

    def call(self, arg_list):
        print arg_list[0].to_string()


class W_TypeOf(W_BuilinFunction):

    def call(self, arg_list):
        obj = arg_list[0]
        clsname = obj.__class__.__name__[2:]

        return W_StringObject(clsname)


BUILTINS = {
    'print': W_PrintFn(),
    'typeof': W_TypeOf(),
}
