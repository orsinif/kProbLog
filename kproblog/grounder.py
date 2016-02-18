"""
Module name
"""
from problog.engine import DefaultEngine
from problog.program import PrologString
from problog.logic import *
from problog.formula import LogicFormula
# from problog.engine_stack import SimpleProbabilisticBuiltIn
from problog.engine_stack import BooleanBuiltIn

# from grounder_builtins import builtin_annotate
from grounder_builtins import BuiltinDeclarationsHelper, BuiltinAnnotationHelper, BuiltinMetafunctionHelper

import re
from collections import defaultdict

METAMETAFUNCTION_FUNCTOR = 'metafunction'

DEBUG_FLAG = False

class Metafunction(Term):
    def __init__(self, *args, **kwargs):
        Term.__init__(self, *args, **kwargs)

    def __str__(self):
        return "@{}[{}]".format(self.functor, ", ".join(map(str, self.args)))

    def __repr__(self):
        return str(self)

def and2list(body):
    if isinstance(body, And):
        return body.to_list()
    else:
        return [body]

def list2and(l):
    return And.from_list(l)


def term2str(term):
    if term.arity == 0:
        return str(term)
    else:
        ptrn = "{}[{}]" if term.functor.startswith("@") else "{}({})"
        return ptrn.format(term.functor, ", ".join(map(term2str, term.args)))

def clause2str(clause):
    if isinstance(clause, Clause):
        head = clause.head
        body = ", ".join(map(term2str, and2list(clause.body)))
        return "{} :- {}.".format(head, body)
    else:
        return "{}.".format(str(clause))


def escape_metafunctions_in_body(body):
    escaped_body_list = []
    for b in body:
        if b.functor == 'annotate':
            escaped_body_list.append(Term(METAMETAFUNCTION_FUNCTOR, Constant(b.args[0]), Constant(b.arity-1)))
            args = escape_metafunctions_in_body(b.args[1:])
            # assert len(args) == b.arity-1 , "{} != {}, --- {}".format(len(args), b.arity-1, str(b))
            escaped_body_list += args
        else:
            escaped_body_list.append(b)
    if DEBUG_FLAG:
        print "escape_metafunctions_in_body: body", body, "--> escaped_body_list", escaped_body_list
    return escaped_body_list

def unescape_metafunctions_in_body(body):
    # print "BODY", body
    function_stack = []
    value_stack = []
    # print "*" * 80
    for i, b in enumerate(body):
        # print i, "value_stack", value_stack, "function_stack", function_stack
        if b.functor == METAMETAFUNCTION_FUNCTOR:
            function_stack.append((b, len(value_stack)))
        else:
            value_stack.append(b)
            stack_size = len(value_stack)
            if function_stack:
                top_function = function_stack[-1][0]
                bp = function_stack[-1][1]  # base pointer
                metafunction_name = "@" + str(top_function.args[0])
                n_args = int(top_function.args[1])
                if stack_size == bp + n_args:
                    metafunction_args = value_stack[bp:bp+stack_size]
                    evaluation = Term(metafunction_name, *metafunction_args)
                    value_stack = value_stack[:-n_args] # remove args
                    value_stack.append(evaluation) # push evaluation
                    function_stack.pop() # remove evaluated metafunction
    assert not function_stack # function_stack must be empty
    # print "body", body, "--> value_stack", value_stack, "function_stack", function_stack
    return value_stack

def escape_metafunctions(clauses):
    res = []
    for clause in clauses:
        if isinstance(clause, Clause):
            clause = Clause(clause.head, list2and(escape_metafunctions_in_body(and2list(clause.body))))
        res.append(clause)
    return res

def unescape_metafunctions(clauses):
    res = []
    for clause in clauses:
        if isinstance(clause, Clause):
            clause = Clause(clause.head, list2and(unescape_metafunctions_in_body(and2list(clause.body))))
        res.append(clause)
    return res


class KPrologGrounder(object):
    def __init__(self, filename=None, data=None):
        assert (filename is None and data is not None) or (filename is not None and data is None)
        if filename is None:
            self.data = data
        else:
            assert data is None
            with open(filename) as f:
                self.data = f.read()
        self.builtin_metafunction = BuiltinMetafunctionHelper()
        self.builtin_declare = BuiltinDeclarationsHelper()
        self.builtin_annotate = BuiltinAnnotationHelper()

    def preprocess_metafunctions(self):
        # Step 1: remove syntactic sugar
        data, _count = re.subn('@([^(]+)[(]', r'annotate(\1, ', self.data)
        # data = self.data
        return data

    def display_preprocessed_code(self, data):
        print '=' * 80
        print "PREPROCESSED DATA"
        print '=' * 80
        print data
        print '=' * 80
        print

    def run(self):
        global DEBUG_FLAG
        data = self.preprocess_metafunctions()
        if DEBUG_FLAG:
            self.display_preprocessed_code(data)
        model = PrologString(data)
        if DEBUG_FLAG:
            print '=' * 80
            print "BEFORE ESCAPING"
            print '=' * 80
            for elem in model: print clause2str(elem)
            print '=' * 80

        model = escape_metafunctions(model)

        if DEBUG_FLAG:
            print '=' * 80
            print "AFTER ESCAPING"
            print '=' * 80
            for elem in model: print clause2str(elem)
            print '=' * 80

        engine = DefaultEngine(label_all=True)
        engine.add_builtin(METAMETAFUNCTION_FUNCTOR, 2, BooleanBuiltIn(self.builtin_metafunction))
        engine.add_builtin('declare', 2, BooleanBuiltIn(self.builtin_declare))
        engine.add_builtin('declare', 3, BooleanBuiltIn(self.builtin_declare))

        db = engine.prepare(model)
        if DEBUG_FLAG:
            print "=" * 80
            print "DATABASE"
            print "=" * 80
            for elem in db: print elem
            print "=" * 80

        gp = LogicFormula(
            keep_all=True,
            keep_order=True,
            keep_duplicates=True,
            avoid_name_clash=True
        )

        gp = engine.ground_all(db, target=gp)
        if DEBUG_FLAG:
            print "=" * 80
            print "GROUND PROGRAM (GROUNDER)"
            print "=" * 80
            for elem in gp.enum_clauses():
                print elem
            print "=" * 80
        clauses = []
        facts = []
        for clause in unescape_metafunctions(gp.enum_clauses()):
            if isinstance(clause, Clause):
                clauses.append(clause)
            else:
                facts.append(clause)

        query_atoms = gp._names['query']
        return self.builtin_declare.declarations, clauses + facts, query_atoms
