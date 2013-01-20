# -*- encoding: utf-8 -*-


# this is very broken currently - lacks tests and
# does not really implement javascript


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


class W_BoolObject(W_Root):
    def __init__(self, boolval):
        self.boolval = bool(boolval)

    def is_true(self):
        return self.boolval

    def eq(self, other):
        if isinstance(other, W_BoolObject):
            return W_BoolObject(self.boolval == other.boolval)
        elif isinstance(other, W_FloatObject):
            return W_BoolObject(float(self.boolval) == other.floatval)
        else:
            return W_BoolObject(False)

    def lt(self, other):
        if isinstance(other, W_BoolObject):
            return W_BoolObject(self.boolval < other.boolval)
        elif isinstance(other, W_FloatObject):
            return W_BoolObject(float(self.boolval) < other.floatval)
        else:
            raise OperationalError('not supported yet')

    def add(self, other):
        if isinstance(other, W_BoolObject):
            other_floatval = float(other.boolval)
        elif isinstance(other, W_FloatObject):
            other_floatval = other.floatval
        else:
            raise OperationalError('not supported yet')
        return W_FloatObject(float(self.boolval) + other_floatval)

    def to_string(self):
        return 'true' if self.boolval else 'false'

    def __eq__(self, other):
        ''' NOT_RPYTHON '''
        return type(self) == type(other) and self.boolval == other.boolval


class W_FloatObject(W_Root):
    def __init__(self, floatval):
        self.floatval = floatval

    def _assert_float(self, other):
        if not isinstance(other, W_FloatObject):
            raise OperationalError('Expected a number')

    def is_true(self):
        return bool(self.floatval)

    def lt(self, other):
        self._assert_float(other)
        return W_BoolObject(self.floatval < other.floatval)

    def eq(self, other):
        self._assert_float(other)
        return W_BoolObject(self.floatval == other.floatval)

    def add(self, other):
        self._assert_float(other)
        return W_FloatObject(self.floatval + other.floatval)

    def to_string(self):
        return str(self.floatval)

    def __eq__(self, other):
        ''' NOT_RPYTHON '''
        return type(self) == type(other) and self.floatval == other.floatval


class OperationalError(Exception):
    pass


