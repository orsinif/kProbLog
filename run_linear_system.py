from kproblog.kProlog_run import kproblog_run

SHOW_GROUNDING = True
ONLY_RELEVANT = True

for weight, atom in kproblog_run(
        filename='./examples/paper/linear_system.kpl',
        show_grounding=SHOW_GROUNDING,
        only_relevant=ONLY_RELEVANT
    ):
    print "{}::{}".format(weight, atom)