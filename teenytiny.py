from lex import *
from emit import *
from parser import *
import sys

if __name__ == "__main__":
    print("Custom Compiler\n")
    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument.")
    with open(sys.argv[1], 'r') as f:
        source = f.read()

    # initialize the lexer, parser and emitter
    lexer = Lexer(source)
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter)

    parser.program() # starts the parser
    emitter.writeFile() # write to the output file
    print("\nCompiling complete.")