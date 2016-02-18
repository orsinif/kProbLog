from .semiring import Semiring

__author__ = 'francesco'


class IntSemiring(Semiring):
    def __init__(self):
        self.type_tag = 'i'

    def approx_equal(self, a, b):
        return a == b

    def one(self):
        return 1

    def is_one(self, value):
        return value == 1

    def zero(self):
        return 0

    def is_zero(self, value):
        return value == 0

    def plus(self, a, b):
        return a + b

    def times(self, a, b):
        return a * b

    def value(self, a):
        return int(a)

    def result(self, a):
        return a

    def parse(self, atom, weight):
        return atom, self.value(weight)
