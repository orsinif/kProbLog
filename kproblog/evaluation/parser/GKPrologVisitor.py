# Generated from /Users/francesco/Documents/problog/kprolog/GKProlog.g4 by ANTLR 4.5.1
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by GKPrologParser.

class GKPrologVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by GKPrologParser#Const.
    def visitConst(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#Int.
    def visitInt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#Float.
    def visitFloat(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#ConstTerm.
    def visitConstTerm(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#FuncTerm.
    def visitFuncTerm(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#TermInList.
    def visitTermInList(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#TermList.
    def visitTermList(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#algebraic_weight.
    def visitAlgebraic_weight(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#multiplyingExpression.
    def visitMultiplyingExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#powExpression_term.
    def visitPowExpression_term(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#powExpression_metafunction.
    def visitPowExpression_metafunction(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#AtomZero.
    def visitAtomZero(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#AtomNonZero.
    def visitAtomNonZero(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#AtomInList.
    def visitAtomInList(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#AtomList.
    def visitAtomList(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#SimpleBodyAtom.
    def visitSimpleBodyAtom(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#DecoratedBodyAtom.
    def visitDecoratedBodyAtom(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#BodyAtomInList.
    def visitBodyAtomInList(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#BodyAtomList.
    def visitBodyAtomList(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#semiring_type.
    def visitSemiring_type(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#Rule.
    def visitRule(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#Fact.
    def visitFact(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#WeightedRule.
    def visitWeightedRule(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#WeightedFact.
    def visitWeightedFact(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#Declaration.
    def visitDeclaration(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#DeclarationCycle.
    def visitDeclarationCycle(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#QueryAtoms.
    def visitQueryAtoms(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#predicate_name.
    def visitPredicate_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#program0.
    def visitProgram0(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GKPrologParser#program.
    def visitProgram(self, ctx):
        return self.visitChildren(ctx)


