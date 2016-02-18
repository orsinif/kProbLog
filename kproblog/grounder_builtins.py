from problog.logic import And, Term, Clause

__author__ = 'francesco'

# def builtin_annotate(annotation, *terms, **kwdargs):
#     return builtin_annotate_help(annotation, terms, **kwdargs)
#
# def builtin_annotate_help(annotation, terms, target=None, database=None, engine=None, **kwdargs):
#     body = And.from_list(terms)
#     body_vars = body.variables()
#
#     clause_head = Term(engine.get_non_cache_functor(), *body_vars)
#     clause = Clause(clause_head, body)
#     subdb = database.extend()
#     subdb += clause
#
#     results = engine.call(clause_head, subcall=True, database=subdb, target=target, **kwdargs)
#     target.annotations[clause_head.functor] = annotation
#     output = []
#     for res, node in results:
#         varvalues = {var: val for var, val in zip(body_vars, res)}
#         output.append(([annotation] + [term.apply(varvalues) for term in terms], node))
#     return output

class BuiltinDeclarationsHelper(object):
    def __init__(self):
        self.declarations = []

    def __call__(self, declare, *terms, **kwdargs):
        return self.call_helper(declare, terms, **kwdargs)

    def call_helper(self, declare, terms, target=None, database=None, engine=None, **kwdargs):
        declared_pred = "{}/{}".format(*tuple(map(str, [declare.args[0],declare.args[1]])))
        args = [declared_pred,] +  map(str, terms)
        s = ":- declare({}).".format(", ".join(args))
        self.declarations.append(s)
        return True

# builtin_declare_help = BuiltinDeclarationsHelper()


class BuiltinAnnotationHelper(object):
    def __init__(self):
        self.annotations = {}

    def __call__(self, annotation, *terms, **kwdargs):
        return self.builtin_annotate_help(annotation, terms, **kwdargs)

    def builtin_annotate_help(self, annotation, terms, target=None, database=None, engine=None, **kwdargs):
        body = And.from_list(terms)
        body_vars = body.variables()

        clause_head = Term(engine.get_non_cache_functor(), *body_vars)
        clause = Clause(clause_head, body)
        subdb = database.extend()
        subdb += clause

        results = engine.call(clause_head, subcall=True, database=subdb, target=target, **kwdargs)
        self.annotations[clause_head.functor] = annotation
        output = []
        for res, node in results:
            varvalues = {var: val for var, val in zip(body_vars, res)}
            output.append(([annotation] + [term.apply(varvalues) for term in terms], node))
        return output

class BuiltinMetafunctionHelper(object):
    def __call__(self, declare, *terms, **kwdargs):
        return self.call_helper(declare, terms, **kwdargs)

    def call_helper(self, declare, terms, target=None, database=None, engine=None, **kwdargs):
        # declared_pred = "{}/{}".format(*tuple(map(str, [declare.args[0],declare.args[1]])))
        # args = [declared_pred,] +  map(str, terms)
        # s = ":- declare({}).".format(", ".join(args))
        # self.declarations.append(s)
        return True