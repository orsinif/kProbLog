from .semiring import Semiring
import sys

__author__ = 'francesco'

class FloatSemiring(Semiring):
    def __init__(self, eps =  None):
        if eps is None:
            self.eps = sys.float_info.epsilon
        else:
            self.eps = max(eps, sys.float_info.epsilon)
        self.type_tag = 'f'

    def approx_equal(self, a, b):
        return abs(a-b) < self.eps

    def one(self):
        return float(1.)

    def is_one(self, value):
        return abs(value - 1.) < self.eps

    def zero(self):
        return float(0.)

    def is_zero(self, value):
        return abs(value) < self.eps

    def plus(self, a, b):
        return a + b

    def times(self, a, b):
        return a * b

    def value(self, a):
        return float(a)

    def parse(self, atom, weight):
        return atom, self.value(weight)

    def result(self, a):
        return a
