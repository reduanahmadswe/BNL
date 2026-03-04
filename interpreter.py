import re
import shlex
import sys
from dataclasses import dataclass
from typing import Any, Optional


# -----------------------------
# Banglish language keywords
# -----------------------------
# variable creation -> dorlam
# print            -> dekhao
# while loop       -> guraw
# end block        -> shesh
# math words       -> jog, biyog, gun, vag

KEY_DORLAM = "dorlam"
KEY_DEKHAO = "dekhao"
KEY_GURAW = "guraw"
KEY_SHESH = "shesh"

BANG_OP_TO_SYMBOL = {
    "jog": "+",
    "biyog": "-",
    "gun": "*",
    "vag": "/",
}


class ParseError(Exception):
    pass


class RuntimeErrorBnl(Exception):
    pass


# -----------------------------
# Expression tokenizer / parser
# -----------------------------

EXPR_TOKEN_REGEX = re.compile(
    r'''\s*(?:
        (?P<NUMBER>\d+(?:\.\d+)?)
      | (?P<STRING>"[^"\\]*(?:\\.[^"\\]*)*"|'[^'\\]*(?:\\.[^'\\]*)*')
      | (?P<OP>==|!=|<=|>=|\+|-|\*|/|<|>|\(|\))
      | (?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)
    )''',
    re.VERBOSE,
)


@dataclass
class Token:
    kind: str
    value: str


@dataclass
class ExprNode:
    kind: str
    value: Any = None
    left: Optional["ExprNode"] = None
    right: Optional["ExprNode"] = None


class ExprParser:
    def __init__(self, text: str):
        self.tokens = self._tokenize(text)
        self.pos = 0

    def _tokenize(self, text: str) -> list[Token]:
        tokens: list[Token] = []
        index = 0

        while index < len(text):
            match = EXPR_TOKEN_REGEX.match(text, index)
            if not match:
                raise ParseError(f"Invalid expression near: {text[index:]}")

            index = match.end()
            kind = match.lastgroup
            value = match.group(kind)

            if kind == "IDENT" and value in BANG_OP_TO_SYMBOL:
                tokens.append(Token("OP", BANG_OP_TO_SYMBOL[value]))
            else:
                tokens.append(Token(kind, value))

        return tokens

    def _current(self) -> Optional[Token]:
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def _eat(self, expected_value: Optional[str] = None, expected_kind: Optional[str] = None) -> Token:
        token = self._current()
        if token is None:
            raise ParseError("Unexpected end of expression")

        if expected_value is not None and token.value != expected_value:
            raise ParseError(f"Expected '{expected_value}', got '{token.value}'")

        if expected_kind is not None and token.kind != expected_kind:
            raise ParseError(f"Expected {expected_kind}, got {token.kind}")

        self.pos += 1
        return token

    def parse(self) -> ExprNode:
        if not self.tokens:
            raise ParseError("Expression cannot be empty")

        node = self._parse_comparison()
        if self._current() is not None:
            raise ParseError(f"Unexpected token: {self._current().value}")

        return node

    def _parse_comparison(self) -> ExprNode:
        node = self._parse_term()
        while self._current() is not None and self._current().value in ("==", "!=", "<", ">", "<=", ">="):
            operator = self._eat().value
            right = self._parse_term()
            node = ExprNode(kind="binary", value=operator, left=node, right=right)
        return node

    def _parse_term(self) -> ExprNode:
        node = self._parse_factor()
        while self._current() is not None and self._current().value in ("+", "-"):
            operator = self._eat().value
            right = self._parse_factor()
            node = ExprNode(kind="binary", value=operator, left=node, right=right)
        return node

    def _parse_factor(self) -> ExprNode:
        node = self._parse_unary()
        while self._current() is not None and self._current().value in ("*", "/"):
            operator = self._eat().value
            right = self._parse_unary()
            node = ExprNode(kind="binary", value=operator, left=node, right=right)
        return node

    def _parse_unary(self) -> ExprNode:
        token = self._current()
        if token is not None and token.value == "-":
            self._eat("-")
            right = self._parse_unary()
            return ExprNode(kind="unary", value="-", right=right)
        return self._parse_primary()

    def _parse_primary(self) -> ExprNode:
        token = self._current()
        if token is None:
            raise ParseError("Unexpected end of expression")

        if token.value == "(":
            self._eat("(")
            node = self._parse_comparison()
            self._eat(")")
            return node

        if token.kind == "NUMBER":
            self._eat(expected_kind="NUMBER")
            if "." in token.value:
                return ExprNode(kind="number", value=float(token.value))
            return ExprNode(kind="number", value=int(token.value))

        if token.kind == "STRING":
            self._eat(expected_kind="STRING")
            text = token.value
            if text[0] == text[-1] and text[0] in ('"', "'"):
                text = bytes(text[1:-1], "utf-8").decode("unicode_escape")
            return ExprNode(kind="string", value=text)

        if token.kind == "IDENT":
            self._eat(expected_kind="IDENT")
            return ExprNode(kind="var", value=token.value)

        raise ParseError(f"Unexpected token: {token.value}")


# -----------------------------
# Statement parser
# -----------------------------


@dataclass
class Statement:
    kind: str
    value: Any = None


class ProgramParser:
    def __init__(self, source: str):
        self.lines = [line.rstrip() for line in source.splitlines()]
        self.pos = 0

    def parse(self) -> list[Statement]:
        return self._parse_block(stop_on_shesh=False)

    def _parse_block(self, stop_on_shesh: bool) -> list[Statement]:
        statements: list[Statement] = []

        while self.pos < len(self.lines):
            raw_line = self.lines[self.pos].strip()
            self.pos += 1

            if not raw_line or raw_line.startswith("#"):
                continue

            pieces = shlex.split(raw_line)
            if not pieces:
                continue

            keyword = pieces[0]

            if keyword == KEY_SHESH:
                if stop_on_shesh:
                    return statements
                raise ParseError("Unexpected 'shesh' at top level")

            if keyword == KEY_DORLAM:
                if len(pieces) < 3:
                    raise ParseError("'dorlam' needs: dorlam <name> <expression>")
                var_name = pieces[1]
                expr_text = raw_line.split(None, 2)[2]
                expr = ExprParser(expr_text).parse()
                statements.append(Statement(kind="set", value=(var_name, expr)))
                continue

            if keyword == KEY_DEKHAO:
                if len(pieces) < 2:
                    raise ParseError("'dekhao' needs an expression")
                expr_text = raw_line.split(None, 1)[1]
                expr = ExprParser(expr_text).parse()
                statements.append(Statement(kind="print", value=expr))
                continue

            if keyword == KEY_GURAW:
                if len(pieces) < 2:
                    raise ParseError("'guraw' needs a condition")
                expr_text = raw_line.split(None, 1)[1]
                condition = ExprParser(expr_text).parse()
                body = self._parse_block(stop_on_shesh=True)
                statements.append(Statement(kind="while", value=(condition, body)))
                continue

            raise ParseError(
                "Unknown keyword: "
                f"{keyword}. Use 'dorlam', 'dekhao', 'guraw', and 'shesh'."
            )

        if stop_on_shesh:
            raise ParseError("Expected 'shesh' before file ended")

        return statements


# -----------------------------
# Runtime / Interpreter
# -----------------------------


class Environment:
    def __init__(self):
        self.variables: dict[str, Any] = {}

    def get_var(self, name: str) -> Any:
        if name not in self.variables:
            raise RuntimeErrorBnl(f"Undefined variable: {name}")
        return self.variables[name]

    def set_var(self, name: str, value: Any) -> None:
        self.variables[name] = value


class Interpreter:
    def __init__(self):
        self.env = Environment()

    def eval_expr(self, node: ExprNode) -> Any:
        if node.kind == "number":
            return node.value

        if node.kind == "string":
            return node.value

        if node.kind == "var":
            return self.env.get_var(node.value)

        if node.kind == "unary":
            value = self.eval_expr(node.right)
            if node.value == "-":
                return -value
            raise RuntimeErrorBnl(f"Unknown unary operator: {node.value}")

        if node.kind == "binary":
            left = self.eval_expr(node.left)
            right = self.eval_expr(node.right)
            operator = node.value

            if operator == "+":
                return left + right
            if operator == "-":
                return left - right
            if operator == "*":
                return left * right
            if operator == "/":
                return left / right
            if operator == "==":
                return left == right
            if operator == "!=":
                return left != right
            if operator == "<":
                return left < right
            if operator == ">":
                return left > right
            if operator == "<=":
                return left <= right
            if operator == ">=":
                return left >= right

            raise RuntimeErrorBnl(f"Unknown operator: {operator}")

        raise RuntimeErrorBnl(f"Unknown expression node: {node.kind}")

    def execute(self, statements: list[Statement]) -> None:
        for statement in statements:
            if statement.kind == "set":
                name, expr = statement.value
                self.env.set_var(name, self.eval_expr(expr))
                continue

            if statement.kind == "print":
                print(self.eval_expr(statement.value))
                continue

            if statement.kind == "while":
                condition, body = statement.value
                while self.eval_expr(condition):
                    self.execute(body)
                continue

            raise RuntimeErrorBnl(f"Unknown statement type: {statement.kind}")


def run_file(path: str) -> None:
    with open(path, "r", encoding="utf-8") as file_handle:
        source = file_handle.read()

    parser = ProgramParser(source)
    program = parser.parse()

    interpreter = Interpreter()
    interpreter.execute(program)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <program.bnl>")
        return

    program_path = sys.argv[1]

    try:
        run_file(program_path)
    except (ParseError, RuntimeErrorBnl) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
