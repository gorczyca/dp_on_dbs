"""Calculates the number of admissible  sets given an argumentation framework"""

import logging

from dpdb.problem import Problem, args
from dpdb.reader import TgfReader, ApxReader
from dpdb.problem import var2col, var2tab_col, var2tab_alias, node2tab_alias
from dpdb.parser_test import TestCEReader


logger = logging.getLogger(__name__)

PROBLEM_NAME = 'problem_ceadmissible'
EXTRA_COL_DATATYPE = 'BOOLEAN'


def var2extra_col(var):
    """Returns the name of an additional column for a variable var.

    :param var: Id of variable (argument)
    :return: Column name
    """
    return f"w{var}"


# Based on paper:
# "Towards fixed-parameter tractable algorithms for abstract argumentation"
#   by Wolfgang Dvořák, Reinhard Pichler, Stefan Woltran

# Encoding
# v{var} BOOLEAN | w{var} BOOLEAN  |    MEANING
# ----------------------------------------------
#       0        |       null      |    OUT
#       0        |       0         |    ATT
#       0        |       1         |    DEF
#       1        |       -         |    IN


class CEAdmissible2(Problem):
    def __init__(self, fname, pool, input_format, unit_test, *args, **kwargs):
        Problem.__init__(self, fname, pool, *args, **kwargs)

        self.input_format = input_format
        self.edges = None
        self.num_vertices = None
        if unit_test == "parser":
            tester = TestCEReader()
            tester.perform_testing(self.input_format)

    def prepare_input(self, fname):
        input_ = None
        if self.input_format == "apx":
            input_ = ApxReader.from_file(fname)
        elif self.input_format == "tgf":
            input_ = TgfReader.from_file(fname)

        # self.adjacency_list = input.adjacency_list
        self.edges = input_.edges
        self.num_vertices = input_.num_vertices

        return input_.num_vertices, input_.edges

    def introduce(self,node):
        return "SELECT false val UNION ALL SELECT true"

    def td_node_column_def(self, var):
        """Returns name and datatype of the column for a variable (argument) var.

        :param var: Id of variable (argument)
        :return: Tuple (name of the column, datatype)
        """
        return var2col(var), "BOOLEAN"

    def td_node_extra_columns(self, node):
        """Returns names and datatypes of additional columns column for a node of a tree decomposition.
        Here, it returns an additional column of type BOOLEAN for every variable in the bag
        and a column for counting the extensions.

        :param node: Node of the tree decomposition.
        :return: List of extra columns for a node in a tree decomposition.
        """
        return [(var2extra_col(v), EXTRA_COL_DATATYPE) for v in node.vertices] + [("model_count", "NUMERIC")]

    def assignment_extra_cols(self, node):
        """Returns additional columns that should appear in the topmost SELECT clause.
        Here, returns the extra variable columns, as well as the model_count column.
        Returns null::BOOLEAN for variables that will be forgotten in the parent node.

        :param node: Node of the tree decomposition.
        :return: Additional columns for the topmost SELECT clause.
        """
        return [var2extra_col(v) if v in node.stored_vertices
                else f"null::{EXTRA_COL_DATATYPE} " + var2extra_col(v) for v in node.vertices] \
            + ["sum(model_count) AS model_count"]

    def group_extra_cols(self, node):
        """Returns additional columns that should be added to the GROUP BY clause.

        :param node: Node of the tree decomposition.
        :return: Additional columns to appear in the GROUP BY clause.
        """
        return [var2extra_col(v) for v in node.stored_vertices]

    def candidate_extra_cols(self, node):
        """Returns additional values to be selected as candidates.
        Here, calculates the value for the extra column (see var2extra method) as well as the value for counter.

        :param node: Node of the tree decomposition.
        :return: Additional values to be selected as candidates.
        """
        extra_values = [self.var2extra(node, v) + " AS " + var2extra_col(v) for v in node.vertices]

        count = ["{} AS model_count".format(
                " * ".join(set([var2cnt(node, v) for v in node.vertices] +
                               [node2cnt(n) for n in node.children])) if node.vertices or node.children else "1"
                )]

        return extra_values + count

    def filter(self, node):
        """Creates the WHERE statement.

        :param node: Node of the tree decomposition.
        :return: WHERE statement
        """
        # if vertex v not in stored_vertices (which means it will be forgotten in the parent)
        # OR node is root (which means no other attack will appear), then it must not be labelled ATT

        # alternatively:
        #forgotten_next_condition = [f'({var2extra_col(v)} OR ({var2extra_col(v)} IS null))'
        # Rule out false, preserve null (OUT) and true (DEF)
        forgotten_next_condition = [f'{var2extra_col(v)} IS NOT false'
                                    for v in node.vertices if v not in node.stored_vertices or node.is_root()]

        # no two vertices can be labeled IN if there's an edge between them
        conflict_free_condition = [f'NOT ({var2col(v)} AND {var2col(w)})' for v, w in self.subframework_edges(node)]

        return "WHERE ({})".format(") AND (".join(forgotten_next_condition + conflict_free_condition)) \
            if forgotten_next_condition + conflict_free_condition else ''

    def subframework_edges(self, node):
        """Returns edges of 'node' subframework, i.e. only those that vertices of appear in the node's bag.

        :param node: Node of the tree decomposition.
        :return: Edges of the node subframework.
        """
        return filter(lambda edge: edge[0] in node.vertices and edge[1] in node.vertices, self.edges)

    def var2extra(self, node, var):
        """Specifies a value to be selected for the extra (w) column of variable (argument) var.

        :param node: Node of the tree decomposition var is in.
        :param var: Id of variable (argument)
        :return: Value for the 'extra' column.
        """

        # list of all attackers  of 'var' within 'node' (as table columns)
        attacking_var = [var2tab_col(node, v, False) for (v, w) in self.subframework_edges(node) if w == var]
        # list of all arguments attacked by  'var' within 'node' (as table columns)
        attacked_by_var = [var2tab_col(node, w, False) for (v, w) in self.subframework_edges(node) if v == var]

        # if any of attackers of var is labelled IN, then var has to be labelled DEF
        def_conditions = [v for v in attacking_var]

        att_conditions_att_already = []
        if not node.needs_introduce(var):
            # if var is not introduced (has appeared before in some child), check if it hasn't already been
            # labelled DEF
            def_conditions += ["({}.{})".format(node2tab_alias(child_node), var2extra_col(var))
                               for child_node in node.vertex_children(var)]
            # if var has been labelled ATT before (in some child) then var has to be labelled ATT
            # (unless it is defeated in the current node)
            att_conditions_att_already = ["(NOT {}.{})".format(node2tab_alias(child_node), var2extra_col(var))
                                          for child_node in node.vertex_children(var)]

        # var must be remain as ATT if no attacker of var is labelled IN
        att_conditions_not_defeated = [f'NOT {v}' for v in attacking_var]

        return f'CASE ' \
               f'WHEN {" OR ".join(def_conditions) if def_conditions else "FALSE"} THEN true ' \
               f'WHEN ({" OR ".join(attacked_by_var) if attacked_by_var else "FALSE"}) ' \
                    f'AND ({" AND ".join(att_conditions_not_defeated) if att_conditions_not_defeated else "TRUE"}) ' \
                    f'OR ({" OR ".join(att_conditions_att_already) if att_conditions_att_already else "FALSE"}) THEN false ' \
               f'ELSE null::{EXTRA_COL_DATATYPE} '\
               f'END'

    # TODO: Temporary:
    # every method / function below is copied from sharpsat.py.
    # it will probably be better if in the future it's abstracted out to some abstract class
    # (like Countable in viktorbesin's repo) or a sharp_util file etc.

    def setup_extra(self):
        def create_tables():
            self.db.ignore_next_praefix()
            self.db.create_table(PROBLEM_NAME, [
                ("id", "INTEGER NOT NULL PRIMARY KEY REFERENCES PROBLEM(id)"),
                ("num_vars", "INTEGER NOT NULL"),
                ("num_edges", "INTEGER NOT NULL"),
                ("model_count", "NUMERIC")
            ])

        def insert_data():
            self.db.ignore_next_praefix()
            self.db.insert(PROBLEM_NAME, ("id", "num_vars", "num_edges"),
                           (self.id, self.num_vertices, len(self.edges)))
            
            # TODO: instead of storing formula, store framework maybe?
            # if "faster" not in self.kwargs or not self.kwargs["faster"]:
            #    self.db.ignore_next_praefix()
            #    self.db.insert("problem_option", ("id", "name", "value"), (self.id,"store_formula",self.store_formula))
            #    if self.store_formula:
            #        store_clause_table(self.db, self.clauses)

        create_tables()
        insert_data()

    def after_solve(self):
        root_tab = f"td_node_{self.td.root.id}"
        sum_count = self.db.replace_dynamic_tabs(f"(select coalesce(sum(model_count),0) from {root_tab})")
        self.db.ignore_next_praefix()
        model_count = self.db.update(PROBLEM_NAME, ["model_count"], [sum_count], [f"ID = {self.id}"], "model_count")[0]
        logger.info("Problem has %d admissible sets", model_count)

def var2cnt(node, var):
    if node.needs_introduce(var):
        return "1"
    else:
        return "{}.model_count".format(var2tab_alias(node, var))


def node2cnt(node):
    return "{}.model_count".format(node2tab_alias(node))


args.specific[CEAdmissible2] = dict(
    help="Give the number of the admissible sets of a given file",
    options={
        "--input-format": dict(
            dest="input_format",
            help="Input format",
            choices=["apx","tgf"],
            default="apx"
        ),
        "--unit-test": dict(
            dest="unit_test",
            help="Unit Test",
            choices=["parser","none"],
            default="none"
        )
    }
)
