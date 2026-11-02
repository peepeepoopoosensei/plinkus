

from abstree import (Literal, Variable, Unary, Binary,
                     PrintStmt, LetStmt, ExprStmt, Block, IfStmt)


class PlinkusRuntimeError(Exception):
    """An error found while running (not parsing) a program.

    Carries the line number of the node that caused it, so errors stay
    fail-fast with line information, just like SyntaxError in the parser.
    """
    def __init__(self, message, line):
        super().__init__(f"[line {line}] RuntimeError: {message}")
        self.line = line


def is_number(value):
    # in Python bool is a subclass of int
    # so isinstance(True, int) is True we dont want True + 1 to work
    return type(value) in (int, float)


def type_name(value):
    names = {int: "int", float: "float", str: "str", bool: "bool"}
    return names.get(type(value), type(value).__name__)


class Interpreter:
    def __init__(self):
        # One global table of variables: name to value.
        self.variables = {}

    # statements : execute() DOES something and returns nothing.

    def run(self, statements):
        for stmt in statements:
            self.execute(stmt)

    def execute(self, stmt):
        if isinstance(stmt, PrintStmt):
            value = self.evaluate(stmt.expr)
            print(self.to_text(value))

        elif isinstance(stmt, LetStmt):
            value = self.evaluate(stmt.value)
            self.variables[stmt.name] = value

        elif isinstance(stmt, ExprStmt):
            self.evaluate(stmt.expr)          # compute it, throw the result away

        elif isinstance(stmt, Block):
            self.run(stmt.statements)         # a block is just a list of statements

        elif isinstance(stmt, IfStmt):
            condition = self.evaluate(stmt.condition)
            if type(condition) is not bool:
                raise PlinkusRuntimeError(
                    f"if condition must be a comparison, got {type_name(condition)}",
                    stmt.line)
            if condition:
                self.execute(stmt.then_branch)
            elif stmt.else_branch is not None:
                self.execute(stmt.else_branch)

        else:
            raise PlinkusRuntimeError(
                f"unknown statement type {type(stmt).__name__}",
                getattr(stmt, "line", "?"))

    
    # expressions  evaluate() RETURNS a value.
    
    def evaluate(self, expr):
        if isinstance(expr, Literal):
            return expr.value

        if isinstance(expr, Variable):
            if expr.name not in self.variables:
                raise PlinkusRuntimeError(
                    f"undefined variable '{expr.name}'", expr.line)
            return self.variables[expr.name]

        if isinstance(expr, Unary):
            operand = self.evaluate(expr.operand)
            if expr.op == '-':
                if not is_number(operand):
                    raise PlinkusRuntimeError(
                        f"cannot negate {type_name(operand)}", expr.line)
                return -operand
            raise PlinkusRuntimeError(
                f"unknown unary operator '{expr.op}'", expr.line)

        if isinstance(expr, Binary):
            # evlaluate BOTH children first then combine
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)
            return self.binary(expr.op, left, right, expr.line)

        raise PlinkusRuntimeError(
            f"unknown expression type {type(expr).__name__}",
            getattr(expr, "line", "?"))

    def binary(self, op, a, b, line):
        # equality works between any two values
        if op == '==':
            return a == b
        if op == '!=':
            return a != b

        # string concatenation: str + str only
        if op == '+' and type(a) is str and type(b) is str:
            return a + b

        # everything else needs two numbers
        if not (is_number(a) and is_number(b)):
            raise PlinkusRuntimeError(
                f"cannot apply '{op}' to {type_name(a)} and {type_name(b)}", line)


        #   int op int to int, int op float to float (automatic promotion)
        if op == '+':
            return a + b
        if op == '-':
            return a - b
        if op == '*':
            return a * b
        if op == '/':
            if b == 0:
                raise PlinkusRuntimeError("division by zero", line)
            return a / b              
        if op == '<':
            return a < b
        if op == '>':
            return a > b
        if op == '<=':
            return a <= b
        if op == '>=':
            return a >= b

        raise PlinkusRuntimeError(f"unknown operator '{op}'", line)

    def to_text(self, value):
        if type(value) is bool:
            return "true" if value else "false"
        return str(value)


def main():
    from lex import tokenize
    from abstree import Parser

    filename = input("Plinkus file to run: ")

    with open(filename) as f:
        source = f.read()

    try:
        statements = Parser(tokenize(source)).parse()
        Interpreter().run(statements)
    except (SyntaxError, PlinkusRuntimeError) as error:
        print(error)   


if __name__ == "__main__":
    main()
