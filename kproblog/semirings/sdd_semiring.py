from problog.sdd_formula import sdd
from .semiring import Semiring

__author__ = 'francesco'

class ProbabilisticSDDSemiring(Semiring):
    def __init__(self, varcount=None):
        auto_gc = True
        if varcount is None:
            varcount = 1
        self.__manager = sdd.sdd_manager_create(varcount, auto_gc)
        self.varcount = varcount
        self.atom2node = {}
        self.current_node = 1
        self.logspace = 0
        self.node2weight = {}

    def resolve_atom2node(self, atom):
        # if not (isinstance(atom, Atom) or isinstance(atom, BogusAtom)):
        #     raise TypeError
        try:
            node = self.atom2node[atom]
        except KeyError:
            node = self.current_node
            self.current_node += 1
            self.atom2node[atom] = node
        return node

    def _add_variable(self, label=0):
        if label == 0 or label > self.varcount:
            sdd.sdd_manager_add_var_after_last(self.__manager)
            self.varcount += 1
            return self.varcount
        else:
            return label

    def _literal(self, label):
        self._add_variable(abs(label))
        return sdd.sdd_manager_literal(label, self.__manager)

    def is_one(self, node):
        return sdd.sdd_node_is_true(node)

    def one(self):
        return sdd.sdd_manager_true(self.__manager)

    def is_zero(self, node):
        return sdd.sdd_node_is_false(node)

    def zero(self):
        return sdd.sdd_manager_false(self.__manager)

    def plus(self, a, b):
        return self.disjoin(a, b)

    def times(self, a, b):
        return self.conjoin(a, b)

    def conjoin(self, *nodes):
        r = self.one()
        for s in nodes:
            r1 = sdd.sdd_conjoin(r, s, self.__manager)
            self.ref(r1)
            self.deref(r)
            r = r1
        return r

    def disjoin(self, *nodes):
        r = self.zero()
        for s in nodes:
            r1 = sdd.sdd_disjoin(r, s, self.__manager)
            self.ref(r1)
            self.deref(r)
            r = r1
        return r

    def equiv(self, node1, node2):
        not1 = self.negate(node1)
        not2 = self.negate(node2)
        i1 = self.disjoin(not1, node2)
        self.deref(not1)
        i2 = self.disjoin(node1, not2)
        self.deref(not2)
        r = self.conjoin(i1, i2)
        self.deref(i1, i2)
        return r

    def negate(self, node):
        new_sdd = sdd.sdd_negate(node, self.__manager)
        self.ref(new_sdd)
        return new_sdd

    def same(self, node1, node2):
        # Assumes SDD library always reuses equivalent nodes.
        if node1 is None or node2 is None:
            return node1 == node2
        else:
            return int(node1) == int(node2)

    def approx_equal(self, a, b):
        return self.same(a, b)

    def ref(self, *nodes):
        for node in nodes:
            sdd.sdd_ref(node, self.__manager)

    def deref(self, *nodes):
        for node in nodes:
            sdd.sdd_deref(node, self.__manager)


    def result(self, a):
        return float(a)

    def parse(self, atom, weight):
        node = self.resolve_atom2node(atom)
        weight_float = float(weight)
        if weight_float < 0 or weight_float > 1:
            raise ValueError
        self.node2weight[node] = weight_float
        return atom, self._literal(node)

    def value(self, a):
        return self._wmc(a, self.node2weight)


    def get_evaluate_metafunction(self):
        def evaluate(node):
            return self._wmc(node, self.node2weight)
        return evaluate

    def _wmc(self, node, weights):
        wmc_manager = sdd.wmc_manager_new(node, self.logspace, self.__manager)
        varcount = sdd.sdd_manager_var_count(self.__manager)
        for i, n in enumerate(sorted(weights)):
            i += 1
            pos = weights[n]
            neg = 1. - pos
            if n <= varcount:
                sdd.wmc_set_literal_weight(n, pos, wmc_manager)  # Set positive literal weight
                sdd.wmc_set_literal_weight(-n, neg, wmc_manager)  # Set negative literal weight
        result = sdd.wmc_propagate(wmc_manager)
        sdd.wmc_manager_free(wmc_manager)
        return result
