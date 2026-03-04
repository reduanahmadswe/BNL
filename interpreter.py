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
# input            -> naw
# if               -> jodi
# else             -> nahole
# while loop       -> guraw
# end block        -> shesh
# break            -> bhenge_jao
# continue         -> cholte_thako
# math words       -> jog, biyog, gun, vag
# logic words      -> ar, ba, na
# bool literals    -> shotti, mitha

KEY_DORLAM = "dorlam"
KEY_DEKHAO = "dekhao"
KEY_NAW = "naw"
KEY_JODI = "jodi"
KEY_NAHOLE = "nahole"
KEY_GURAW = "guraw"
KEY_SHESH = "shesh"
KEY_BREAK = "bhenge_jao"
KEY_CONTINUE = "cholte_thako"

BANG_OP_TO_SYMBOL = {
    "jog": "+",
    "biyog": "-",
    "gun": "*",
    "vag": "/",
    "ar": "and",
    "ba": "or",
    "na": "not",
}

BOOL_LITERALS = {
    "shotti": True,
    "mitha": False,
}


class ParseError(Exception):
    pass


class RuntimeErrorBnl(Exception):
    pass


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
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

        node = self._parse_or()
        if self._current() is not None:
            raise ParseError(f"Unexpected token: {self._current().value}")

        return node

    def _parse_or(self) -> ExprNode:
        node = self._parse_and()
        while self._current() is not None and self._current().value == "or":
            operator = self._eat().value
            right = self._parse_and()
            node = ExprNode(kind="binary", value=operator, left=node, right=right)
        return node

    def _parse_and(self) -> ExprNode:
        node = self._parse_not()
        while self._current() is not None and self._current().value == "and":
            operator = self._eat().value
            right = self._parse_not()
            node = ExprNode(kind="binary", value=operator, left=node, right=right)
        return node

    def _parse_not(self) -> ExprNode:
        token = self._current()
        if token is not None and token.value == "not":
            self._eat("not")
            right = self._parse_not()
            return ExprNode(kind="unary", value="not", right=right)
        return self._parse_comparison()

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
            if token.value in BOOL_LITERALS:
                return ExprNode(kind="bool", value=BOOL_LITERALS[token.value])
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

    @staticmethod
    def _split_print_args(expr_text: str) -> list[str]:
        return re.findall(r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'|[^\s]+', expr_text)

    def parse(self) -> list[Statement]:
        statements, stop_keyword = self._parse_block(stop_keywords=set())
        if stop_keyword is not None:
            raise ParseError(f"Unexpected '{stop_keyword}' at top level")
        return statements

    def _error(self, message: str) -> ParseError:
        return ParseError(f"Line {self.pos}: {message}")

    def _parse_block(self, stop_keywords: set[str]) -> tuple[list[Statement], Optional[str]]:
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

            if keyword in stop_keywords:
                return statements, keyword

            if keyword == KEY_SHESH:
                raise self._error("Unexpected 'shesh' at top level")

            if keyword == KEY_NAHOLE:
                raise self._error("Unexpected 'nahole' without matching 'jodi'")

            if keyword == KEY_DORLAM:
                if len(pieces) < 3:
                    raise self._error("'dorlam' needs: dorlam <name> <expression>")
                var_name = pieces[1]
                expr_text = raw_line.split(None, 2)[2]
                expr = ExprParser(expr_text).parse()
                statements.append(Statement(kind="set", value=(var_name, expr)))
                continue

            if keyword == KEY_DEKHAO:
                if len(pieces) < 2:
                    raise self._error("'dekhao' needs an expression")
                expr_text = raw_line.split(None, 1)[1]
                try:
                    expr = ExprParser(expr_text).parse()
                    statements.append(Statement(kind="print", value=expr))
                except ParseError:
                    arg_exprs: list[ExprNode] = []
                    for arg_text in self._split_print_args(expr_text):
                        arg_exprs.append(ExprParser(arg_text).parse())
                    statements.append(Statement(kind="print_many", value=arg_exprs))
                continue

            if keyword == KEY_NAW:
                if len(pieces) < 2:
                    raise self._error("'naw' needs: naw <name> [prompt]")
                var_name = pieces[1]
                prompt_expr = None
                if len(pieces) > 2:
                    prompt_text = raw_line.split(None, 2)[2]
                    prompt_expr = ExprParser(prompt_text).parse()
                statements.append(Statement(kind="input", value=(var_name, prompt_expr)))
                continue

            if keyword == KEY_JODI:
                if len(pieces) < 2:
                    raise self._error("'jodi' needs a condition")
                condition_text = raw_line.split(None, 1)[1]
                condition_expr = ExprParser(condition_text).parse()

                then_body, stop_keyword = self._parse_block({KEY_NAHOLE, KEY_SHESH})
                else_body: list[Statement] = []

                if stop_keyword == KEY_NAHOLE:
                    else_body, end_keyword = self._parse_block({KEY_SHESH})
                    if end_keyword != KEY_SHESH:
                        raise self._error("Expected 'shesh' after 'nahole' block")
                elif stop_keyword != KEY_SHESH:
                    raise self._error("Expected 'shesh' after 'jodi' block")

                statements.append(Statement(kind="if", value=(condition_expr, then_body, else_body)))
                continue

            if keyword == KEY_GURAW:
                if len(pieces) < 2:
                    raise self._error("'guraw' needs a condition")
                expr_text = raw_line.split(None, 1)[1]
                condition = ExprParser(expr_text).parse()
                body, end_keyword = self._parse_block({KEY_SHESH})
                if end_keyword != KEY_SHESH:
                    raise self._error("Expected 'shesh' after 'guraw' block")
                statements.append(Statement(kind="while", value=(condition, body)))
                continue

            if keyword == KEY_BREAK:
                statements.append(Statement(kind="break"))
                continue

            if keyword == KEY_CONTINUE:
                statements.append(Statement(kind="continue"))
                continue

            raise self._error(
                "Unknown keyword: "
                f"{keyword}. Use 'dorlam', 'dekhao', 'naw', 'jodi', 'nahole', 'guraw', 'shesh', 'bhenge_jao', and 'cholte_thako'."
            )

        if stop_keywords:
            expected = " / ".join(sorted(stop_keywords))
            raise self._error(f"Expected '{expected}' before file ended")

        return statements, None


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

    @staticmethod
    def _coerce_input_value(raw_value: str) -> Any:
        raw_value = raw_value.strip()
        if re.fullmatch(r"-?\d+", raw_value):
            return int(raw_value)
        if re.fullmatch(r"-?\d+\.\d+", raw_value):
            return float(raw_value)
        return raw_value

    def eval_expr(self, node: ExprNode) -> Any:
        if node.kind == "number":
            return node.value

        if node.kind == "string":
            return node.value

        if node.kind == "bool":
            return node.value

        if node.kind == "var":
            return self.env.get_var(node.value)

        if node.kind == "unary":
            value = self.eval_expr(node.right)
            if node.value == "-":
                return -value
            if node.value == "not":
                return not bool(value)
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
            if operator == "and":
                return bool(left) and bool(right)
            if operator == "or":
                return bool(left) or bool(right)

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

            if statement.kind == "print_many":
                values = [self.eval_expr(expr) for expr in statement.value]
                print(*values)
                continue

            if statement.kind == "input":
                var_name, prompt_expr = statement.value
                prompt = ""
                if prompt_expr is not None:
                    prompt = str(self.eval_expr(prompt_expr))
                user_text = input(prompt)
                self.env.set_var(var_name, self._coerce_input_value(user_text))
                continue

            if statement.kind == "if":
                condition, then_body, else_body = statement.value
                if self.eval_expr(condition):
                    self.execute(then_body)
                else:
                    self.execute(else_body)
                continue

            if statement.kind == "while":
                condition, body = statement.value
                while self.eval_expr(condition):
                    try:
                        self.execute(body)
                    except ContinueSignal:
                        continue
                    except BreakSignal:
                        break
                continue

            if statement.kind == "break":
                raise BreakSignal()

            if statement.kind == "continue":
                raise ContinueSignal()
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
