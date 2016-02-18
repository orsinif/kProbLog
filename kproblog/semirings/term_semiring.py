from .semiring import Semiring
from problog.logic import *

__author__ = 'francesco'

class TermSemiring(Semiring):
    def value(self, a):
        return Term(a)

    def parse(self, atom, weight):
        return atom, self.value(weight)

    def zero(self):
        return Term('semiring_zero')

    def result(self, a):
        return a

    def times(self, a, b):
        if self.is_one(a):
            return b
        elif self.is_one(b):
            return a
        else:
            return Term('*', a, b)

    def plus(self, a, b):
        if self.is_zero(a):
            return self.zero()
        elif self.is_zero(b):
            return self.zero()
        else:
            return Term('+', a, b)

    def approx_equal(self, a, b):
        return a == b

    def one(self):
        return Term('semiring_one')

    def is_one(self, value):
        return value == self.one()

    def is_zero(self, value):
        return value == self.zero()
