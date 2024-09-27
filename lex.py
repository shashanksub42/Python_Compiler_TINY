import enum
import sys 

## Specifies every possible token our language allows
class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3

    # Keywords
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111

    # Operators
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211

## Keep track of what type of token it is and the exact text from the code
class Token:
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText # Then token's actual text. Used for identifiers, strings and numbers
        self.kind = tokenKind # The token type that the token is classified as

class Lexer:
    def __init__(self, source):
        self.source = source + '\n' #string of code which needs to be parsed
        self.curChar = ''
        self.curPos = -1
        self.nextChar()

    def nextChar(self):
        self.curPos += 1
        if self.curPos >= len(self.source):
            self.curChar = '\0'
        else:
            self.curChar = self.source[self.curPos]

    def peek(self):
        if self.curPos + 1 >= len(self.source):
            return '\0'
        else:
            return self.source[self.curPos + 1]

    def abort(self, message):
        sys.exit("Lexing error. " + message)

    def skipWhiteSpace(self):
        while self.curChar == ' ' or self.curChar == '\t' or self.curChar == '\r':
            self.nextChar()

    def skipComment(self):
        if self.curChar == '#':
            while self.curChar != '\n':
                self.nextChar()

    def getToken(self):
        self.skipWhiteSpace()
        self.skipComment()
        token = None

        # Plus token
        if self.curChar == '+':
            token = Token(self.curChar, TokenType.PLUS)
        # Minus token
        elif self.curChar == '-':
            token = Token(self.curChar, TokenType.MINUS)
        # Asterisk
        elif self.curChar == '*':
            token = Token(self.curChar, TokenType.ASTERISK)
        # Slash
        elif self.curChar == '/':
            token = Token(self.curChar, TokenType.SLASH)
        # Assignment and Equals ops
        elif self.curChar == '=':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.EQEQ)
            else:
                token = Token(self.curChar, TokenType.EQ)
        # > and >=
        elif self.curChar == '>':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.GTEQ)
            else:
                token = Token(self.curChar, TokenType.GT)
        # < and <=
        elif self.curChar == '<':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.LTEQ)
            else:
                token = Token(self.curChar, TokenType.LT)
        # !=
        elif self.curChar == '!':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())
        # STRING type
        elif self.curChar == '\"':
            self.nextChar()
            startPos = self.curPos
            # no escape characters and no %
            while self.curChar != '\"':
                if self.curChar == '\r' or self.curChar == '\n' or self.curChar == '\t' or self.curChar == '\\' or self.curChar == '%':
                    self.abort("Illegal character in string.")
                self.nextChar()

            tokText = self.source[startPos : self.curPos]
            token = Token(tokText, TokenType.STRING)

        # NUMBERS
        elif self.curChar.isdigit():
            # store the start position of the number
            startPos = self.curPos
            # iterate until the next char is not a number
            while self.peek().isdigit():
                self.nextChar()
            #check if next char is decimal
            if self.peek() == '.':
                self.nextChar()
                # if the next char after the decimal point is not a number, then throw an error
                if not self.peek().isdigit():
                    self.abort("Illegal character in number.")
                # keep moving to the next char until it is not a number
                while self.peek().isdigit():
                    self.nextChar()
            
            tokText = self.source[startPos : self.curPos+1]
            token = Token(tokText, TokenType.NUMBER)



        # newline char
        elif self.curChar == '\n':
            token = Token(self.curChar, TokenType.NEWLINE)
        # EOF char
        elif self.curChar == '\0':
            token = Token(self.curChar, TokenType.EOF)
        else:
            # unknown token
            self.abort("Unknown Token: " + self.curChar)
        
        self.nextChar()
        return token 
