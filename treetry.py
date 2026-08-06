from dataclasses import dataclass
from lex import tokenize          # whatever your lexer function is called
from abstree import Parser        # or wherever your Parser lives

with open("Try1.plink", "r", encoding="utf-8") as file:
    source = file.read()

tokens = tokenize(source)         # lexer produces the tokens
program = Parser(tokens).parse()  # parser turns them into the tree
for stmt in program:
    print(stmt)
