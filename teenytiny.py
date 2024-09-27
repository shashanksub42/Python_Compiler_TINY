from lex import *

if __name__ == "__main__":
    source = "+-123 9.8654*/"
    lexer = Lexer(source)

    token = lexer.getToken()
    while token.kind != TokenType.EOF:
        print(token.kind)
        token = lexer.getToken()