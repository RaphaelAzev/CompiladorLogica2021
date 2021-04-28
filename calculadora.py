import re
import sys
import pyparsing

Operators = ["+", "-", "*", "/", "(", ")", "="]
Reserved = ["println"]

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
        elif(token == "="):
            return "ASSIGN"
        elif(token == ";"):
            return "ENDL"

class SymbolTable():
    def __init__(self):
        self.symbtable = {}

    def getter(self, key):
        if key in self.symbtable.keys():
            return self.symbtable[key]

        else:
            raise ValueError("Key {} não existe na Tabela".format(key))
    
    def setter(self, key, value):
        self.symbtable[key] = value

class Node():
    def __init__(self, val = None, nodelist = None):
        self.value = val
        self.children = nodelist

    def Evaluate(self):
        pass

class BinOp(Node):
    def Evaluate(self, symbtable):
        if (self.value == '*'):
            return self.children[0].Evaluate(symbtable) * self.children[1].Evaluate(symbtable)
        if (self.value == '/'):
            return self.children[0].Evaluate(symbtable) // self.children[1].Evaluate(symbtable)
        if (self.value == '+'):
            return self.children[0].Evaluate(symbtable) + self.children[1].Evaluate(symbtable)
        if (self.value == '-'):
            return self.children[0].Evaluate(symbtable) - self.children[1].Evaluate(symbtable)

class UnOp(Node):
    def Evaluate(self, symbtable):
        if (self.value == '+'):
            return +(self.children[0].Evaluate(symbtable))
        if (self.value == '-'):
            return -(self.children[0].Evaluate(symbtable))

class IntVal(Node):
    def Evaluate(self, symbtable):
        return int(self.value)

class Identifier(Node):
    def Evaluate(self, symbtable):
        return symbtable.getter(self.value)

class AssignOp(Node):
    def Evaluate(self, symbtable):
        symbtable.setter(self.children[0].value, self.children[1].Evaluate(symbtable))

class PrintNode(Node):
    def Evaluate(self, symbtable):
        print(self.children[0].Evaluate(symbtable))

class CommandNode(Node):
    def Evaluate(self, symbtable):
        for x in self.children:
            x.Evaluate(symbtable)

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

            if self.origin[self.position].isalpha():
                text = self.origin[self.position]
                self.position += 1
                while self.position < len(self.origin) and (self.origin[self.position].isdigit() or self.origin[self.position].isalpha() or self.origin[self.position] == "_"): 
                    text += self.origin[self.position]
                    self.position += 1
                
                if text.lower() not in Reserved:
                    self.actual = Token("identifier", text)
                else:
                    self.actual = Token(text.lower(),text.lower())

            else:
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
    def parseBlock():
        Parser.tokens.selectNext()
        nodes = []
        while Parser.tokens.actual.type != "EOF":
            nodes.append(Parser.parseCommand())
    
        return CommandNode("BLOCK", nodes)

    @staticmethod
    def parseCommand():

        if (Parser.tokens.actual.type == "identifier"):
            result = Identifier(Parser.tokens.actual.value)
            Parser.tokens.selectNext()

            if (Parser.tokens.actual.type == "ASSIGN"):
                result = AssignOp("=", [result, Parser.parseExpression()])

                if (Parser.tokens.actual.type == "ENDL"):
                    Parser.tokens.selectNext()
                    return result

                else:
                    raise ValueError("ERRO, esperava-se um fim de linha com ;")
            else:
                raise ValueError("ERRO, esperava-se uma atribuicao com =")
        
        elif (Parser.tokens.actual.type == "println"): 
            result = PrintNode(Parser.tokens.actual.value, [Parser.parseExpression()])
            
            if (Parser.tokens.actual.type == "ENDL"):
                Parser.tokens.selectNext()
                return result
                
            else:
                raise ValueError("ERRO, esperava-se um fim de linha com ;")

        elif (Parser.tokens.actual.type == "ENDL"):
            Parser.tokens.selectNext()
            return result 
        
        else:
            raise ValueError("ERRO, esperava-se um fim de linha com ;")

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
        
        elif(Parser.tokens.actual.type == "identifier"):
            result = Identifier(Parser.tokens.actual.value)
            Parser.tokens.selectNext()

        else:
            raise Exception('ERRO')

        return result

    @staticmethod
    def run(code):
        nocommentstring = PrePro.filter(code.rstrip('\n'))
        nocommentstring = nocommentstring.replace("\n", "")
        Parser.tokens = Parser().tokens(origem = nocommentstring) 

        compiled = Parser().parseBlock()

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

    ST = SymbolTable()

    Parser().run(program).Evaluate(ST)


if __name__ == "__main__":
    main()
