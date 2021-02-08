"""Calculates the number of complete extensions given an argumentation framework"""

import logging, os

from dpdb.problem import Problem, args
from dpdb.reader import TgfReader, ApxReader
from dpdb.problem import var2col, var2tab_col, var2tab_alias, node2tab_alias
from dpdb.parser_test import TestCEReader


logger = logging.getLogger(__name__)

PROBLEM_NAME = 'problem_cecomplete'

# Encoding
# v_var SMALLINT| p_var BOOLEAN |    MEANING
# ----------------------------------------------
#       0       |       1       |    Invalid
#       0       |       0       |    IN
#       1       |       1       |    DEF
#       1       |       0       |    DEFP
#       2       |       1       |    OUT
#       2       |       0       |    OUTP 


def var2col_proved(var):
    """Returns the name of the column indicating whether variable (argument) var is proved/not.

    :param var: Id of variable (argument)
    :return: Column name
    """
    return f"p{var}"    

class CEComplete(Problem):
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
        return "SELECT 0 val UNION ALL SELECT 1 UNION ALL SELECT 2"

    def td_node_column_def(self, var):
        """Returns name and datatype of the column for a variable (argument) var.

        :param var: Id of variable (argument)
        :return: Tuple (name of the column, datatype)
        """
        return var2col(var), "SMALLINT"

    def td_node_extra_columns(self, node):
        """Returns names and datatypes of additional columns column for a node of a tree decomposition.
        Here, it returns an additional column of type BOOLEAN for every variable in the bag
        and a column for counting the extensions.

        :param node: Node of the tree decomposition.
        :return: List of extra columns for a node in a tree decomposition.
        """
        return [(var2col_proved(v), "BOOLEAN") for v in node.vertices] + [("model_count", "NUMERIC")]

    def assignment_extra_cols(self, node):
        """Returns additional columns that should appear in the topmost SELECT clause.
        Here, returns the 'proved' columns, as well as the model_count column.
        Returns null::BOOLEAN for variables that will be forgotten in the parent node.

        :param node: Node of the tree decomposition.
        :return: Additional columns for the topmost SELECT clause.
        """
        return [var2col_proved(v) if v in node.stored_vertices
                else f"null::BOOLEAN " + var2col_proved(v) for v in node.vertices] \
            + ["sum(model_count) AS model_count"]

    def group_extra_cols(self, node):
        """Returns additional columns that should be added to the GROUP BY clause.

        :param node: Node of the tree decomposition.
        :return: Additional columns to appear in the GROUP BY clause.
        """
        return [var2col_proved(v) for v in node.stored_vertices]

    def candidate_extra_cols(self, node):
        """Returns additional values to be selected as candidates.
        Here, calculates the value for the 'proved' column (see var2proved method) as well as the value for counter.

        :param node: Node of the tree decomposition.
        :return: Additional values to be selected as candidates.
        """
        defeats = [self.var2proved(node, v) + " AS " + var2col_proved(v) for v in node.vertices]

        count = ["{} AS model_count".format(
                " * ".join(set([var2cnt(node, v) for v in node.vertices] +
                               [node2cnt(n) for n in node.children])) if node.vertices or node.children else "1"
                )]
        return defeats + count

    def filter(self, node):
        """Creates the WHERE statement.

        :param node: Node of the tree decomposition.
        :return: WHERE statement
        """
        # if vertex v not in stored_vertices (which means it will be forgotten in the parent) 
        # OR node is root (which means no other attack will appear), then it must either be labeled IN or proved to be DEF or OUT
        forgotten_next_condition = [f'{var2col(v)} = 0 OR {var2col_proved(v)}' 
                                    for v in node.vertices if v not in node.stored_vertices or node.is_root()]

        # if vertex v is attacked by something in IN, it must be DEF(p)
        must_be_defeated = [f'NOT ({var2col(v)} = 0 AND {var2col(w)} = 2)' for (v, w) in self.subframework_edges(node)]

        # if vertex v is in IN and attacked by something, the attacker must be DEF
        admissible_condition = [f'NOT ({var2col(v)} = 2 AND {var2col(w)} = 0)' for (v, w) in self.subframework_edges(node)]

        # no two vertices can be labeled in if there's an edge between them
        conflict_free_condition = [f'NOT ({var2col(v)} = 0 AND {var2col(w)} = 0)' for v, w in self.subframework_edges(node)]
            
        return "WHERE ({})".format(") AND (".join(forgotten_next_condition + conflict_free_condition + admissible_condition + must_be_defeated)) \
            if forgotten_next_condition + conflict_free_condition + admissible_condition + must_be_defeated else ''

    def subframework_edges(self, node):
        """Returns edges of 'node' subframework, i.e. only those that vertices of appear in the node's bag.

        :param node: Node of the tree decomposition.
        :return: Edges of the node subframework.
        """
        return filter(lambda edge: edge[0] in node.vertices and edge[1] in node.vertices, self.edges)

    def var2proved(self, node, var):
        # list of all attackers of 'var' within 'node' that is labeled in
        conditionsd = [var2tab_col(node, v, False) + " = 0" for (v, w) in self.subframework_edges(node) if w == var]

        # list of all attackers of 'var' within 'node' that is labeled out
        conditionso = [var2tab_col(node, v, False) + " = 2" for (v, w) in self.subframework_edges(node) if w == var]

        if not node.needs_introduce(var):
            # if var is not introduced (has appeared before in some child), check if it hasn't already been proved
            conditionsd += ["{}.{}".format(node2tab_alias(child_node), var2col_proved(var)) for child_node in node.vertex_children(var)]
            conditionso += ["{}.{}".format(node2tab_alias(child_node), var2col_proved(var)) for child_node in node.vertex_children(var)]

        # var is in proved as def when it is in def and one of its attackers labeled in
        # var is in proved as out when it is in out and one of its attackers labeled out
        # otherwise, is not proved (FALSE)
        q = '(' 
        q += ('('+var2tab_col(node, var, False) + " = 1 AND (" + ' OR '.join(conditionsd) + '))') if conditionsd else 'FALSE' 
        q += ' OR '
        q += ('('+var2tab_col(node, var, False) + " = 2 AND (" + ' OR '.join(conditionso) + ')))') if conditionso else 'FALSE)'   
        return q

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
        logger.info("Problem has %d complete extensions", model_count)

    def call_aspartix(self, fname):
        if fname.endswith(".apx"):
            print(fname)
            os.system(f"clingo --quiet=3 {fname} aspartix/complete.lp 0")

def var2cnt(node, var):
    if node.needs_introduce(var):
        return "1"
    else:
        return "{}.model_count".format(var2tab_alias(node, var))


def node2cnt(node):
    return "{}.model_count".format(node2tab_alias(node))


args.specific[CEComplete] = dict(
    help="Give the number of the complete extensions of a given file",
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
