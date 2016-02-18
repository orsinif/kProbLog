from kproblog.evaluation.evaluation import GKProbLog
from kproblog.evaluation.mappings import TYPENAME_TO_SEMIRING
from kproblog.evaluation.mappings import METAFUNCTION_TO_FUNCTION
import traceback

def main():
    import glob
    problems = []
    for file_name in glob.iglob('examples/debug_ground/example*.gkpl'):
        print '=' * 80
        print "file_name", file_name
        print '=' * 80
        try:
            with open(file_name) as f:
                for line in f:
                    print line,
            print
            print '=' * 80
            query_atoms = None
            gkproblog = GKProbLog(
                TYPENAME_TO_SEMIRING,
                METAFUNCTION_TO_FUNCTION,
                query_atoms,
                file_name=file_name
            )
            gkproblog.run()
            print
            print
            print
        except:
            traceback.print_exc()
            problems.append(file_name)

    print "problems", problems

if __name__ == '__main__':
    main()
