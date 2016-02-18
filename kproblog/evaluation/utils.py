from collections import namedtuple
from problog.logic import Term

__author__ = 'francesco'

################################################################################
# TERMS END
################################################################################

Predicate = namedtuple("Predicate", "functor arity")
WeightedRule = namedtuple("WeightedRule", "weight head body")
Fact = namedtuple("Fact", "atom")
# WeightedFact = namedtuple("WeightedFact", "weight atom")


class WeightedFact(object):
    def __init__(self, weight, atom):
        # assert isinstance(weight, Term), type(weight)
        self.weight = weight
        self.atom = atom

class Atom(object):
    def __init__(self, predicate, *args, **kwdargs):
        assert predicate is not None
        self.predicate = predicate
        self.args  = args
        self.functor = str(self.predicate.functor)

    def to_term(self):
        return Term(self.functor, *self.args)

    def __eq__(self, other):
        if isinstance(other, Atom):
            return (self.predicate == other.predicate) and (self.args == other.args)
        else:
            return False

    def __hash__(self):
        return hash((self.predicate, self.args))

    def __repr__(self):
        return "Atom(predicate={}, args={})".format(str(self.predicate), str(self.args))

    def __str__(self):
        if self.predicate.arity == 0:
            return str(self.predicate.functor)
        else:
            return "{}({})".format(self.predicate.functor, ", ".join(map(str, self.args)))


class BogusAtom(object):
    def __init__(self, predicate, atom_id):
        self.predicate = predicate
        self.atom_id = atom_id
        self.functor = str(self.predicate.functor)

    def to_term(self):
        return Term("__bogus__" + self.functor, str(self.atom_id))


    def __eq__(self, other):
        if isinstance(other, BogusAtom):
            return self.predicate == other.predicate and \
                self.atom_id == other.atom_id
        else:
            return False

    def __hash__(self):
        return hash((self.predicate, self.atom_id))

    def __repr__(self):
        return "BogusAtom(predicate={}, atom_id={})".format(str(self.predicate), str(self.atom_id))

    def __str__(self):
        return "<BogusAtom>({})".format(self.atom_id)


class BogusAtomManager(object):
    def __init__(self, pred2semiring):
        self.pred2semiring = pred2semiring
        self._bogus_atom_id = 0

    def create_bogus_atom(self, predicate):
        if not isinstance(predicate, Predicate):
            raise TypeError
        if predicate not in self.pred2semiring:
            raise RuntimeError, "undeclared {}, {}".format(str([predicate]), str(self.pred2semiring))

        atom_id = self._bogus_atom_id
        self._bogus_atom_id += 1
        return BogusAtom(predicate, atom_id)


class Rule(object):
    def __init__(self, head, body):
        self.head = head
        self.body = body

    def __eq__(self, other):
        if isinstance(other, Rule):
            return self.head == other.head and \
                self.body == other.body
        else:
            return False

    def __hash__(self):
        return hash((self.head, self.body))

    def get_direct_dependencies(self):
        res = set()
        for atom in self.body:
            if isinstance(atom, Metafunction):
                res = res.union(atom.get_direct_dependencies())
            else:
                if not isinstance(atom, Atom) and not isinstance(atom, BogusAtom):
                    raise TypeError, type(atom)
                res.add(atom)
        return res

    def __iter__(self):
        yield self.head
        yield self.body

    def __repr__(self):
        return "Rule(head={}, body={})".format(self.head, self.body)

    def __str__(self):
        return "{} :- {}.".format(str(self.head), ', '.join(map(str, self.body)))


class Metafunction(object):
    def __init__(self, function, args):
        self.function = function
        self.args = args

    def get_direct_dependencies(self):
        res = set()
        for atom in self.args:
            if isinstance(atom, Metafunction):
                res = res.union(atom.get_direct_dependencies())
            else:
                if not isinstance(atom, Atom) and not isinstance(atom, BogusAtom):
                    raise TypeError, type(atom)
                res.add(atom)
        return res

    def __iter__(self):
        yield self.function
        yield self.args

    def __repr__(self):
        return "Metafunction(function={}, args={})".format(str(self.function), str(self.args))

    def __str__(self):
        return "@{}[{}]".format(self.function, ', '.join(map(str, self.args)))


class WeightManager(object):
    def __init__(self, pred2semiring_obj):
        self.atom2weight = {}
        self.pred2semiring_obj = pred2semiring_obj

    def _check(self, atom):
        # TODO also parse and check that the weight is compatible with the semiring type
        if atom.predicate not in self.pred2semiring_obj:
            raise RuntimeError, "undeclared {}".format(str(atom.predicate))

    def iteritems(self):
        return self.atom2weight.iteritems()

    def set_weight(self, atom, weight):
        self._check(atom)
        # atom, weight = self.pred2semiring_obj[atom.predicate].parse(atom, weight)
        if atom in self.atom2weight:
            raise RuntimeError, "{} already in {}".format(atom, self.atom2weight.keys())
        self.atom2weight[atom] = weight

    def get_weight(self, atom):
        if not isinstance(atom, Atom):
            raise TypeError
        return self.atom2weight[atom]
