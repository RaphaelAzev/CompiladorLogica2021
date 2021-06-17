import re
import sys

Operators = ["+", "-", "*", "/", "(", ")", "<", ">", "||", "&&", "!", "=="]
Reserved = ["println", "readln", "while", "if", "else"]

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
        elif(token == "=="):
            return "EQUAL"
        elif(token == ">"):
            return "GREATER"
        elif(token == "<"):
            return "LESSER"
        elif(token == "&&"):
            return "AND"
        elif(token == "||"):
            return "OR"
        elif(token == "!"):
            return "NEG"
        elif(token == "{"):
            return "OPENBLOCK"
        elif(token == "}"):
            return "CLOSEBLOCK"

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
        if (self.value == '<'):
            return self.children[0].Evaluate(symbtable) < self.children[1].Evaluate(symbtable)
        if (self.value == '>'):
            return self.children[0].Evaluate(symbtable) > self.children[1].Evaluate(symbtable)
        if self.value == "==":
            return self.children[0].Evaluate(symbtable) == self.children[1].Evaluate(symbtable)
        if self.value == "&&":
            return self.children[0].Evaluate(symbtable) and self.children[1].Evaluate(symbtable)
        if self.value == "||":
            return self.children[0].Evaluate(symbtable) or self.children[1].Evaluate(symbtable)

class UnOp(Node):
    def Evaluate(self, symbtable):
        if (self.value == '+'):
            return +(self.children[0].Evaluate(symbtable))
        if (self.value == '-'):
            return -(self.children[0].Evaluate(symbtable))
        elif self.value == "!":
            return  not (self.children[0].Evaluate(symbtable))

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

class ReadNode(Node):
    def Evaluate(self, symbtable):
        return int(input())

class CommandNode(Node):
    def Evaluate(self, symbtable):
        for x in self.children:
            x.Evaluate(symbtable)

class NoOp(Node):
    def __init__(self):
        pass

    def Evaluate(self):
        pass

class WhileNode(Node): 
    def Evaluate(self, symbtable):
        while self.children[0].Evaluate(symbtable) == True:
            self.children[1].Evaluate(symbtable)
        
class IfNode(Node): 
    def Evaluate(self, symbtable):
        if self.children[0].Evaluate(symbtable) == True:
            self.children[1].Evaluate(symbtable) 
        # Checa se tem else e roda ele
        elif len(self.children) == 3:
            self.children[2].Evaluate(symbtable) 


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
                
                if text not in Reserved:
                    self.actual = Token("identifier", text)
                else:
                    self.actual = Token(text,text)

            else:
                self.actual = Token(valor = self.origin[self.position], typetoken = get_type(self.origin[self.position]))
                self.position += 1

                if(self.position < len(self.origin)):
                    while(get_type(self.origin[self.position]) == self.actual.type and self.origin[self.position] not in Operators):
                        self.actual.value += self.origin[self.position] 
                        self.position += 1
                        # Tratamento especial para n confundir == com =
                        if (self.actual.value in Operators):
                            self.actual.type = get_type(self.actual.value)
                            break
                        if(self.position == len(self.origin)):
                            break

        return self.actual

class Parser():
    def __init__(self):
        self.tokens = Tokenizer

    @staticmethod
    def parseBlock():
        #Parser.tokens.selectNext()
        nodes = []
        if Parser.tokens.actual.type == "OPENBLOCK":
            Parser.tokens.selectNext()
            while Parser.tokens.actual.type != "EOF" and Parser.tokens.actual.type != "CLOSEBLOCK":
                nodes.append(Parser.parseCommand())
            # Select next pra n confundir um bloco finalizado com final do programa
            Parser.tokens.selectNext()
    
        else:
            raise ValueError("Nao existe uma abertura ou fechadura de bloco")

        return CommandNode("BLOCK", nodes)

    @staticmethod
    def parseCommand():

        if (Parser.tokens.actual.type == "identifier"):
            result = Identifier(Parser.tokens.actual.value)
            Parser.tokens.selectNext()

            if (Parser.tokens.actual.type == "ASSIGN"):
                result = AssignOp("=", [result, Parser.parseOrExpression()])

                if (Parser.tokens.actual.type == "ENDL"):
                    Parser.tokens.selectNext()
                    return result

                else:
                    raise ValueError("ERRO, esperava-se um fim de linha com ;")
            else:
                raise ValueError("ERRO, esperava-se uma atribuicao com =")
        
        elif (Parser.tokens.actual.type == "println"): 
            result = PrintNode(Parser.tokens.actual.value, [Parser.parseOrExpression()])
            
            if (Parser.tokens.actual.type == "ENDL"):
                Parser.tokens.selectNext()
                return result
                
            else:
                raise ValueError("ERRO, esperava-se um fim de linha com ;")

        elif Parser.tokens.actual.type == "while":
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type == "OPENBR":
                # Cria condicao do while
                cond = Parser.parseOrExpression()
                if Parser.tokens.actual.type == "CLOSEBR":
                    Parser.tokens.selectNext()
                    # Cria o/s commando/s dentro do while
                    commands = Parser.parseCommand()
                    # Cria node do while
                    result = WhileNode("while", [cond, commands])
                    return result
                else:
                    raise ValueError("ERRO: nao fechou parenteses do while")
            else:
                raise ValueError("ERRO: nao abriu parenteses do while")
        
        elif Parser.tokens.actual.type == "if":
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type == "OPENBR":
                # Cria condicao do if
                cond = Parser.parseOrExpression()
                if Parser.tokens.actual.type == "CLOSEBR":
                    Parser.tokens.selectNext()
                    # Cria commandos
                    commands = Parser.parseCommand()
                    # Cria else se tiver
                    if Parser.tokens.actual.type == 'else':
                        Parser.tokens.selectNext()
                        elseblock = Parser.parseCommand()
                        result = IfNode("if", [cond, commands, elseblock])
                        return result

                    # Senao cria if sem else
                    else:
                        result = IfNode("if", [cond, commands])
                        return result
                else:
                    raise ValueError("ERRO: nao fechou parenteses do if")
            else:
                raise ValueError("ERRO: nao abriu parenteses do if")

        elif (Parser.tokens.actual.type == "ENDL"):
            Parser.tokens.selectNext()
            # se so tiver ; faz nada
            return NoOp(None)
        
        # se nao cair em nenhum dos casos chama BLOCK
        else:
            result = Parser.parseBlock()
            return result
            

    @staticmethod
    def parseOrExpression():

        result = Parser.parseAndExpression()

        while(Parser.tokens.actual.type == "OR"):
            if Parser.tokens.actual.type == "OR":
                return BinOp(Parser.tokens.actual.value, [result, Parser.parseAndExpression()])
        
        return result
        
    @staticmethod
    def parseAndExpression():

        result = Parser.parseEqExpression()

        while(Parser.tokens.actual.type == "AND"):
            if Parser.tokens.actual.type == "AND":
                return BinOp(Parser.tokens.actual.value, [result, Parser.parseEqExpression()])

        return result

    @staticmethod
    def parseEqExpression():

        result = Parser.parseRelExpression()

        while(Parser.tokens.actual.type == "EQUAL"):
            if Parser.tokens.actual.type == "EQUAL":
                return BinOp(Parser.tokens.actual.value, [result, Parser.parseRelExpression()])

        return result


    @staticmethod
    def parseRelExpression():

        result = Parser.parseExpression()

        while(Parser.tokens.actual.type == "GREATER" or Parser.tokens.actual.type == "LESSER"):
            if Parser.tokens.actual.type == "GREATER":
                return BinOp(Parser.tokens.actual.value, [result, Parser.parseExpression()])
            
            if Parser.tokens.actual.type == "LESSER":
                return BinOp(Parser.tokens.actual.value, [result, Parser.parseExpression()])\
        
        return result

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
            result = Parser.parseOrExpression()
            if Parser.tokens.actual.type != "CLOSEBR":
                raise Exception('ERRO: parenteses errado')

            Parser.tokens.selectNext()
        
        elif(Parser.tokens.actual.type == "identifier"):
            result = Identifier(Parser.tokens.actual.value)
            Parser.tokens.selectNext()

        elif Parser.tokens.actual.type == "NOT":
            result = UnOp(Parser.tokens.actual.value, [Parser.parseFactor()])

        elif(Parser.tokens.actual.type == "readln"):
            result = ReadNode()
            Parser.tokens.selectNext()
            if(Parser.tokens.actual.type == "OPENBR"):
                Parser.tokens.selectNext()
                if Parser.tokens.actual.type != "CLOSEBR":
                    raise Exception('ERRO: parenteses errado em um readln')
                Parser.tokens.selectNext()
            else:
                raise Exception('ERRO: parenteses errado em um readln')

        else:
            raise Exception('ERRO')

        return result

    @staticmethod
    def run(code):
        nocommentstring = PrePro.filter(code.rstrip('\n'))
        nocommentstring = nocommentstring.replace("\n", "")
        Parser.tokens = Parser().tokens(origem = nocommentstring) 

        # Select next pra pegar o primeiro token
        Parser.tokens.selectNext()

        compiled = Parser().parseBlock()

        # select next pois o programa sai em uma fechadura de } 
        # Parser.tokens.selectNext()

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
