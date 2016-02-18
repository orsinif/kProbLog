import warnings
warnings.simplefilter("ignore")

from kproblog.evaluation.utils import BogusAtomManager

from kproblog.evaluation.parser.GKPrologVisitor import GKPrologVisitor
from kproblog.semirings.semiring import Semiring
from problog.logic import Term, Constant
from kproblog.evaluation.utils import WeightManager, Predicate, Atom, WeightedFact, Fact, Rule, Metafunction, BogusAtom, WeightedRule
from kproblog.evaluation.mappings import BUILTIN_PREDICATES


__author__ = 'francesco'

class GKPrologVisitorLexer(GKPrologVisitor):
    # Visit a parse tree produced by GKPrologParser#Const.
    def visitConst(self, ctx):
        return Constant(str(ctx.getText()))

    # Visit a parse tree produced by GKPrologParser#Int.
    def visitInt(self, ctx):
        return Constant(int(ctx.getText()))

    # Visit a parse tree produced by GKPrologParser#Float.
    def visitFloat(self, ctx):
        return Constant(float(ctx.getText()))


class GKPrologVisitorTerms(GKPrologVisitorLexer):
    # Visit a parse tree produced by GKPrologParser#ConstTerm.
    def visitConstTerm(self, ctx):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GKPrologParser#FuncTerm.
    def visitFuncTerm(self, ctx):
        functor = str(ctx.CONST_ID())
        args = self.visit(ctx.term_list())
        return Term(functor, *args)

    # Visit a parse tree produced by GKPrologParser#TermInList.
    def visitTermInList(self, ctx):
        return (self.visit(ctx.term()),)

    # Visit a parse tree produced by GKPrologParser#TermList.
    def visitTermList(self, ctx):
        return (self.visit(ctx.term()),) + self.visit(ctx.term_list())


class GKPrologVisitorAlgebraicWeight(GKPrologVisitorTerms):
    # Visit a parse tree produced by GKPrologParser#algebraic_weight.
    def visitAlgebraic_weight(self, ctx):
        acc = self.visit(ctx.multiplyingExpression(0))
        i = 1
        while ctx.multiplyingExpression(i) is not None:
            acc = Term('+', acc, self.visit(ctx.multiplyingExpression(i)))
            i += 1
        return acc

    # Visit a parse tree produced by GKPrologParser#multiplyingExpression.
    def visitMultiplyingExpression(self, ctx):
        acc = self.visit(ctx.powExpression(0))
        i = 1
        while ctx.powExpression(i) is not None:
            acc =  Term('*', acc, self.visit(ctx.powExpression(i)))
            i += 1
        return acc

    # Visit a parse tree produced by GKPrologParser#powExpression_term.
    def visitPowExpression_term(self, ctx):
        base = self.visit(ctx.term(0))
        if ctx.term(1) is None:
            return base
        else:
            exp = self.visit(ctx.term(1))
            return Term('^', base, exp)

    # Visit a parse tree produced by GKPrologParser#powExpression_metatunction.
    def visitPowExpression_metafunction(self, ctx):
        function = self.visit(ctx.constant())
        args = tuple(self.visit(arg) for arg in ctx.algebraic_weight())
        return Metafunction(function, args)


class GKPrologVisitorAtoms(GKPrologVisitorAlgebraicWeight):
    def __init__(self):
        self.pred2semiring = {}
        self.bogus_atom_manager = BogusAtomManager(self.pred2semiring)

    def Atom(self, *args, **kwargs):
        atom = Atom(*args, **kwargs)
        if atom.predicate not in self.pred2semiring and atom.predicate not in BUILTIN_PREDICATES:
            warnings.warn("undeclared {}".format(str(atom.predicate)))
        return atom

    def create_bogus_atom(self, predicate):
        return self.bogus_atom_manager.create_bogus_atom(predicate)

    # Visit a parse tree produced by GKPrologParser#AtomZero.
    def visitAtomZero(self, ctx):
        functor = self.visit(ctx.constant())
        args = ()
        arity = 0
        predicate = Predicate(functor, arity)
        return self.Atom(predicate, *args)

    # Visit a parse tree produced by GKPrologParser#AtomNonZero.
    def visitAtomNonZero(self, ctx):
        functor = self.visit(ctx.constant())
        args = self.visit(ctx.term_list())
        arity = len(args)
        predicate = Predicate(functor, arity)
        return self.Atom(predicate, *args)

    # Visit a parse tree produced by GKPrologParser#AtomInList.
    def visitAtomInList(self, ctx):
        return (self.visit(ctx.atom()),)

    # Visit a parse tree produced by GKPrologParser#AtomList.
    def visitAtomList(self, ctx):
        return (self.visit(ctx.atom()),) + self.visit(ctx.atom_list())

    # Visit a parse tree produced by GKPrologParser#SimpleBodyAtom.
    def visitSimpleBodyAtom(self, ctx):
        return self.visit(ctx.atom())

    # Visit a parse tree produced by GKPrologParser#DecoratedBodyAtom.
    def visitDecoratedBodyAtom(self, ctx):
        metafunction_name = self.visit(ctx.constant())
        metafunction_args = self.visit(ctx.body_atom_list())
        return Metafunction(metafunction_name, metafunction_args)

    # Visit a parse tree produced by GKPrologParser#BodyAtomInList.
    def visitBodyAtomInList(self, ctx):
        return (self.visit(ctx.body_atom()),)

    # Visit a parse tree produced by GKPrologParser#BodyAtomList.
    def visitBodyAtomList(self, ctx):
        return (self.visit(ctx.body_atom()),) + self.visit(ctx.body_atom_list())


class GKPrologVisitorPredicateDeclarations(GKPrologVisitorAtoms):
    def __init__(self, semiring_const2semiring_obj):
        GKPrologVisitorAtoms.__init__(self)
        self.pred2update_type = {}
        self.weight_manager = WeightManager(self.pred2semiring)
        if not isinstance(semiring_const2semiring_obj, dict):
            raise TypeError
        for semiring_const, semiring_obj in semiring_const2semiring_obj.iteritems():
            if not isinstance(semiring_obj, Semiring):
                raise ValueError, "wrong object type for the semiring {} --> {}".format(semiring_const,  str(type(semiring_obj)))
        self.semiring_const2semiring_obj = semiring_const2semiring_obj

    def resolve_semiring(self, semiring_const):
        return self.semiring_const2semiring_obj[str(semiring_const)]


    def register_weighted_fact(self, weighted_fact):
        if not isinstance(weighted_fact, WeightedFact):
            raise TypeError
        self.weight_manager.set_weight(weighted_fact.atom, weighted_fact.weight)

    def transform_weighted_rule(self, weighted_rule):
        if not isinstance(weighted_rule, WeightedRule):
            raise TypeError
        head_predicate = weighted_rule.head.predicate
        bogus_atom = self.create_bogus_atom(head_predicate)
        bogus_weighted_fact = WeightedFact(weighted_rule.weight, bogus_atom)
        self.register_weighted_fact(bogus_weighted_fact)
        new_body = (bogus_atom,) + weighted_rule.body
        head = weighted_rule.head
        return Rule(head, new_body)

    # Visit a parse tree produced by GKPrologParser#Rule.
    def visitRule(self, ctx):
        head = self.visit(ctx.atom())
        body = self.visit(ctx.body_atom_list())
        return Rule(head, body)

    # Visit a parse tree produced by GKPrologParser#WeightedRule.
    def visitWeightedRule(self, ctx):
        head_term = self.visit(ctx.atom())
        body = self.visit(ctx.body_atom_list())
        weight_term = self.visit(ctx.algebraic_weight())
        head, weight = self.pred2semiring[head_term.predicate].parse(head_term, weight_term) # XXX SEMIRING PARSED RULE
        res = WeightedRule(weight, head, body)
        res = self.transform_weighted_rule(res)
        return res

    # Visit a parse tree produced by GKPrologParser#Fact.
    def visitFact(self, ctx):
        atom = self.visit(ctx.atom())
        weight = self.pred2semiring[atom.predicate].one()
        res = WeightedFact(weight, atom)
        self.register_weighted_fact(res)
        return Fact(atom)

    # Visit a parse tree produced by GKPrologParser#WeightedFact.
    def visitWeightedFact(self, ctx):
        atom_term = self.visit(ctx.atom())
        weight_term = self.visit(ctx.algebraic_weight())
        atom, weight = self.pred2semiring[atom_term.predicate].parse(atom_term, weight_term)
        res = WeightedFact(weight, atom)
        self.register_weighted_fact(res)
        return Fact(atom)

    def registerTypeDeclaration(self, ctx):
        pred_name = self.visit(ctx.predicate_name())
        pred_arity = int(ctx.INT_ID().getText())
        semiring_type = self.visit(ctx.semiring_type())
        semiring_type = str(semiring_type) # TODO remove make a symbolic version
        pred = Predicate(pred_name, pred_arity)
        if pred in self.pred2semiring:
            raise ValueError, "predicate {} was already declared".format(str(pred))
        self.pred2semiring[pred] = self.resolve_semiring(semiring_type)
        return pred

    # Visit a parse tree produced by GKPrologParser#Declaration.
    def visitDeclaration(self, ctx):
        self.registerTypeDeclaration(ctx)
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GKPrologParser#DeclarationCycle.
    def visitDeclarationCycle(self, ctx):
        pred = self.registerTypeDeclaration(ctx)
        update_type = ctx.UPDATE_TYPE().getText()
        if pred in self.pred2update_type:
            raise ValueError, "the updated type for predicate {} was already declared".format(str(pred))
        self.pred2update_type[pred] = update_type
        return self.visitChildren(ctx)


class GKPrologVisitorQueries(GKPrologVisitorPredicateDeclarations):
    def __init__(self, semiring_const2semiring_obj):
        GKPrologVisitorPredicateDeclarations.__init__(self, semiring_const2semiring_obj)
        self.query_atoms_nested_list = []

    # Visit a parse tree produced by GKPrologParser#QueryOneAtom.
    def visitQueryAtoms(self, ctx):
        atom_list = self.visit(ctx.atom_list())
        self.query_atoms_nested_list.append(atom_list)
        return self.visitChildren(ctx)


class GKPrologEvaluationVisitor(GKPrologVisitorQueries):
    def __init__(self, semiring_const2semiring_obj):
        GKPrologVisitorQueries.__init__(self, semiring_const2semiring_obj)

    # Visit a parse tree produced by GKPrologParser#program0.
    def visitProgram0(self, ctx):
        return [self.visit(clause) for clause in ctx.clause()]

    # Visit a parse tree produced by GKPrologParser#program.
    def visitProgram(self, ctx):
        return self.visitChildren(ctx)
