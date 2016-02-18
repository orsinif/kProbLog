__author__ = 'francesco'


class Semiring(object):
    def one(self):
        """Returns the identity element of the multiplication."""
        raise NotImplementedError()

    def approx_equal(self, a, b):
        raise NotImplementedError()

    # def is_one(self, value):
    #     """Tests whether the given value is the identity element of the multiplication."""
    #     raise NotImplementedError()

    def zero(self):
        """Returns the identity element of the addition."""
        raise NotImplementedError()

    def is_zero(self, value):
        """Tests whether the given value is the identity element of the addition."""
        raise NotImplementedError()

    def plus(self, a, b):
        """Computes the addition of the given values."""
        raise NotImplementedError()

    def times(self, a, b):
        """Computes the multiplication of the given values."""
        raise NotImplementedError()

    def value(self, a):
        """Transform the given external value into an internal value."""
        raise NotImplementedError()

    def parse(self, atom, weight):
        raise NotImplementedError()

    def result(self, a):
        """Transform the given internal value into an external value."""
        raise NotImplementedError()

    def to_int(self, value):
        return int(value)

    def pow(self, base, expo):
        acc = self.one()
        expo = self.to_int(expo)
        for i in xrange(expo):
            acc =self.times(base, acc)
        return acc