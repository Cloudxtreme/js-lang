# -*- encoding: utf-8 -*-


# this is very broken currently - lacks tests and
# does not really implement javascript


class OperationalError(Exception):
    pass


class W_Root(object):
    def is_true(self):
        raise NotImplementedError

    def lt(self, other):
        raise NotImplementedError

    def eq(self, other):
        raise NotImplementedError

    def add(self, other):
        raise NotImplementedError

    def to_string(self):
        raise NotImplementedError


class W_Numeric(W_Root):
    def add(self, other):
        return W_FloatObject(self.get_floatval() + other.get_floatval())

    def sub(self, other):
        return W_FloatObject(self.get_floatval() - other.get_floatval())

    def mul(self, other):
        return W_FloatObject(self.get_floatval() * other.get_floatval())

    def div(self, other):
        return W_FloatObject(self.get_floatval() / other.get_floatval())

    def mod(self, other):
        return W_FloatObject(float(
            int(self.get_floatval()) % int(other.get_floatval())))

    def lt(self, other):
        return W_BoolObject(self.get_floatval() < other.get_floatval())

    def eq(self, other):
        return W_BoolObject(self.get_floatval() == other.get_floatval())

    def get_floatval(self):
        raise NotImplementedError


class W_BoolObject(W_Numeric):
    #_immutable_fields_ = ['boolval']

    def __init__(self, boolval):
        self.boolval = bool(boolval)

    def is_true(self):
        return self.boolval

    def to_string(self):
        return 'true' if self.boolval else 'false'

    def get_floatval(self):
        return float(self.boolval)

    def __eq__(self, other):
        ''' NOT_RPYTHON '''
        return type(self) == type(other) and self.boolval == other.boolval


class W_FloatObject(W_Numeric):
    #_immutable_fields_ = ['floatval']

    def __init__(self, floatval):
        self.floatval = floatval

    def is_true(self):
        return bool(self.floatval)

    def to_string(self):
        return str(self.floatval)

    def get_floatval(self):
        return self.floatval

    def __eq__(self, other):
        ''' NOT_RPYTHON '''
        return type(self) == type(other) and self.floatval == other.floatval

    def __repr__(self):
        ''' NOT_RPYTHON '''
        return '<%s: %f>' % (type(self).__name__, self.floatval)



class W_BuilinFunction(W_Root):
    def call(self, arg_list):
        raise NotImplementedError


class W_Function(W_Root):
    def __init__(self, bytecode, parent_frame):
        self.bytecode = bytecode
        self.parent_frame = parent_frame

