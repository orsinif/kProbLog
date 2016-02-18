__author__ = 'francesco'

from .frozendict import FrozenDict

from functools import total_ordering
from collections import defaultdict
import numpy as np



class BasePolynomial(object):
    def __init__(self, semiring):
        self.semiring = semiring

    def __add__(self, other):
        a = polynomial(self.semiring, self)
        b = polynomial(self.semiring, other)
        return a.add(b)

    def __radd__(self, other):
        a = polynomial(self.semiring, self)
        b = polynomial(self.semiring, other)
        return b.add(a)

    def __mul__(self, other):
        a = polynomial(self.semiring, self)
        b = polynomial(self.semiring, other)
        return a.mul(b)

    def __rmul__(self, other):
        a = polynomial(self.semiring, self)
        b = polynomial(self.semiring, other)
        return b.mul(a)

    def __pow__(self, exp):
        assert isinstance(exp, int)
        a = polynomial(self.semiring, self)
        res = polynomial(self.semiring, self.semiring.one())
        for _ in xrange(exp):
            res = res * a
        return res

def polynomial(semiring, t):
    if isinstance(t, Indeterminate):
        m = Monomial(semiring, {t:1})
        return Polynomial(semiring, {m:semiring.one()})
    elif isinstance(t, Monomial):
        return Polynomial(semiring, {t:semiring.one()})
    elif isinstance(t, Polynomial):
        return t
    else:
        m = Monomial(semiring, {})
        return Polynomial(semiring, {m:t})


@total_ordering
class Indeterminate(BasePolynomial):
    def __init__(self, semiring, name):
        BasePolynomial.__init__(self, semiring)
        self.name = str(name)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __le__(self, other):
        return self.name.__le__(other.name)

    def __str__(self):
        return self.name

@total_ordering
class Monomial(BasePolynomial):
    def __init__(self, semiring, var2exp):
        BasePolynomial.__init__(self, semiring)
        self.var2exp = FrozenDict(var2exp)
        self._degree = sum(self.var2exp.values())
        self._key = (self.degree(), self.var2exp.key)

    def degree(self):
        return self._degree

    def __eq__(self, other):
        return self._key.__eq__(other._key)

    def __le__(self, other):
        return self._key.__le__(other._key)

    def __hash__(self):
        return hash(self._key)

    def iteritems(self):
        return self.var2exp.iteritems()

    def mul(self, other):
        assert self.semiring == other.semiring
        res = defaultdict(int)
        for v, e in self.var2exp.iteritems():
            res[v] += e
        for v, e in other.var2exp.iteritems():
            res[v] += e
        return Monomial(self.semiring, res)

    def __str__(self):
        l = []
        for v, e in self.iteritems():
            if e != 1:
                l.append("{}^{}".format(v, e))
            else:
                l.append(str(v))
        return " ".join(l)

@total_ordering
class Polynomial(BasePolynomial):
    def __init__(self, semiring, mon2coeff):
        BasePolynomial.__init__(self, semiring)
        for m, c in mon2coeff.iteritems():
            assert isinstance(m, Monomial)
            assert not isinstance(c, Polynomial)
            assert not isinstance(c, Monomial)
            assert not isinstance(c, Indeterminate)
        self.mon2coeff = FrozenDict({
            m:c
            for m, c in mon2coeff.iteritems()
                if not semiring.is_zero(c)
        })

    def negate(self):
        mon2coeff = FrozenDict({
            m:-c
            for m, c in self.mon2coeff.iteritems()
                if not self.semiring.is_zero(c)
        })
        return Polynomial(self.semiring, mon2coeff)

    def to_hash_dict(self, hash_function):
        d = defaultdict(float)
        for mon, coeff in self.mon2coeff.iteritems():
            k = hash_function(mon)
            d[k] += coeff
        return dict(d)

    def dot(self, other):
        assert isinstance(other, Polynomial)
        res = self.semiring.zero()
        for mon, c1 in self.iteritems():
            c2 = other.mon2coeff[mon]
            res += c1 * c2
        return res

    def normalize(self):
        nn = np.sqrt(self.squared_norm())
        if abs(nn) > 1e-16:
            mon2coeff = {mon:coeff/nn for mon, coeff in self.mon2coeff.iteritems()}
            return Polynomial(self.semiring, mon2coeff)
        else:
            return self

    def squared_norm(self):
        res = self.semiring.zero()
        for _, c in self.iteritems():
            res = res + c*c
        return res

    def is_zero(self, eps=1e-6):
        return self.squared_norm() < eps

    def __eq__(self, other):
        return self.mon2coeff.__eq__(other.mon2coeff)

    def __le__(self, other):
        return self.mon2coeff.__le__(other.mon2coeff)

    def __hash__(self):
        return hash(self.mon2coeff)

    def iteritems(self):
        return self.mon2coeff.iteritems()

    def add(self, other):
        assert self.semiring == other.semiring
        mon2coeff = defaultdict(self.semiring.zero)
        for mon, coeff in self.iteritems():
            assert not isinstance(coeff, Polynomial)
            mon2coeff[mon] = coeff + mon2coeff[mon]
        for mon, coeff in other.iteritems():
            assert not isinstance(coeff, Polynomial)
            mon2coeff[mon] = coeff + mon2coeff[mon]
        return Polynomial(self.semiring, mon2coeff)

    def mul(self, other):
        assert self.semiring == other.semiring
        mon2coeff = defaultdict(self.semiring.zero)
        for m1, c1 in self.iteritems():
            assert not isinstance(c1, Polynomial)
            for m2, c2 in other.iteritems():
                assert not isinstance(c2, Polynomial)
                m = m1.mul(m2)
                c = c1 * c2
                mon2coeff[m] = mon2coeff[m] + c
        return Polynomial(self.semiring, mon2coeff)

    def __str__(self):
        l = []
        for mon, coeff in self.mon2coeff.iteritems():
            l.append("{} {}".format(coeff, mon))
        return " + ".join(l)

class VariableFactoryName(object):
    def __init__(self, semiring, prefix):
        self.semiring = semiring
        self.prefix = str(prefix)
        self.name2var = {}

    def __getitem__(self, name):
        varname = "x({}{})".format(self.prefix, str(name))
        try:
            res = self.name2var[name]
        except KeyError:
            res = Indeterminate(self.semiring, varname)
            self.name2var[name] = res
        return res

class IdFunction(object):
    def __init__(self, semiring, prefix):
        self.obj2var = {}
        self.semiring = semiring
        self.factory = VariableFactoryName(semiring, prefix)
        self.i = 0

    def __call__(self, obj):
        if isinstance(obj, BasePolynomial):
            obj = polynomial(self.semiring, obj)
        try:
            res = self.obj2var[obj]
        except KeyError:
            name = self.i
            self.i += 1
            res = self.factory[self.i]
            self.obj2var[obj] = res
        res = self.semiring.one() * res
        # print "HASH", res, '->', obj
        return res