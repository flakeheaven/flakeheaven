# built-in
from ast import AST
from tokenize import TokenInfo
from typing import Sequence, TypeVar


try:
    # external
    from pylint.__pkginfo__ import __version__ as version
    from pylint.lint import Run
    from pylint.reporters import BaseReporter
except ImportError:
    version = '0.0.0'
    Run = None
    BaseReporter = type


STDIN = 'stdin'


class Reporter(BaseReporter):
    def _display(self, layout) -> None:
        pass


P = TypeVar('P', bound='PyLintChecker')


class PyLintChecker:
    name = 'pylint'
    version = version
    max_line_length: int

    @classmethod
    def parse_options(cls, options) -> None:
        cls.max_line_length = options.max_line_length

    def __init__(
        self,
        tree: AST,
        file_tokens: Sequence[TokenInfo],
        filename: str = STDIN,
    ) -> None:
        self.tree = tree
        self.filename = filename
        self.file_tokens = file_tokens

    def run(self):
        # pylint is not installed, skip
        if Run is None:
            return

        args = [self.filename, f'--max-line-length={self.max_line_length}']
        reporter = Reporter()
        Run(args, reporter=reporter, exit=False)
        for error in reporter.messages:
            yield (
                error.line,
                error.column,
                f'{error.msg_id} {error.msg or ""} ({error.symbol})',
                type(self),
            )
