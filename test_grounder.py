from kproblog.grounder import KPrologGrounder
from kproblog.grounder import clause2str
from problog.logic import *

import sys

__author__ = 'francesco'

TEST_PROGRAM = """
:- declare(a/1, poly).
:- declare(b/2, poly).
:- declare(c/2, poly).
:- declare(d/1, poly).
:- declare(z/0, poly).
:- declare(k/0, poly, additive).
:- declare(q/2, poly).

label0::a(pluto).
b(pluto, topolino).
c(pluto, minnie).
c(topolino, paperino).
label1::d(X):- c(_, X).
z.
k.
3*label2(X)::q(X,Z) :-
    @f(a(X),b(X,Y)),
    z,
    c(Y,Z),
    @g(d(Z)).

query(q(_,_)).
"""

def main(filename=None):
    if filename is None:
        data = TEST_PROGRAM
    else:
        data = None
    grounder = KPrologGrounder(filename, data)
    declarations, res, query_atoms = grounder.run()
    for declaration in declarations:
        print declaration
    for elem in res:
        print clause2str(elem)

if __name__ == '__main__':
    # main(*sys.argv[1:])
    main('examples/paper/problog.kpl')
