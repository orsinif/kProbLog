def parse_gspan(gspan_file_name, vertex_predicate_ptrn, edge_predicate_ptrn):
    with open(gspan_file_name) as gspan_file:
        current_graph = None
        for line in gspan_file:
            line = line.strip()
            ch = line[0]
            if ch == 't':
                if current_graph is not None:
                    yield current_graph
                current_graph = []
            elif ch == 'v':
                _, vid, vlabel = line.split()[:3]
                current_graph.append(vertex_predicate_ptrn.format(v=vid, lbl=vlabel))
            elif ch == 'e':
                _, vid, wid, elabel = line.split()[:4]
                current_graph.append(edge_predicate_ptrn.format(v=vid, w=wid, lbl=elabel))
            else:
                raise ValueError, line
        if current_graph is not None:
            yield current_graph

def parse_target(target_file_name):
    with open(target_file_name) as target_file:
        for line in target_file:
            yield int(line.strip())