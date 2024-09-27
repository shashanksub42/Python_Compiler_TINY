from lex import *

if __name__ == "__main__":
    source = "+= \"This is a stringgg\" # comment comment "
    lexer = Lexer(source)

    token = lexer.getToken()
    while token.kind != TokenType.EOF:
        print(token.kind)
        token = lexer.getToken()