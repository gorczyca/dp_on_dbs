from dpdb.problem import Problem, args
from dpdb.reader import TgfReader, ApxReader


class CEStable(Problem):
    def __init__(self, fname, pool, input_format, *args, **kwargs):
        Problem.__init__(self, fname, pool, *args, **kwargs)
        self.input_format = input_format


    def prepare_input(self, fname):
        # TODO: why passing file_name again?
        input = None
        if self.input_format == "apx":
            input = ApxReader.from_file(fname)
        elif self.input_format == "tgf":
            input = TgfReader.from_file(fname)

        return (input.num_vertices, input.edges)


args.specific[CEStable] = dict(
    help="Give the number of the stable extensions of a given file",
    options={
        "--input-format": dict(
            dest="input_format",
            help="Input format",
            choices=["apx","tgf"],
            default="apx"
        )
    }
)
