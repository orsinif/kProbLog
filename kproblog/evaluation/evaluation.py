from collections import defaultdict

from antlr4 import *
import networkx as nx

from kproblog.evaluation.utils import Rule, Atom, BogusAtom, Metafunction
from kproblog.evaluation.parser.GKPrologLexer import GKPrologLexer
from kproblog.evaluation.parser.GKPrologParser import GKPrologParser
from kproblog.evaluation.visitor import GKPrologEvaluationVisitor
from kproblog.evaluation.mappings import BUILTIN_PREDICATES

DEBUG_FLAG = False
if DEBUG_FLAG:
    import datadiff


__author__ = 'francesco'

if DEBUG_FLAG:
    def dict_in_dict_out(F):
        def wrapper(x):
            assert isinstance(x, dict), (type(x), x)
            res = F(x)
            assert isinstance(res, dict), type(res)
            return res
        return wrapper

    def dict_in(F):
        def wrapper(x):
            assert isinstance(x, dict), type(x)
            res = F(x)
            return res
        return wrapper
else:
    def dict_in_dict_out(F): return F
    def dict_in(F): return F


class Stratum(object):
    def __init__(self, stratum_atoms, rules):
        stratum_atoms = set(stratum_atoms)
        self.cyclic = []
        self.acyclic = []
        for rule in rules:
            rule_dep_set = rule.get_direct_dependencies()
            if stratum_atoms.intersection(rule_dep_set): # non-empty intersection
                self.cyclic.append(rule)
            else: # empty intersection
                self.acyclic.append(rule)

    def __nonzero__(self):
        return bool(self.cyclic) or bool(self.acyclic)

    def __repr__(self):
        return "Stratum(acyclic={}, cyclic={})".format(self.acyclic, self.cyclic)

    def __str__(self):
        ret = "Stratum(acyclic=[{}], cyclic=[{}])"\
                .format(", ".join(map(str, self.acyclic)), ", ".join(map(str, self.cyclic)))
        return ret


class DependencyGraph(object):
    def __init__(self):
        self.dep_graph = nx.DiGraph()
        self.head2rules = defaultdict(list)

    def add_rule(self, rule):
        if not isinstance(rule, Rule):raise TypeError
        self.head2rules[rule.head].append(rule)
        for atom in rule.get_direct_dependencies():
            self.dep_graph.add_edge(atom, rule.head)

    def add_rules(self, rules):
        for rule in rules:
            self.add_rule(rule)

    def debug_print(self):
        for v in self.dep_graph.nodes():
            print v, "ancestors", ', '.\
                join(map(str, sorted(nx.ancestors(self.dep_graph, v))))

    def condensation(self):
        if DEBUG_FLAG:
            print "self.dep_graph.number_of_nodes()", self.dep_graph.number_of_nodes()
        c0 = nx.condensation(self.dep_graph)
        for cnode in c0.nodes():
            stratum_atoms = c0.node[cnode]['members']
            rules = []
            for atom in stratum_atoms:
                for rule in self.head2rules[atom]:
                    rules.append(rule)
            c0.node[cnode]['stratum'] = Stratum(stratum_atoms, rules)
        return c0

    def get_evaluation_sequence(self):
        if self.dep_graph.number_of_nodes() > 0:
            c = self.condensation()
            ret = [ c.node[node]['stratum']
                    for node in nx.topological_sort(c)
                        if c.node[node]['stratum'] # strata might be empty and we do not want it
                ]
        else:
            ret = []
        return ret

class RuleCompiler(object):
    def __init__(self, metafunction2function, pred2semiring, pred2update_type):
        self.metafunction2function = metafunction2function
        self.pred2semiring = pred2semiring
        self.pred2update_type = pred2update_type

    def resolve_atom_semiring(self, atom):
        return self.pred2semiring[atom.predicate]

    def resolve_update_type(self, atom):
        ret = self.pred2update_type[atom.predicate]
        assert ret in {'additive', 'destructive'}
        return ret

    def compile_body_atom(self, body_atom):
        if isinstance(body_atom, Atom) or isinstance(body_atom, BogusAtom):
            if body_atom.predicate in self.pred2semiring:
                @dict_in
                def get_weight(atom2weight):
                    assert isinstance(atom2weight, dict), type(atom2weight)
                    if body_atom not in atom2weight:
                        semiring = self.resolve_atom_semiring(body_atom)
                        atom2weight[body_atom] = semiring.zero()
                    return atom2weight[body_atom]
                return get_weight
            else:
                raise RuntimeError, "this branch must be unreachable"
        elif isinstance(body_atom, Metafunction):
            function = self.metafunction2function[str(body_atom.function)]
            f_list = self.compile_body_atom_list(body_atom.args)
            @dict_in
            def rfunction(atom2weight):
                args = tuple(f(atom2weight) for f in f_list)
                return function(*args)
            return rfunction
        else:
            raise TypeError

    def compile_body_atom_list(self, body_atom_list):
        f_list = []
        for body_atom in body_atom_list:
            if isinstance(body_atom, Metafunction) or body_atom.predicate in self.pred2semiring:
                f = self.compile_body_atom(body_atom)
                f_list.append(f)
            else:
                if body_atom.predicate not in BUILTIN_PREDICATES:
                    raise ValueError, "undeclared predicate {} for atom {}".format(str(body_atom.predicate), type(body_atom))

        f_list = tuple(f_list)
        return f_list

    def compile_rule_body(self, rule):
        semiring = self.resolve_atom_semiring(rule.head)
        body_atom_list = rule.body
        f_list = self.compile_body_atom_list(body_atom_list)
        n_atoms = len(f_list)
        if n_atoms == 0:
            if len(body_atom_list) == 0: raise RuntimeError, "language implementation error"
            @dict_in
            def rfunction(atom2weight):
                return semiring.zero()
            return rfunction
        elif n_atoms == 1:
            return f_list[0]
        else: # n_atoms > 1
            @dict_in
            def rfunction(atom2weight):
                acc = f_list[0](atom2weight)
                for f in f_list[1:]:
                    acc = semiring.times(acc, f(atom2weight))
                return acc
            return rfunction

    def _compile_rules_with_the_same_head(self, head, rules):
        """TODO it is aprivate method because you need to make sure
        that all the rules given as input have the same head"""
        semiring = self.resolve_atom_semiring(head)
        n_rules = len(rules)
        f_list = [self.compile_rule_body(rule) for rule in rules]

        if n_rules == 0: # if there are no rules no update needs to be done
            def rfunction(atom2weight):
                return {}
            return rfunction
        elif n_rules == 1:
            return self.compile_rule_body(rules[0])
        else: # n_rules > 1
            @dict_in
            def rfunction(atom2weight):
                acc = f_list[0](atom2weight)
                for f in f_list[1:]:
                    acc = semiring.plus(acc, f(atom2weight))
                return acc
            return rfunction

    def compile_weight_delta(self, rules):
        head2rules = defaultdict(list)
        for rule in rules:
            head2rules[rule.head].append(rule)
        head2rules = dict(head2rules)
        head2f = {
            head: self._compile_rules_with_the_same_head(head, rules)
                for head, rules in head2rules.iteritems()
        }

        head2semiring = {
            head:self.resolve_atom_semiring(head)
                for head in head2rules
        }

        @dict_in_dict_out
        def rfunction(atom2weight):
            ret = {}
            for head, f in head2f.iteritems():
                weight_value = f(atom2weight)
                semiring = head2semiring[head]
                if not semiring.is_zero(weight_value):
                    ret[head] = weight_value
            return ret

        return rfunction

    def compile_weight_update(self):
        def weight_update(atom2weight, delta_atom2weight):
            res = {}
            atom_set = set(atom2weight.keys()).union(set(delta_atom2weight.keys()))
            for atom in atom_set:
                if atom in atom2weight and atom in delta_atom2weight:
                    update_type = self.resolve_update_type(atom)
                    if update_type == 'additive':
                        semiring = self.resolve_atom_semiring(atom)
                        res[atom] = semiring.plus(atom2weight[atom], delta_atom2weight[atom])
                    elif update_type == 'destructive':
                        res[atom] = delta_atom2weight[atom]
                    else:
                        raise RuntimeError, "this code should be unreachable"
                elif atom in atom2weight and atom not in delta_atom2weight:
                    res[atom] = atom2weight[atom]
                elif atom not in atom2weight and atom in delta_atom2weight:
                    res[atom] = delta_atom2weight[atom]
                else:
                    raise RuntimeError, "this code should be unreachable"
            return res
        return weight_update

    def compile_additive_weight_update(self):
        def additive_weight_update(atom2weight, delta_atom2weight):
            res = {}
            atom_set = set(atom2weight.keys()).union(set(delta_atom2weight.keys()))
            for atom in atom_set:
                if atom in atom2weight and atom in delta_atom2weight:
                    semiring = self.resolve_atom_semiring(atom)
                    res[atom] = semiring.plus(atom2weight[atom], delta_atom2weight[atom])
                elif atom in atom2weight and atom not in delta_atom2weight:
                    res[atom] = atom2weight[atom]
                elif atom not in atom2weight and atom in delta_atom2weight:
                    res[atom] = delta_atom2weight[atom]
                else:
                    raise RuntimeError, "this code should be unreachable"
            return res
        return additive_weight_update

    def compile_same_weights(self):
        def same_weights(a, b):
            keys = set(a.keys())
            if set(b.keys()) == keys:
                for atom in keys:
                    semiring = self.resolve_atom_semiring(atom)
                    wa = a[atom]
                    wb = b[atom]
                    if not semiring.approx_equal(wa, wb):
                        return False
                return True
            else:
                return False
        return same_weights

    def compile_stratum_function(self, stratum):
        acyclic_function = self.compile_weight_delta(stratum.acyclic)
        cyclic_function = self.compile_weight_delta(stratum.cyclic)
        weight_update = self.compile_weight_update()
        additive_weight_update = self.compile_additive_weight_update()
        same_weights = self.compile_same_weights()
        @dict_in_dict_out
        def rfunction(atom2weight):
            delta_atom2weight = acyclic_function(atom2weight)
            atom2weight = additive_weight_update(atom2weight, delta_atom2weight)
            if DEBUG_FLAG:
                print ">> stratum", [
                    "{}::{}".format(str(weight), str(atom))
                    for atom, weight in atom2weight.iteritems()
                ]
            while True:
                atom2weight_old = atom2weight
                delta_atom2weight = cyclic_function(atom2weight)
                atom2weight = weight_update(atom2weight, delta_atom2weight)
                if DEBUG_FLAG:
                    print "DIFF", datadiff.diff(atom2weight_old, atom2weight)
                if same_weights(atom2weight_old, atom2weight):
                    break
            if DEBUG_FLAG:
                print
            return atom2weight
        return rfunction

    def compile_evaluation_sequence(self, stratum_list):
        stratum_funct_list = [
            self.compile_stratum_function(stratum)
                for stratum in stratum_list
            ]
        @dict_in_dict_out
        def rfunction(atom2weight):
            stratum_i = 0
            if DEBUG_FLAG:
                print "> stratum", stratum_i, [
                    "{}::{}".format(str(weight), str(atom))
                        for atom, weight in atom2weight.iteritems()
                ]
            for stratum_funct in stratum_funct_list:
                stratum_i += 1
                atom2weight = stratum_funct(atom2weight)
                if DEBUG_FLAG:
                    print "> stratum", stratum_i, [
                        "{}::{}".format(str(weight), str(atom))
                        for atom, weight in atom2weight.iteritems()
                    ]
            return { atom: self.resolve_atom_semiring(atom).value(weight)
                for atom, weight in atom2weight.iteritems() }
        return rfunction


def filter_rules(rules, pred2semiring):
    res = []
    for rule in rules:
        if isinstance(rule, Rule) and rule.head.predicate in pred2semiring:
            new_body = []
            for b in rule.body:
                if isinstance(b, Metafunction) or b.predicate in pred2semiring:
                    new_body.append(b)

            if new_body: # means the body is not empty
                res.append(Rule(rule.head, tuple(new_body)))
    return res

class GKProbLog(object):
    def __init__(self, typename_to_semiring=None, metafunction_to_function=None, query_atoms=None, file_name=None, code=None):
        if file_name is not None and code is None:
            self.finput = FileStream(file_name)
        elif file_name is None and code is not None:
            self.finput = InputStream(code)
        else:
            raise RuntimeError, "you must give one and only one between file_name and code"
        self.typename_to_semiring = typename_to_semiring
        self.metafunction_to_function = metafunction_to_function
        self.query_atoms = query_atoms
        if DEBUG_FLAG:
            print "query_atoms", query_atoms

    def run(self):
        lexer = GKPrologLexer(self.finput)
        stream = CommonTokenStream(lexer)
        parser = GKPrologParser(stream)
        tree = parser.program0()
        visitor = GKPrologEvaluationVisitor(self.typename_to_semiring)

        rules = visitor.visit(tree)
        # print ">>>>>", set(map(type, rules))
        rules = filter_rules(rules, visitor.pred2semiring)
        if DEBUG_FLAG:
            self.display_rules(rules)
            self.display_weighted_facts(visitor)

        dep_graph = DependencyGraph()
        dep_graph.add_rules(rules)

        if DEBUG_FLAG:
            dep_graph.debug_print()
            self.display_query_atoms(visitor)
            self.display_condensation(dep_graph)

        stratum_list = dep_graph.get_evaluation_sequence()

        if DEBUG_FLAG:
            self.display_evaluation_sequence(stratum_list)

        rule_compiler = RuleCompiler(
            self.metafunction_to_function,
            visitor.pred2semiring,
            visitor.pred2update_type
        )
        evaluation_function = rule_compiler\
            .compile_evaluation_sequence(stratum_list)
        if DEBUG_FLAG:
            print '=' * 80
            print "INITIAL WEIGHTS"
            print '=' * 80
            for a, w in visitor.weight_manager.atom2weight.iteritems():
                print a, ": ", w, "-->", type(w)
            print '=' * 80

        final_weights = evaluation_function(visitor.weight_manager.atom2weight)
        if DEBUG_FLAG:
            print "FINAL WEIGHTS"
            print {(k, k.to_term()):v for k, v in final_weights.iteritems()}
            print
        return self.display_result(final_weights)

    def display_weighted_facts(self, visitor):
        print 80 * '='
        print "WEIGHTED FACTS"
        print 80 * '='
        for atom, weight in visitor.weight_manager.iteritems():
            print weight, '::', atom

    def display_rules(self, rules):
        print '=' * 80
        print "RULES"
        print '=' * 80
        for elem in rules:
            print str(elem)

    def display_condensation(self, dep_graph):
        print '=' * 80
        print "CONDENSATION"
        print '=' * 80
        for node, attrs in dep_graph.condensation().nodes(data=True):
            print node, bool(attrs['stratum']), attrs['stratum']

    def display_evaluation_sequence(self, stratum_list):
        print '=' * 80
        print "EVALUATION SEQUENCE"
        print '=' * 80
        for stratum_i, stratum in enumerate(stratum_list, 1):
            print stratum_i, ')'
            print str(stratum)
            print

    def display_query_atoms(self, visitor):
        print "=" * 80
        print "QUERY ATOMS"
        print "=" * 80
        for atom_list in visitor.query_atoms_nested_list:
            print ", ".join(map(str, atom_list))

    def display_result(self, final_weights):
        # TODO make it work with Terms rather than strings
        if DEBUG_FLAG:
            print '=' * 80
            print "RESULT"
            print '=' * 80

            print "DEBUG query_atoms:"
            if self.query_atoms is not None:
                for qa in self.query_atoms.keys():
                    print "Q", qa, type(qa.functor), map(type, qa.args)
                    print
            print "RESULT ATOMS"
        qstrs = set(map(str, self.query_atoms.keys())) if self.query_atoms is not None else None
        result = []
        for atom, weight in final_weights.iteritems():
            term = str(atom.to_term())
            if qstrs is None or term in qstrs:
                # print "{}::{}.".format(weight, term)
                result.append((weight, term))
        return result
