from lex import *
import sys
from parser import *

if __name__ == "__main__":
    print("Custom Compiler\n")
    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument.")
    with open(sys.argv[1], 'r') as f:
        source = f.read()

    lexer = Lexer(source)
    parser = Parser(lexer)

    parser.program() # starts the parser
    print("\nParsing complete.")