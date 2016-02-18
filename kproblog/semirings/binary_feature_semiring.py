from .semiring import Semiring
import numpy as np
from scipy.stats import logistic

__author__ = 'francesco'

class FeatureSemiring(Semiring):
    def __init__(self, float_eps, batch_size):
        self.float_eps = float_eps
        self.batch_size = batch_size

    def value(self, term):
        if term.functor != 'attr': raise ValueError
        term.args[0]
        term.args[0]


    def parse(self, atom, weight):
        return atom, self.value(weight)

    def is_one(self, value):
        return self.is_zero(FeatureObj(value.v-1.))

    def zero(self):
        return FeatureObj(np.array([0.]))

    def result(self, a):
        return a

    def is_zero(self, value):
        return ((value.v )**2).mean() < self.float_eps # TODO double check this criterion

    def times(self, a, b):
        return a * b

    def plus(self, a, b):
        return a + b

    def approx_equal(self, a, b):
        return self.is_zero(FeatureObj(a.v-b.v))

    def one(self):
        return FeatureObj(np.array([1.]))


class FeatureObj(object):
    def __init__(self, v, is_zero_one_flag):
        self.v = v
        self.is_zero_one_flag = is_zero_one_flag

    def sigmoid(self):
        return FeatureObj(logistic.cdf(self.v), True) # TODO pay attention to rounding errors

    def sample(self):
        if not self.is_zero_one_flag:
            raise RuntimeError
        return FeatureObj((np.random.rand(*self.v.shape) < self.v)* 1., True)

    def sum_minibatch(self):
        return FeatureObj(np.array([self.v.sum()]), False)

    def __add__(self, other):
        return FeatureObj(self.v + other.v, False)

    def __mul__(self, other):
        return FeatureObj(self.v * other.v, False)


