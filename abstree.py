from dataclasses import dataclass
from lex import TokenType

# --- expressions ---
@dataclass
class Literal:
    value: object # int, float, or str
    line: int
@dataclass
class Variable:
    name: str
    line: int
@dataclass
class Unary:
    op: str # e.g. '-'
    operand: object # an expression node
    line: int
@dataclass
class Binary:
    op: str # e.g. '+', '&lt;=', '=='
    left: object # an expression node
    right: object # an expression node
    line: int
# --- statements ---
@dataclass
class PrintStmt:
    expr: object
    line: int
@dataclass
class LetStmt:
    name: str
    value: object
    line: int
@dataclass
class ExprStmt:
    expr: object
    line: int
@dataclass
class Block:
    statements: list
    line: int
@dataclass
class IfStmt:
    condition: object
    then_branch: object # usually a Block
    else_branch: object # a Block or None
    line: int

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    # ---------- low-level cursor helpers ----------
    
    # returns current token thats on cursor 

    def peek(self):
        return self.tokens[self.current]


    # chkecks whether cursor token is the type we are asking about 

    def check(self, ttype):
        return self.peek().type == ttype


    # stores token on cursor then moves cursor if its not eof , outputs token of cursor before the move 

    def advance(self):
        tok = self.peek()
        if tok.type != TokenType.EOF:
            self.current += 1
        return tok


    # creates tuples of types we accept (*ttypes creates tuple of things you give), if cursor token is in those we move the cursor and return true otherwise we leave       the token where it is and return false 

    def match(self, *ttypes):
        if self.peek().type in ttypes:
            self.advance()
            return True
        return False


    # consume is like match but it expects one type since it is demanded for a specific token and if its not that it raises an error
    # it returns the token on cursor because it calls self.advance then moves obviously 

    def consume(self, ttype, message):
        if self.check(ttype):
            return self.advance()
        tok = self.peek()
        raise SyntaxError(f"Line {tok.line}: {message}")

    # ---------- entry point ----------
    def parse(self):
        statements = []
        while not self.check(TokenType.EOF):
            statements.append(self.statement())
        return statements

    # ---------- statements ----------
    def statement(self):
        t = self.peek().type
        if t == TokenType.PRINT:
            return self.print_stmt()
        if t == TokenType.LET:
            return self.let_stmt()
        if t == TokenType.IF:
            return self.if_stmt()
        if t == TokenType.LBRACE:
            return self.block()
        return self.expr_stmt()

    def print_stmt(self):
        kw = self.advance()
        self.consume(TokenType.LPAREN, "expected '(' after 'print'")
        value = self.expression()
        self.consume(TokenType.RPAREN, "expected ')' after print value")
        self.consume(TokenType.SEMICOLON, "expected ';' after print statement")
        return PrintStmt(value, kw.line)

    def let_stmt(self):
        kw = self.advance()
        name = self.consume(TokenType.IDENTIFIER, "expected a name after 'let'")
        self.consume(TokenType.EQUAL, "expected '=' after name in 'let'")
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "expected ';' after let declaration")
        return LetStmt(name.text, value, kw.line)

    def if_stmt(self):
        kw = self.advance()
        self.consume(TokenType.LPAREN, "expected '(' after 'if'")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "expected ')' after if condition")
        then_branch = self.block()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.block()
        return IfStmt(condition, then_branch, else_branch, kw.line)

    def block(self):
        brace = self.consume(TokenType.LBRACE, "expected '{'")
        statements = []
        while not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
            statements.append(self.statement())
        self.consume(TokenType.RBRACE, "expected '}' to close block")
        return Block(statements, brace.line)

    def expr_stmt(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "expected ';' after expression")
        return ExprStmt(expr, expr.line)

    # ---------- expressions: the precedence cascade ----------
    def expression(self):
        return self.equality()

    def equality(self):
        expr = self.comparison()
        while self.peek().type in (TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            op = self.advance()
            right = self.comparison()
            expr = Binary(op.text, expr, right, op.line)
        return expr

    def comparison(self):
        expr = self.term()
        while self.peek().type in (TokenType.LESS, TokenType.GREATER,
                                   TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            op = self.advance()
            right = self.term()
            expr = Binary(op.text, expr, right, op.line)
        return expr

    def term(self):
        expr = self.factor()
        while self.peek().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance()
            right = self.factor()
            expr = Binary(op.text, expr, right, op.line)
        return expr

    def factor(self):
        expr = self.unary()
        while self.peek().type in (TokenType.STAR, TokenType.SLASH):
            op = self.advance()
            right = self.unary()
            expr = Binary(op.text, expr, right, op.line)
        return expr

    def unary(self):
        if self.peek().type == TokenType.MINUS:
            op = self.advance()
            operand = self.unary()
            return Unary(op.text, operand, op.line)
        return self.primary()

    def primary(self):
        tok = self.peek()
        if tok.type == TokenType.NUMBER_INT:
            self.advance()
            return Literal(int(tok.text), tok.line)
        if tok.type == TokenType.NUMBER_FLOAT:
            self.advance()
            return Literal(float(tok.text), tok.line)
        if tok.type == TokenType.STRING:
            self.advance()
            return Literal(tok.text, tok.line)
        if tok.type == TokenType.IDENTIFIER:
            self.advance()
            return Variable(tok.text, tok.line)
        if tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.expression()
            self.consume(TokenType.RPAREN, "expected ')' after expression")
            return expr
        raise SyntaxError(f"Line {tok.line}: expected an expression")

