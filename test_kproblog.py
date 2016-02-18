import glob
from kproblog.kProlog_run import kproblog_run
__author__ = 'francesco'

if __name__ == '__main__':
    show_grounding = True
    only_relevant = True
    for kpl_file_name in glob.iglob('examples/debug/*.kpl'):
        print 'kpl_file_name', kpl_file_name
        kproblog_run(filename=kpl_file_name, data=None, show_grounding=show_grounding, only_relevant=only_relevant)
        print "\n" * 5
