__author__ = 'francesco'

class FrozenDict(object):
    def __init__(self, d):
        self.d = dict(d)
        self.key = tuple(sorted(self.d.iteritems()))
        self._hash = hash(self.key)

    def __getitem__(self, *args):
        return self.d.__getitem__(*args)

    def iteritems(self):
        return iter(self.key)

    def keys(self):
        return self.d.keys()

    def values(self):
        return self.d.values()

    def has_key(self, *args):
        return self.d.has_key(*args)

    def __contains__(self, *args):
        return self.d.__contains__(*args)

    def __eq__(self, other):
        return self.key == other.key

    def __le__(self, other):
        return self.key.__le__(other.key)

    def __hash__(self):
        return self._hash

    def __str__(self):
        return str(self.d)

    def __repr__(self):
        return repr(self.d)