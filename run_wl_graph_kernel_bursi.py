from itertools import islice
from kproblog.machine_learning.io import parse_gspan
from kproblog.machine_learning.feature_extraction import FeatureExtractor

kpl_file = open("./examples/paper/wl_graph_kernel_escape.kpl")
gspan_file_name = "./data/bursi/bursi.gspan"

code_str = "".join(list(kpl_file))
escape_string = 'graph_data'
feature_extractor = FeatureExtractor(code_str, escape_string, verbose_flag=False, show_grounding=False)
LIMIT_EXAMPLES = 2
VERTEX_PREDICATE_PTRN = "1.0 * x('{lbl}')::vertex({v})."
EDGE_PREDICATE_PTRN = "edge_asymm({v}, {w})."

for graph_i, graph in enumerate(islice(parse_gspan(gspan_file_name, VERTEX_PREDICATE_PTRN, EDGE_PREDICATE_PTRN), LIMIT_EXAMPLES)):
    print graph_i, ')'
    # print graph
    for weight, atom in feature_extractor.extract(graph):
        if atom.startswith('sv_feature'):
            print weight, atom
print