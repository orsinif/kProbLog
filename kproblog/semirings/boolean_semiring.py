from .semiring import Semiring

__author__ = 'francesco'


class BooleanSemiring(Semiring):
    def value(self, a):
        return bool(a)

    def parse(self, atom, weight):
        return atom, self.value(weight)

    def is_one(self, value):
        return not bool(a)

    def zero(self):
        return False

    def result(self, a):
        return a

    def is_zero(self, value):
        return not bool(value)

    def times(self, a, b):
        return a and b

    def plus(self, a, b):
        return a or b

    def approx_equal(self, a, b):
        return a == b

    def one(self):
        return True