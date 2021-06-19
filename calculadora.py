import re
import sys

Operators = ["+", "-", "*", "/", "(", ")", "<", ">", "||", "&&", "!", "==", "{", "}"]

Reserved = ["println", "readln", "while", "if", "else", "false", "true", "bool" ,"int", "string"]

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


class ASMBgen():
    # String pra guardar o codigo assembly gerado pelo compilador
    generatedCode = ""

    # String pra guardar o init padrao fornecido pelo arquivo no roteiro 8
    defaultStart = """
; constantes
SYS_EXIT equ 1
SYS_READ equ 3
SYS_WRITE equ 4
STDIN equ 0
STDOUT equ 1
True equ 1
False equ 0

segment .data

segment .bss  ; variaveis
  res RESB 1

section .text
  global _start

print:  ; subrotina print

  PUSH EBP ; guarda o base pointer
  MOV EBP, ESP ; estabelece um novo base pointer

  MOV EAX, [EBP+8] ; 1 argumento antes do RET e EBP
  XOR ESI, ESI

print_dec: ; empilha todos os digitos
  MOV EDX, 0
  MOV EBX, 0x000A
  DIV EBX
  ADD EDX, '0'
  PUSH EDX
  INC ESI ; contador de digitos
  CMP EAX, 0
  JZ print_next ; quando acabar pula
  JMP print_dec

print_next:
  CMP ESI, 0
  JZ print_exit ; quando acabar de imprimir
  DEC ESI

  MOV EAX, SYS_WRITE
  MOV EBX, STDOUT

  POP ECX
  MOV [res], ECX
  MOV ECX, res

  MOV EDX, 1
  INT 0x80
  JMP print_next

print_exit:
  POP EBP
  RET

; subrotinas if/while
binop_je:
  JE binop_true
  JMP binop_false

binop_jg:
  JG binop_true
  JMP binop_false

binop_jl:
  JL binop_true
  JMP binop_false

binop_false:
  MOV EBX, False
  JMP binop_exit
binop_true:
  MOV EBX, True
binop_exit:
  RET

_start:

PUSH EBP ; guarda o base pointer
MOV EBP, ESP ; estabelece um novo base pointer

"""

    defaultEnd = """
; interrupcao de saida
POP EBP
MOV EAX, 1
INT 0x80
"""
    
    @staticmethod
    def NodeAdd(NodeCode):
        # Soma codigo do node ao codigo gerado pelo compilador
        ASMBgen.generatedCode += NodeCode + "\n"

    @staticmethod
    def WriteAll():
        with open ("compiled.nasm", 'w') as f:
            # Escreve o inicio padrao + o codigo + o final padrao em um arquivo
            f.write(ASMBgen.defaultStart + ASMBgen.generatedCode + ASMBgen.defaultEnd)

class SymbolTable():
    def __init__(self):
        self.symbtable = {}
        # nova table pra guardar os deslocamentos
        self.deslocateTable = {}
        # variavel que representa o deslocamento
        self.deslocate = 0

    # Agora sao tuplas com format (valor, tipo)
    def getter(self, key):
        if key in self.symbtable.keys():
            return self.symbtable[key]

        else:
            raise ValueError("Variavel {} não existe na Tabela".format(key))

    # Funcao pra pegar o deslocamento
    def getDeslocate(self, key):
        if key in self.deslocateTable.keys():
            return self.deslocateTable[key]

        else:
            raise ValueError("Variavel {} não existe na Tabela".format(key))

    def setter(self, key, value):
        if key in self.symbtable:
            self.symbtable[key] = (value, self.symbtable[key][1])
        else:
            raise ValueError("Variavel {} não existe na Tabela".format(key))

    # Declaracao de variavel, nao da valor mas da um tipo para a chave
    def declare(self, key, type):
        # Quando criar variavel, desloca 4 
        self.deslocate += 4
        if (not self.declared(key)):
            self.symbtable[key] = (None, type)
            # Salva deslocamento pra essa variavel na tabela
            self.deslocateTable[key] = self.deslocate
        else:
            raise ValueError(f"ERRO: variavel ja {key} declarada")

    def declared(self, key):
        if (key in self.symbtable):
            return True


# Agora todos os nodes retornam tuplas e fazem operacoes com um elemento no indice 0 da tupla
class Node():
    
    node_id = 0

    def __init__(self, val = None, nodelist = None):
        self.value = val
        self.children = nodelist

    def Evaluate(self):
        pass

class BinOp(Node):
    def Evaluate(self, symbtable):
        # Dar evaluates antes pra n repetir e escrever varios assemblies
        c1eval = self.children[0].Evaluate(symbtable)

        ASMBgen.NodeAdd("PUSH EBX")

        c2eval = self.children[1].Evaluate(symbtable)

        ASMBgen.NodeAdd("POP EAX")

        # Checa se esta dentro da combinacao de tipos permitida
        cond1 = (c1eval[1] in ["int", "bool"] and c2eval[1] == "string")
        cond2 = (c1eval[1] == "string" and c2eval[1] in ["int", "bool"])

        if (cond1 or cond2):
            raise ValueError(f"ERRO: Nao se pode operar {self.children[0].Evaluate(symbtable)[1]} com {self.children[1].Evaluate(symbtable)[1]}")

        if (self.value == '*'):
            ASMBgen.NodeAdd("IMUL EBX")
            ASMBgen.NodeAdd("MOV EBX, EAX")
            return (c1eval[0] * c2eval[0], "int")
        elif (self.value == '/'):
            ASMBgen.NodeAdd("IDIV EBX")
            ASMBgen.NodeAdd("MOV EBX, EAX")
            return (c1eval[0] // c2eval[0], "int")
        elif (self.value == '+'):
            ASMBgen.NodeAdd("ADD EAX, EBX")
            ASMBgen.NodeAdd("MOV EBX, EAX")
            return (c1eval[0] + c2eval[0], "int")
        elif (self.value == '-'):
            ASMBgen.NodeAdd("SUB EAX, EBX")
            ASMBgen.NodeAdd("MOV EBX, EAX")
            return (c1eval[0] - c2eval[0], "int")
        elif (self.value == '<'):
            ASMBgen.NodeAdd("CMP EAX, EBX")
            ASMBgen.NodeAdd("CALL binop_jl")
            return (c1eval[0] < c2eval[0], "bool")
        elif (self.value == '>'):
            ASMBgen.NodeAdd("CMP EAX, EBX")
            ASMBgen.NodeAdd("CALL binop_jg")
            return (c1eval[0] > c2eval[0], "bool")
        elif self.value == "==":
            ASMBgen.NodeAdd("CMP EAX, EBX")
            ASMBgen.NodeAdd("CALL binop_je")
            return (c1eval[0] == c2eval[0], "bool")
        elif self.value == "&&":
            ASMBgen.NodeAdd("OR EBX, EAX")
            #ASMBgen.NodeAdd("MOV EBX, EAX")
            return (c1eval[0] and c2eval[0], "bool")
        elif self.value == "||":
            ASMBgen.NodeAdd("AND EBX, EAX")
            #ASMBgen.NodeAdd("MOV EBX, EAX")
            return (c1eval[0] or c2eval[0], "bool")

class UnOp(Node):
    def Evaluate(self, symbtable):
        c1eval = self.children[0].Evaluate(symbtable)

        if (self.value == '+'):
            return (+(c1eval[0]), "int")
        elif (self.value == '-'):
            ASMBgen.NodeAdd(f"MOV EAX, {c1eval[0]}")
            ASMBgen.NodeAdd("MOV EBX, -1")
            ASMBgen.NodeAdd("IMUL EBX")
            ASMBgen.NodeAdd("MOV EBX, EAX")
            return (-(c1eval[0]), "int")
        elif self.value == "!":
            ASMBgen.NodeAdd("NEG EBX")
            return  (not (c1eval[0]), "bool")

class IntVal(Node):
    def Evaluate(self, symbtable):
        ASMBgen.NodeAdd(f"MOV EBX, {int(self.value)}")
        return (int(self.value), "int")

class Identifier(Node):
    def __init__(self, val, type = None):
        super().__init__(val=val)
        self.type = type

    def Evaluate(self, symbtable):
        # Pra checar se eh declaracao ou nao
        declared_this = 0
        if (self.type != None):
            declared_this = 1
            symbtable.declare(self.value, self.type)
            ASMBgen.NodeAdd(f"PUSH DWORD 0 ; Dim {self.value} as {self.type} [EBP-{symbtable.getDeslocate(self.value)}]")

        # Se nao eh declacao roda esse assembly
        if (declared_this == 0):
            ASMBgen.NodeAdd(f"MOV EBX, [EBP-{symbtable.getDeslocate(self.value)}]")
            
        return symbtable.getter(self.value)

class AssignOp(Node):
    def Evaluate(self, symbtable):
        self.children[0].Evaluate(symbtable)
        varname = self.children[0].value
        type1 = symbtable.getter(varname)[1]

        newValue = self.children[1].Evaluate(symbtable)

        # Checa se sao tipos iguais no assign
        if type1 != newValue[1]:
            raise ValueError(f"ERRO: Nao podemos operar {type1} com {newValue[1]}")

        symbtable.setter(varname, newValue[0])
        ASMBgen.NodeAdd(f"MOV [EBP-{symbtable.getDeslocate(varname)}], EBX")

class PrintNode(Node):
    def Evaluate(self, symbtable):
        print(self.children[0].Evaluate(symbtable)[0])
        ASMBgen.NodeAdd("PUSH EBX")
        ASMBgen.NodeAdd("CALL print")
        ASMBgen.NodeAdd("POP EBX")

class ReadNode(Node):
    def Evaluate(self, symbtable):
        return (int(input()), "int")

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
    def __init__(self, val = None, nodelist = None):
        self.value = val
        self.children = nodelist
        self.node_id = Node.node_id + 1
        Node.node_id += 1 


    def Evaluate(self, symbtable):
        ASMBgen.NodeAdd(f"LABEL_WHILE{self.node_id}:")
        self.children[0].Evaluate(symbtable)
        ASMBgen.NodeAdd("CMP EBX, False")
        ASMBgen.NodeAdd(f"JE LABEL_WEND{self.node_id}")
        #self.children[1].Evaluate(symbtable)

        while self.children[0].Evaluate(symbtable)[0] == True:
            self.children[1].Evaluate(symbtable)
        
        ASMBgen.NodeAdd(f"JMP LABEL_WHILE{self.node_id}")
        ASMBgen.NodeAdd(f"LABEL_WEND{self.node_id}:")

class IfNode(Node): 
    def __init__(self, val = None, nodelist = None):
        self.value = val
        self.children = nodelist
        self.node_id = Node.node_id + 1
        Node.node_id += 1               

    def Evaluate(self, symbtable):
        c1eval = self.children[0].Evaluate(symbtable)
        ASMBgen.NodeAdd("CMP EBX, False")
        # Checa se existe else pra criar label
        if len(self.children) == 3:
            ASMBgen.NodeAdd(f"JE LABEL_ELSE{self.node_id}")
        else:
            ASMBgen.NodeAdd(f"JE LABEL_ENDIF{self.node_id}")

        # So gera oq esta dentro do if se a condicao for verdade
        if c1eval[0] == True:
            self.children[1].Evaluate(symbtable) 
            ASMBgen.NodeAdd(f"JMP LABEL_ENDIF{self.node_id}")
        # Checa se tem else e roda ele
        elif len(self.children) == 3:
            ASMBgen.NodeAdd(f"LABEL_ELSE{self.node_id}:")
            self.children[2].Evaluate(symbtable) 

        ASMBgen.NodeAdd(f"LABEL_ENDIF{self.node_id}:")

class BoolVal(Node):
    def Evaluate(self, symbtable):
        if(self.value == "true"):
            ASMBgen(f"MOV EBX, True")
            return(True, "bool")
        elif(self.value == "false"):
            ASMBgen(f"MOV EBX, False")
            return(False,"bool")
        return (self.value, "bool")

class StringVal(Node):        
    def Evaluate(self,symbtable):
        return (self.value, "string")


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

            if self.origin[self.position] == '"':
                word = ''
                self.position += 1
                while (self.origin[self.position] != '"'):
                    word += self.origin[self.position]
                    self.position += 1
                # pra n continuar com abre aspas 
                self.position += 1
                self.actual = Token("string", word)
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

        if (Parser.tokens.actual.type == "bool" or Parser.tokens.actual.type == "string" or Parser.tokens.actual.type == "int"):
            vartype = Parser.tokens.actual.type
            Parser.tokens.selectNext()
            if (Parser.tokens.actual.type == "identifier"):
                # EX: bool x // x = (None, bool);
                result = Identifier(Parser.tokens.actual.value, vartype)
                Parser.tokens.selectNext()
                if (Parser.tokens.actual.type == "ASSIGN"):
                    result = AssignOp("=", [result, Parser.parseOrExpression()])

                if (Parser.tokens.actual.type == "ENDL"):
                    Parser.tokens.selectNext()
                    return result

                else: 
                    raise ValueError(f"ERRO: Sem ; depois de declaracao de {vartype}")

            else:
                raise ValueError(f"ERRO: Declaracao de {vartype} sem variavel")

        elif (Parser.tokens.actual.type == "identifier"):
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
                result = BinOp(Parser.tokens.actual.value, [result, Parser.parseAndExpression()])
        
        return result
        
    @staticmethod
    def parseAndExpression():

        result = Parser.parseEqExpression()

        while(Parser.tokens.actual.type == "AND"):
            if Parser.tokens.actual.type == "AND":
                result = BinOp(Parser.tokens.actual.value, [result, Parser.parseEqExpression()])

        return result

    @staticmethod
    def parseEqExpression():

        result = Parser.parseRelExpression()

        while(Parser.tokens.actual.type == "EQUAL"):
            if Parser.tokens.actual.type == "EQUAL":
                result = BinOp(Parser.tokens.actual.value, [result, Parser.parseRelExpression()])

        return result


    @staticmethod
    def parseRelExpression():

        result = Parser.parseExpression()

        while(Parser.tokens.actual.type == "GREATER" or Parser.tokens.actual.type == "LESSER"):
            if Parser.tokens.actual.type == "GREATER":
                result = BinOp(Parser.tokens.actual.value, [result, Parser.parseExpression()])
            
            if Parser.tokens.actual.type == "LESSER":
                result = BinOp(Parser.tokens.actual.value, [result, Parser.parseExpression()])
        
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

        elif(Parser.tokens.actual.type == "true" or Parser.tokens.actual.type == "false"):
            result = BoolVal(Parser.tokens.actual.value)
            Parser.tokens.selectNext()

        elif(Parser.tokens.actual.type == "string"):
            result = StringVal(Parser.tokens.actual.value)
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

        elif Parser.tokens.actual.type == "NEG":
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
    ASMBgen.WriteAll()


if __name__ == "__main__":
    main()
