from kproblog.semirings.int_semiring import IntSemiring
from kproblog.semirings.float_semiring import FloatSemiring
from kproblog.semirings.sdd_semiring import ProbabilisticSDDSemiring
from kproblog.semirings.tropical_semiring import TropicalSemiring
from kproblog.semirings.boolean_semiring import BooleanSemiring
from kproblog.semirings.term_semiring import TermSemiring
from kproblog.semirings.poly_semiring import PolynomialSemiring
from kproblog.semirings.language_semiring import LangSemiring
from kproblog.semirings.polynomial_obj import IdFunction
from kproblog.semirings.python_semiring import PythonSemiring
from kproblog.semirings.gradient_semiring import GradientSemiring

from problog.logic import Term
import numpy as np
from kproblog.evaluation.utils import Predicate


def f_debug(*args): return Term('f_debug', *args)
def g_debug(*args): return Term('g_debug', *args)

__author__ = 'francesco'

BIG_PRIME = 2**31-1

class NHash(object):
    def __init__(self, max_hash):
        if max_hash > BIG_PRIME: raise ValueError
        self.max_hash = max_hash

    def __call__(self, x):
        h = hash(x)
        if h >= 0:
            h *= 2
        else:
            h *= -2
            h += 1
        return int((h % BIG_PRIME) % self.max_hash)

float_semiring = FloatSemiring(1e-8)
int_semiring = IntSemiring()

polynomial_float = PolynomialSemiring(float_semiring)
polynomial_int = PolynomialSemiring(int_semiring)

idf_function = IdFunction(float_semiring, 'f#')
id_function = IdFunction(int_semiring, 'i#')

python_semiring = PythonSemiring()

def sample_bernoulli(prob):
    if isinstance(prob, np.ndarray):
        r = np.random.rand(*prob.shape)
    else:
        r = np.random.rand()
    return r < prob

def sv_feature(poly, max_hash):
    nhash = NHash(max_hash)
    d = poly.to_hash_dict(nhash)
    acc = python_semiring.zero()
    for k in sorted(d):
        kobj = python_semiring.value(k)
        freqobj = python_semiring.value(d[k])
        elem = python_semiring.times(kobj, freqobj)
        # print "elem", elem
        acc = python_semiring.plus(acc, elem)
    # print "acc", acc
    return acc


TYPENAME_TO_SEMIRING = {
    'int': int_semiring,
    'float': float_semiring,
    'real': float_semiring,
    'prob_sdd': ProbabilisticSDDSemiring(),
    'tropical': TropicalSemiring(),
    'boolean': BooleanSemiring(),
    'term': TermSemiring(),
    'polynomial(float)': polynomial_float,
    'polynomial(int)': polynomial_int,
    'string': LangSemiring(),
    'pyobj': python_semiring,
    'grad':GradientSemiring(),
    # 'float_expr': FloatExprSemiring(1e-15),
    # 'binary_examples': FeatureSemiring(),
}

def grad_metafunction(x, dim):
    # assert isinstance(dim, Term)
    # print "type(dim.functor)", type(dim.functor)
    # print "(dim.functor)", (dim.functor)
    # print "(dim.arity)", (dim.arity)
    # print "type(dim.functor.functor)", type(dim.functor.functor)
    # print "(dim.functor.functor)", (dim.functor.functor)
    # print "(dim.functor.arity)", (dim.functor.arity)
    # print "(dim.functor.args)", (dim.functor.args)
    # assert dim.functor == 'eps' and dim.arity == 1
    # print "grad", x, "<>", dim
    dim = dim.functor # TODO FIXME
    return x.grad(dim)

METAFUNCTION_TO_FUNCTION = {
    'sqrt': lambda x: x ** 0.5,
    'square': lambda x: x * x,
    'minus': lambda x: -x,
    'invert': lambda x: 1./x,
    'subtraction': lambda a, b: a-b,
    'div': lambda x, y: x * 1. / y,
    'logistic': lambda c, x: c * x * (1. - x),
    'normal1d': lambda sigma: np.random.randn(1)*sigma,
    'cos': np.cos,
    'g': f_debug,
    'f': g_debug,
    'idf': idf_function,
    'id': id_function,
    'rand_uniform': np.random.uniform,
    'sigmoid':lambda x: 1. / (1 + np.exp(x)),
    'sample_bernoulli': sample_bernoulli,
    'sv_feature': sv_feature,
    'grad': grad_metafunction
}


BUILTIN_PREDICATES = {
    Predicate("'\='", 2),
    Predicate("'<'", 2),
    Predicate("'>'", 2),
    Predicate("'is'", 2),
    Predicate('<', 2),
    Predicate('range', 3),
}

