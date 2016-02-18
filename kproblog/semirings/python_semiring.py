from .semiring import Semiring

class PythonSemiring(Semiring):
    def one(self):
        return [()]

    def approx_equal(self, a, b):
        return a == b

    def zero(self):
        return []

    def is_zero(self, value):
        return not value

    def plus(self, a, b):
        return a + b

    def times(self, a, b):
        res = []
        for ea in a:
            for eb in b:
                res.append(ea + eb)
        return res

    def value(self, a):
        return [(a,)]

    def parse(self, atom, weight):
        return atom, self.value(weight)

    def result(self, a):
        return a
