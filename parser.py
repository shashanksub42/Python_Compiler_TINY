import sys
from lex import *

# parser keeps track of current token and checks if the code matches the grammar
class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set() # keeps track of variables declared 
        self.labelsDeclared = set() # keeps track of labels declared
        self.labelsGotoed = set() # keeps track of labels goto'ed 

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken() # call this twice to initialize current token and next token
    
    # return true if the current token matches
    def checkToken(self, kind):
        return kind == self.curToken.kind

    # return true if the next token matches
    def checkPeek(self, kind):
        return kind == self.peekToken.kind
    
    # try to match the current token. if no match, then throw an error. advance to the next token
    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    # advance the current token
    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()

    def abort(self, message):
        sys.exit("ERROR: " + message)

    # Production rules

    # program ::= {statement}
    def program(self):
        # initialize the C program with the header and main function
        self.emitter.headerLine("#include <stdio.h>")
        self.emitter.headerLine("int main(void){")
        
        # skipping newline chars
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
        
        # parse all statements in the program
        while not self.checkToken(TokenType.EOF):
            self.statement()

        # return 0 and close the curly bracket
        self.emitter.emitLine("return 0;")
        self.emitter.emitLine("}")

        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO undeclared label: " + label)

    def statement(self):
        # "PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            # print("STATEMENT-PRINT")
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                # simple string
                self.emitter.emitLine("printf(\"" + self.curToken.text + "\\n\");")
                self.nextToken()
            else:
                # expect an expression, print result as a float
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emitLine("));")

        # "IF" comparison "THEN" {statement} "ENDIF"
        elif self.checkToken(TokenType.IF):
            # print("STATEMENT-IF")
            self.nextToken()
            self.emitter.emit("if(")
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emitLine("){")

            # zero or more statements in the body
            while not self.checkToken(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
            self.emitter.emitLine("}")

        # "WHILE" comparison "REPEAT" nl {statement} "ENDWHILE"
        elif self.checkToken(TokenType.WHILE):
            # print("STATEMENT-WHILE")
            self.nextToken()
            self.emitter.emit("while(")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emitLine("){")

            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()
            
            self.match(TokenType.ENDWHILE)
            self.emitter.emitLine("}")

        # "LABEL" ident nl
        elif self.checkToken(TokenType.LABEL):
            # print("STATEMENT-LABEL")
            self.nextToken()

            # make sure that the label doesnt already exist
            if self.curToken.text in self.labelsDeclared:
                self.abort("Label already exists: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)

            self.emitter.emitLine(self.curToken.text + ":")
            self.match(TokenType.IDENT)

        # "GOTO" ident nl
        elif self.checkToken(TokenType.GOTO):
            # print("STATEMENT-GOTO")
            self.nextToken()
            # add the token to the labels goto'ed set
            self.labelsGotoed.add(self.curToken.text)
            self.emitter.emitLine("goto " + self.curToken.text + ";")
            self.match(TokenType.IDENT)

        # "LET" ident "=" expression nl
        elif self.checkToken(TokenType.LET):
            # print("STATEMENT-LET")
            self.nextToken()

            # check if ident exists in the symbols set. if not, then declare it
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            self.emitter.emit(self.curToken.text + "= ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            
            self.expression()
            self.emitter.emitLine(";")

        # "INPUT" ident nl
        elif self.checkToken(TokenType.INPUT):
            # print("STATEMENT-INPUT")
            self.nextToken()

            # check if variable exists. If not, then add it to the symbols set. 
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            # emit scanf but also validate input. if invalid, set the variable to 0 and clear the input
            self.emitter.emitLine("if(0 == scanf(\"%" + "f\", &" + self.curToken.text +")) {")
            self.emitter.emitLine(self.curToken.text + " = 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emitLine("*s\");")
            self.emitter.emitLine("}")
            self.match(TokenType.IDENT)

        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

        self.nl()

    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        # print("COMPARISON")

        self.expression()
        # must be at least one comparison operator, and another expression
        # this "if" block needs to be checked because we need to confirm that what comes after the expression is one of the comparison operators.
        # once we confirm this, we can move to the "while" block to look for more comparison operators
        # if the current token itself is not a comparison operator, then throw an error
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.curToken.text)

        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        # print("EXPRESSION")

        self.term()
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        # print("TERM")

        self.unary()
        while self.checkToken(TokenType.SLASH) or self.checkToken(TokenType.ASTERISK):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        # print("UNARY")

        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        self.primary()

    # primary ::= number | ident
    def primary(self):
        # print("PRIMARY (" +self.curToken.text + ")")

        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # ensure that variable already exists. If not, then throw an error
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curToken.text)
            
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        else:
            # error
            self.abort("Unexpected token at " + self.curToken.text)


    # nl ::= '\n'+
    def nl(self):
        # print("NEWLINE")

        # require at least one newline
        self.match(TokenType.NEWLINE)
        # but we can have extra newlines too
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()