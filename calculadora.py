import re
import sys
import pyparsing

Operators = ["+", "-", "*", "/", "(", ")"]

def get_type(token):
        if(token.isdigit() == True):
            return "INT"
        elif(token == "+"):
            return "PLUS"
        elif(token == "-"):
            return "MINUS"
        elif(token == " "):
            return "SPACE"
        elif(token == "*"):
            return "MULT"
        elif(token == "/"):
            return "DIV"
        elif(token == "("):
            return "OPENBR"
        elif(token == ")"):
            return "CLOSEBR"   
        
class Node():
    def __init__(self, val = None, nodelist = None):
        self.value = val
        self.children = nodelist

    def Evaluate(self):
        pass

class BinOp(Node):
    def Evaluate(self):
        if (self.value == '*'):
            return self.children[0].Evaluate() * self.children[1].Evaluate()
        if (self.value == '/'):
            return self.children[0].Evaluate() // self.children[1].Evaluate()
        if (self.value == '+'):
            return self.children[0].Evaluate() + self.children[1].Evaluate()
        if (self.value == '-'):
            return self.children[0].Evaluate() - self.children[1].Evaluate()

class UnOp(Node):
    def Evaluate(self):
        if (self.value == '+'):
            return +(self.children[0].Evaluate())
        if (self.value == '-'):
            return -(self.children[0].Evaluate())

class IntVal(Node):
    def Evaluate(self):
        return int(self.value)

class NoOp(Node):
    def __init__(self):
        pass

    def Evaluate(self):
        pass

class Token:
    def __init__(self, typetoken = None, valor = None):
        self.type = typetoken
        self.value = valor

class Tokenizer:
    def __init__(self, origem = None, posicao = 0, atual = None):
        self.origin = origem
        self.position = posicao
        self.actual = atual

    def selectNext(self):
        if(self.position == len(self.origin)):
            self.actual = Token(typetoken = "EOF")
            return self.actual

        if(self.position < len(self.origin)):
            while(self.origin[self.position] == " "):
                self.position += 1
                
                if(self.position == len(self.origin)):
                    self.actual = Token(typetoken = "EOF")
                    return self.actual
            
            self.actual = Token(valor = self.origin[self.position], typetoken = get_type(self.origin[self.position]))
            self.position += 1

            if(self.position < len(self.origin)):
                while(get_type(self.origin[self.position]) == self.actual.type and self.origin[self.position] not in Operators):
                    self.actual.value += self.origin[self.position] 
                    self.position += 1
                    if(self.position == len(self.origin)):
                        break

        return self.actual

class Parser():
    def __init__(self):
        self.tokens = Tokenizer

    @staticmethod
    def parseExpression():
        
        result = Parser.parseTerm()

        while(Parser.tokens.actual.type == "PLUS" or Parser.tokens.actual.type == "MINUS"):
            if Parser.tokens.actual.type == "PLUS":
                result = BinOp(Parser.tokens.actual.value, [result, Parser.parseTerm()])

            if Parser.tokens.actual.type == "MINUS":
                result = BinOp(Parser.tokens.actual.value, [result, Parser.parseTerm()])

            #Parser.tokens.selectNext()

        return result
    
    @staticmethod
    def parseTerm():

        result = Parser.parseFactor()

        while(Parser.tokens.actual.type == "MULT" or Parser.tokens.actual.type == "DIV"):
            if Parser.tokens.actual.type == "MULT":
                result = BinOp(Parser.tokens.actual.value, [result, Parser.parseFactor()])

            if Parser.tokens.actual.type == "DIV":
                result = BinOp(Parser.tokens.actual.value, [result, Parser.parseFactor()])


        return result

    @staticmethod
    def parseFactor():

        Parser.tokens.selectNext()

        if(Parser.tokens.actual.type == "INT"):
            result = IntVal(Parser.tokens.actual.value)
            Parser.tokens.selectNext()

        elif Parser.tokens.actual.type == "PLUS":
            result = UnOp(Parser.tokens.actual.value, [Parser.parseFactor()])

        elif Parser.tokens.actual.type == "MINUS":
            result = UnOp(Parser.tokens.actual.value, [Parser.parseFactor()])

        elif(Parser.tokens.actual.type == "OPENBR"):
            result = Parser.parseExpression()
            if Parser.tokens.actual.type != "CLOSEBR":
                raise Exception('ERRO')

            Parser.tokens.selectNext()
        
        else:
            raise Exception('ERRO')

        return result

    @staticmethod
    def run(code):
        nocommentstring = PrePro.filter(code.rstrip('\n'))
        Parser.tokens = Parser().tokens(origem = nocommentstring) 

        compiled = Parser().parseExpression()

        if Parser.tokens.actual.type == "EOF":
            return compiled
        else:
            raise Exception('ERRO')
    
class PrePro():
    @staticmethod
    def filter(code):
        nocommentstring = re.sub(re.compile("/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/",re.DOTALL ) ,"" ,code)
        return nocommentstring
        

def main():
    c_file = sys.argv[1]
    with open (c_file, 'r') as file:
        program = file.read()

    if(len(sys.argv) < 2):
        raise Exception("Nao foi passado argumento pro arquivo")

    print(Parser().run(program).Evaluate())


if __name__ == "__main__":
    main()
