from .semiring import Semiring
import sys

__author__ = 'francesco'


class TropicalSemiring(Semiring):
    def __init__(self, eps =  None):
        if eps is None:
            self.eps = sys.float_info.epsilon
        else:
            self.eps = max(eps, sys.float_info.epsilon)

    def value(self, a):
        return float(a)

    def parse(self, atom, weight):
        return atom, self.value(weight)

    def zero(self):
        return float('inf')

    def result(self, a):
        return a

    def times(self, a, b):
        return a + b

    def plus(self, a, b):
        return min(a, b)

    def approx_equal(self, a, b):
        return (a - b) < self.eps

    def one(self):
        return float(0.)

    def is_one(self, value):
        return abs(value - self.one()) < self.eps

    def is_zero(self, value):
        return value == float('inf')
