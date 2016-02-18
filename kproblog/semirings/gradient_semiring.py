from .semiring import Semiring
from problog.logic import Term

class GradientSemiring(Semiring):
    def approx_equal(self, a, b):
        return a == b

    def one(self):
        return GradientObj(1, {})

    def is_one(self, value):
        return (value.x == 1.) and bool(value.partial)

    def zero(self):
        return GradientObj(0., {})

    def is_zero(self, value):
        return (value.x == 0.) and bool(value.partial)

    def plus(self, a, b):
        return a + b

    def times(self, a, b):
        return a * b

    def value(self, a):
        if isinstance(a, GradientObj):
            return a
        elif isinstance(a, Term):
            assert a.functor == 'eps' and a.arity == 1
            return GradientObj(0, {a: 1.})
        else:
            print 'type(a)', type(a)
            return GradientObj(float(a), {})
        return a

    def result(self, a):
        return a

    def parse(self, atom, weight):
        return atom, self.value(weight)

from collections import defaultdict

def sv_add(a, b):
    res = defaultdict(float)
    for ka, va in a.iteritems():
        res[ka] = va
    for kb, vb in b.iteritems():
        res[kb] += vb
    return dict(res)

def sv_scalar_mul(scalar, sv):
    return {k:scalar*v for k, v in sv.iteritems()}

def const_gradient_object(value):
    return GradientObj(value, {})

class GradientObj(object):
    def __init__(self, x, partials):
        self.x = x
        self.partials = partials

    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            other = const_gradient_object(other)
        x = self.x + other.x
        partials = sv_add(self.partials, other.partials)
        return GradientObj(x, partials)

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            other = const_gradient_object(other)
        x = self.x * other.x
        partials = sv_add(
            sv_scalar_mul(self.x, other.partials),
            sv_scalar_mul(other.x, self.partials)
        )
        return GradientObj(x, partials)

    def __rmul__(self, other):
        return self.__mul__(other)

    def grad(self, key):
        return self.partials[key]

    def __str__(self):
        eps_str = " + ".join(["{} {}".format(val, key)
            for key, val in self.partials.iteritems()])
        return "{} + {}".format(self.x, eps_str)
