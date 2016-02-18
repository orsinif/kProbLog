# # OLD
# from problog.logic import Clause
#
# class TransformationManager(object):
#     def __init__(self, engine, gp, annotations):
#         self.engine = engine
#
#         clauses = []
#         facts = []
#         for clause in gp.enum_clauses():
#             if isinstance(clause, Clause):
#                 clauses.append(clause)
#             else:
#                 facts.append(clause)
#
#         self.facts = facts
#         self.clauses = self._transform_clauses_wo_nested_metafunctions(clauses, annotations)
#
#     def bogus_clause2metafunction(self, bogus_clause, annotations):
#         metafuntion = annotations[bogus_clause.head.functor]
#         body = bogus_clause.body
#         body = tuple(body.to_list()) if isinstance(body, And) else tuple([body])
#         return Metafunction(metafuntion, *body)
#
#     def _transform_clauses_wo_nested_metafunctions(self, clauses, annotations):
#         true_clauses = []
#         bogus_head_clauses = []
#         for clause in clauses:
#             if isinstance(clause, Clause) and clause.head.functor.startswith("_nocache_"):
#                 bogus_head_clauses.append(clause)
#             else:
#                 true_clauses.append(clause)
#         bogus_head2metafunction = {}
#         for bogus_head_clause in bogus_head_clauses:
#             bogus_head = bogus_head_clause.head
#             metafunction = self.bogus_clause2metafunction(bogus_head_clause, annotations)
#             bogus_head2metafunction[bogus_head] = metafunction
#
#         res = []
#         for clause in true_clauses:
#             head = clause.head
#             body_list = and2list(clause.body)
#             new_body_list = []
#             for atom in body_list:
#                 if atom.functor.startswith("_nocache_"):
#                     b = bogus_head2metafunction[atom]
#                 else:
#                     b = atom
#                 new_body_list.append(b)
#             new_body = list2and(new_body_list)
#             res.append(Clause(head, new_body))
#         return res