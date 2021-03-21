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
                result += Parser.parseTerm()

            if Parser.tokens.actual.type == "MINUS":
                result -= Parser.parseTerm()

            #Parser.tokens.selectNext()

        return result
    
    @staticmethod
    def parseTerm():

        result = Parser.parseFactor()

        while(Parser.tokens.actual.type == "MULT" or Parser.tokens.actual.type == "DIV"):
            if Parser.tokens.actual.type == "MULT":
                result *= int(Parser.parseFactor())

            if Parser.tokens.actual.type == "DIV":
                result /= int(Parser.parseFactor())
                result = int(result)


        return result

    @staticmethod
    def parseFactor():

        Parser.tokens.selectNext()

        if(Parser.tokens.actual.type == "INT"):
            result = int(Parser.tokens.actual.value)
            Parser.tokens.selectNext()

        elif Parser.tokens.actual.type == "PLUS":
            result = Parser.parseFactor() * 1

        elif Parser.tokens.actual.type == "MINUS":
            result = Parser.parseFactor() * -1

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
        nocommentstring = PrePro.filter(code)
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
    if(len(sys.argv) < 2):
        raise Exception("Nao foi passado argumento pro arquivo")
    
    print(Parser().run(sys.argv[1]))


if __name__ == "__main__":
    main()
