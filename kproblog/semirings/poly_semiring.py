from problog.logic import Constant, Term
from .polynomial_obj import BasePolynomial, Indeterminate, polynomial
from .semiring import Semiring

__author__ = 'francesco'

class PolynomialSemiring(Semiring):
    def __init__(self, semiring):
        self.semiring = semiring
        self.ZERO = polynomial(self.semiring, semiring.zero())
        self.ONE = polynomial(self.semiring, semiring.one())
        self.parse_polynomial = get_semiring_parser(semiring)

    def __call__(self):
        return self.zero()

    def is_zero(self, val):
        return polynomial(self.semiring, val).is_zero()

    def zero(self):
        return self.ZERO

    def one(self):
        return self.ONE

    def value(self, a):
        if isinstance(a, BasePolynomial):
            return a
        elif isinstance(a, Term):
            return self.parse_polynomial(a)
        else:
            print "VALUE", type(a)
            raise NotImplementedError

    def parse(self, atom, weight):
        return atom, self.value(weight)

    def approx_equal(self, a, b):
        return self.is_zero(self.plus(a, b.negate()))

    # def is_one(self, value):
    #     return value == self.one()

    def plus(self, a, b):
        return a + b

    def times(self, a, b):
        return a * b

    def result(self, a):
        return a


def get_semiring_parser(semiring):
    def parse_polynomial(a):
        if isinstance(a, Constant):
            if a.is_float():
                return polynomial(semiring, float(a))
            elif a.is_integer():
                return polynomial(semiring, int(a))
            else:
                return Indeterminate(semiring, a.compute_value())
        else:
            assert isinstance(a, Term)
            if a.functor == "'*'":
                return reduce(lambda x, y:x*y, map(parse_polynomial, a.args))
            elif a.functor == "'+'":
                return reduce(lambda x, y:x+y, map(parse_polynomial, a.args))
            elif a.functor == "'^'":
                assert a.arity == 2
                base = parse_polynomial(a.args[0])
                exponent = parse_polynomial(a.args[1])
                return base ** exponent
            else:
                return Indeterminate(semiring, a)
                # raise NotImplementedError, "{}/{}".format(a.functor, a.arity)
    return parse_polynomial