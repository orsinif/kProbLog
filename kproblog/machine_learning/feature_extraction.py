from kproblog.kProlog_run import kproblog_run

class FeatureExtractor(object):
    def __init__(self, code_str, escape_string, verbose_flag=False, show_grounding=False):
        self.code_str = code_str
        self.escape_string = escape_string
        self.verbose_flag = verbose_flag
        self.show_grounding = show_grounding

    def extract(self, data_predicates):
        data = '\n'.join(data_predicates)
        data_dict = {self.escape_string: data}
        code = self.code_str.format(**data_dict)
        if self.verbose_flag:
            print "=" * 80
            print "CODE"
            print "=" * 80
            for line_number, line in enumerate(code.split('\n'), 1):
                print "{}:{}".format(line_number, line)
            print "=" * 80
        return kproblog_run(filename=None, data=code, show_grounding=self.show_grounding, only_relevant=False)
