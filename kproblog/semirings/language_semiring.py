from .semiring import Semiring

__author__ = 'francesco'

class LangSemiring(Semiring):
    def approx_equal(self, a, b):
        return a == b

    def one(self):
        return {()}

    def is_one(self, value):
        return value == [()]

    def zero(self):
        return set()

    def is_zero(self, value):
        return value == []

    def plus(self, a, b):
        return a.union(b)

    def times(self, a, b):
        res = set()
        for ea in a:
            for eb in b:
                res.add(ea + eb)
        return res

    def value(self, a):
        return [(a,)]

    def result(self, a):
        return a

    def parse(self, atom, weight):
        return atom, self.value(weight)
