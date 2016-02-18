import glob
from .grounder import KPrologGrounder
from .grounder import clause2str
from .evaluation.evaluation import GKProbLog
from .evaluation.mappings import TYPENAME_TO_SEMIRING
from .evaluation.mappings import METAFUNCTION_TO_FUNCTION

__author__ = 'francesco'

def kproblog_run(filename=None, data=None, show_grounding=True, only_relevant=True):
    assert (filename is None and data is not None) or (filename is not None and data is None)
    grounder = KPrologGrounder(filename, data)
    declarations, res, query_atoms = grounder.run()
    if not only_relevant:
        query_atoms = None

    ground_program = '\n'.join(list(declarations) + map(clause2str, res))
    if show_grounding:
        print '=' * 80
        print "GROUNDING"
        print '=' * 80
        print ground_program
        print '=' * 80
    gkproblog = GKProbLog(
        typename_to_semiring=TYPENAME_TO_SEMIRING,
        metafunction_to_function=METAFUNCTION_TO_FUNCTION,
        query_atoms=query_atoms,
        code=ground_program
    )
    return gkproblog.run()


def main():
    show_grounding = False
    only_relevant = True
    for kpl_file_name in glob.iglob('examples/paper/*.kpl'):
        print 'kpl_file_name:', kpl_file_name
        res = kproblog_run(
            filename=kpl_file_name,
            data=None,
            show_grounding=show_grounding,
            only_relevant=only_relevant
        )
        for w, a in res:
            print "{}::{}".format(w, a)
        print
        print

if __name__ == '__main__':
    main()
