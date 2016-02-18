from problog.logic import Term, Constant
from .float_semiring import FloatSemiring
from kprolog.evaluation.utils import Metafunction
from kprolog.evaluation.mappings import METAFUNCTION_TO_FUNCTION
__author__ = 'francesco'

def eval_expr(expr):
    # TODO make non recursive
    if isinstance(expr, Term) and not isinstance(expr, Metafunction):
        if expr.functor == '*':
            return eval_expr(expr.args[0]) * eval_expr(expr.args[1])
        elif expr.functor == '+':
            return eval_expr(expr.args[0]) + eval_expr(expr.args[1])
        elif expr.functor == '^':
            return eval_expr(expr.args[0]) ** eval_expr(expr.args[1])
        elif isinstance(expr, Constant):
            return expr.compute_value()
        else:
            raise RuntimeError
    elif isinstance(expr, Metafunction):
        f = METAFUNCTION_TO_FUNCTION[str(expr.function)]
        args = tuple(map(eval_expr, expr.args))
        return f(*args)
    else:
        return float(expr)


class FloatExprSemiring(FloatSemiring):
    def __init__(self, eps=None):
        FloatSemiring.__init__(self, eps)

    def value(self, expr):
        return eval_expr(expr)
