from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    # Keywords
    LET = auto()
    PRINT = auto()
    IF = auto()
    ELSE = auto()

    # Literals
    IDENTIFIER = auto()
    NUMBER_INT = auto()
    NUMBER_FLOAT = auto()
    STRING = auto()

    # Arithmetic operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()

    # Comparison operators
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    EQUAL_EQUAL = auto()
    BANG_EQUAL = auto()

    # Assignment
    EQUAL = auto()

    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()

    # Special
    ERROR = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    text: str
    line: int


# For the "munch the whole word, then look it up" approach
KEYWORDS = {
    "let": TokenType.LET,
    "print": TokenType.PRINT,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
}


#Tokenization

def tokenize(source):
    tokens = []
    pos = 0
    line = 1


    while pos < len(source):
        current_char = source[pos]

        # 2. if it produces nothing (space, newline, @ comment): handle and continue
        if current_char == " ":
            pos+=1
        
        elif current_char == "@":
            pos += 1
            while source[pos] != "@" and source[pos] !="\0":
                pos += 1
            if source[pos] == "\0":
                raise SyntaxError(f"Line {line}: unterminated comment")
            pos +=1

        elif current_char == "\n":
            line += 1
            pos += 1


        # 3. otherwise dispatch on its family (digit / letter / " / symbol)

        elif current_char.isdigit():
            start = pos
            while source[pos].isdigit():
                pos += 1
            is_float = False
            if source[pos] == "." and source[pos + 1].isdigit():
                is_float = True
                pos += 1
                while source[pos].isdigit():
                    pos += 1
            text = source[start:pos]
            token_type = TokenType.NUMBER_FLOAT if is_float else TokenType.NUMBER_INT
            tokens.append(Token(token_type, text, line))


        elif current_char.isalpha():
            start = pos
            while source[pos].isalnum() or source[pos] == "_":
                pos += 1
            word = source[start:pos]
            
            token_type = KEYWORDS.get(word, TokenType.IDENTIFIER)
            tokens.append(Token(token_type, word, line))
                    
        elif current_char == "(":     # a SEPARATE branch, same indentation level
            tokens.append(Token(TokenType.LPAREN, "(", line))
            pos += 1
        elif current_char == ")":     # another sibling
            tokens.append(Token(TokenType.RPAREN, ")", line))
            pos += 1
        elif current_char == "<":     # another sibling
            if source[pos + 1] == "=":
                tokens.append(Token(TokenType.LESS_EQUAL, "<=", line))
                pos += 2
            else:
                tokens.append(Token(TokenType.LESS, "<", line))
                pos += 1
        elif current_char == ">":     # another sibling
            if source[pos + 1] == "=":
                tokens.append(Token(TokenType.GREATER_EQUAL, ">=", line))
                pos += 2
            else:
                tokens.append(Token(TokenType.GREATER, ">", line))
                pos += 1
        elif current_char == "\0":
            break

        elif current_char == '"' :
            start = pos 
            pos += 1
            while source[pos] != '"' and source[pos] !="\0" :
                pos += 1
            if source[pos] == "\0":
                raise SyntaxError(f"Line {line}: unterminated string")
            pos += 1
            text = source[start+1:pos-1] 
            tokens.append(Token(TokenType.STRING, text, line))
        
        elif current_char == '=' :
            if source[pos + 1] == "=":
                tokens.append(Token(TokenType.EQUAL_EQUAL, "==", line))
                pos += 2
            else:
                tokens.append(Token(TokenType.EQUAL, "=", line))
                pos += 1
        elif current_char == '!' :
            if source[pos+1] == '=' :
                tokens.append(Token(TokenType.BANG_EQUAL, "!=", line))
                pos += 2
            else:
                raise SyntaxError(f"Line {line} : Missing equal sign after !, plinkus doesnt have a not operator (yet)")
            
            
        # copy and paste charachters no special features for lexer 
        elif current_char == "{":
            tokens.append(Token(TokenType.LBRACE, "{", line))
            pos += 1
        elif current_char == "}":
            tokens.append(Token(TokenType.RBRACE, "}", line))
            pos += 1
        elif current_char == ";":
            tokens.append(Token(TokenType.SEMICOLON, ";", line))
            pos += 1
        elif current_char == "+":
            tokens.append(Token(TokenType.PLUS, "+", line))
            pos += 1
        elif current_char == "-":
            tokens.append(Token(TokenType.MINUS, "-", line))
            pos += 1
        elif current_char == "*":
            tokens.append(Token(TokenType.STAR, "*", line))
            pos += 1
        elif current_char == "/":
            tokens.append(Token(TokenType.SLASH, "/", line))
            pos += 1

        # 4. if it belongs to no family: error
        else : 
            raise SyntaxError(f"Line {line}: unexpected character '{current_char}'")
    
        
    tokens.append(Token(TokenType.EOF, "", line))
    print(tokens)
    return tokens


with open("Try1.txt") as f:
    source = f.read() + "\0"
    tokenize(source)

