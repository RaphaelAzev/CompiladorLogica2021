import re
import sys

Operators = ["+", "-"]

def get_type(token):
        if(token.isdigit() == True):
            return "INT"
        elif(token == "+"):
            return "PLUS"
        elif(token == "-"):
            return "MINUS"
        elif(token == " "):
            return "SPACE"


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
        Parser.tokens.selectNext()

        if(Parser.tokens.actual.type == "INT"):
            result = int(Parser.tokens.actual.value)
            Parser.tokens.selectNext()

            while(Parser.tokens.actual.type == "PLUS" or Parser.tokens.actual.type == "MINUS"):
                if Parser.tokens.actual.type == "PLUS":
                    Parser.tokens.selectNext()
                    if(Parser.tokens.actual.type == "INT"):
                        result += int(Parser.tokens.actual.value)
                    else:
                        raise Exception('ERRO: Operador binario nao e seguido de um token valido')

                if Parser.tokens.actual.type == "MINUS":
                    Parser.tokens.selectNext()
                    if(Parser.tokens.actual.type == "INT"):
                        result -= int(Parser.tokens.actual.value)
                    else:
                        raise Exception('ERRO: Operador binario nao e seguido de um token valido')

                Parser.tokens.selectNext()
            if Parser.tokens.actual.type == "EOF":
                return result
            else:
                raise Exception('ERRO: Numero inteiro nao e seguido de um token valido')
        else:
            raise Exception('ERRO: Operacao nao inicia com numero')
        
    @staticmethod
    def run(code):
        Parser.tokens = Parser().tokens(origem = code) 


        return Parser().parseExpression()
    

        

def main():
    if(len(sys.argv) < 2):
        raise Exception("Nao foi passado argumento pro arquivo")
    
    print(Parser().run(sys.argv[1]))


if __name__ == "__main__":
    main()
