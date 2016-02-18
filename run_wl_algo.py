from kproblog.kProlog_run import kproblog_run

__author__ = 'francesco'

if __name__ == '__main__':
    SHOW_GROUNDING = False
    ONLY_RELEVANT = True
    kpl_file_name = 'examples/paper/wl_graph_algo.kpl'
    print 'kpl_file_name', kpl_file_name
    res = kproblog_run(filename=kpl_file_name, data=None, show_grounding=SHOW_GROUNDING, only_relevant=ONLY_RELEVANT)
    for w, atom in res:
        print "{}::{}".format(w, atom)