#from ast import parse
import re
import sys

Operators = ["+", "-", "*", "/", "(", ")", "<", ">", "||", "&&", "!", "==", ",", "}", "{"]

Reserved = ["println", "readln", "while", "if", "else", "false", "true", "bool" ,"int", "string", "return"]

types = ["bool", "int", "string"]

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
        elif token == ",":
            return "COMMA"

class SymbolTable():
    def __init__(self):
        self.symbtable = {}
        self.functiontable = {}

    # Agora sao tuplas com format (valor, tipo)
    def getter(self, key):
        if key in self.symbtable.keys():
            return self.symbtable[key]

        else:
            raise ValueError("Variavel {} não existe na Tabela".format(key))

    def setter(self, key, value):
        if key in self.symbtable:
            # Casta pra true ou false dependendo do valor
            if(self.symbtable[key][1] == "bool"):
                self.symbtable[key] = (int(bool(value)), self.symbtable[key][1])
            else:
                self.symbtable[key] = (value, self.symbtable[key][1])
        else:
            raise ValueError("Variavel {} não existe na Tabela".format(key))

    # Declaracao de variavel, nao da valor mas da um tipo para a chave
    def declare(self, key, type):
        if (not self.declared(key)):
            self.symbtable[key] = (None, type)
        else:
            raise ValueError(f"ERRO: variavel ja {key} declarada")

    def declared(self, key):
        if (key in self.symbtable):
            return True

    # Funcoes sao tuplas com (args, commands, tipo)
    def getFunc(self, key):
        if key in self.functiontable.keys():
            return self.functiontable[key]

        else:
            raise ValueError("Funcao {} não existe na Tabela".format(key))

    # Funcoes sao tuplas com (args, commands, tipo)
    def setFunc(self, key, args, commands, tipo):
        if key not in self.functiontable.keys():
            self.functiontable[key] = (args, commands, tipo)
        else:
            raise ValueError(f"ERRO: funcao ja {key} declarada")


# Agora todos os nodes retornam tuplas e fazem operacoes com um elemento no indice 0 da tupla
class Node():
    def __init__(self, val = None, nodelist = None):
        self.value = val
        self.children = nodelist

    def Evaluate(self):
        pass

class BinOp(Node):
    def Evaluate(self, symbtable):
        # Checa se esta dentro da combinacao de tipos permitida

        var1 = self.children[0].Evaluate(symbtable)
        var2 = self.children[1].Evaluate(symbtable)
        cond1 = (var1[1] in ["int", "bool"] 
                and var2[1] == "string")
        cond2 = (var1[1] == "string" 
                and var2[1] in ["int", "bool"])

        if (cond1 or cond2):
            raise ValueError(f"ERRO: Nao se pode operar {var1[1]} com {var2[1]}")

        if (self.value == '*'):
            return (var1[0] * var2[0], "int")
        elif (self.value == '/'):
            return (var1[0] // var2[0], "int")
        elif (self.value == '+'):
            return (var1[0] + var2[0], "int")
        elif (self.value == '-'):
            return (var1[0] - var2[0], "int")
        elif (self.value == '<'):
            return (bool(var1[0] < var2[0]), "bool")
        elif (self.value == '>'):
            return (bool(var1[0] > var2[0]), "bool")
        elif self.value == "==":
            return (bool(var1[0] == var2[0]), "bool")
        elif self.value == "&&":
            return (bool(var1[0] and var2[0]), "bool")
        elif self.value == "||":
            return (bool(var1[0] or var2[0]), "bool")

class UnOp(Node):
    def Evaluate(self, symbtable):
        if (self.value == '+'):
            return (+(self.children[0].Evaluate(symbtable)[0]), "int")
        elif (self.value == '-'):
            return (-(self.children[0].Evaluate(symbtable)[0]), "int")
        elif self.value == "!":
            return  (not bool((self.children[0].Evaluate(symbtable)[0])), "bool")

class IntVal(Node):
    def Evaluate(self, symbtable):
        return (int(self.value), "int")

class Identifier(Node):
    def __init__(self, val, type = None):
        super().__init__(val=val)
        self.type = type

    def Evaluate(self, symbtable):
        if (self.type != None):
            symbtable.declare(self.value, self.type)
        return symbtable.getter(self.value)

class AssignOp(Node):
    def Evaluate(self, symbtable):
        self.children[0].Evaluate(symbtable)
        varname = self.children[0].value
        type1 = symbtable.getter(varname)[1]

        newValue = self.children[1].Evaluate(symbtable)

        # Checa se sao tipos iguais no assign
        cond1 = (type1 in ["int", "bool"] 
                and newValue[1] == "string")
        cond2 = (type1 == "string" 
                and newValue[1] in ["int", "bool"])

        if cond1 or cond2:
            raise ValueError(f"ERRO: Nao podemos operar {type1} com {newValue[1]}")

        symbtable.setter(varname, newValue[0])

class PrintNode(Node):
    def Evaluate(self, symbtable):
        print(self.children[0].Evaluate(symbtable)[0])

class ReadNode(Node):
    def Evaluate(self, symbtable):
        return (int(input()), "int")

class CommandNode(Node):
    def Evaluate(self, symbtable):
        for x in self.children:
            if x.value == "return":
                return x.Evaluate(symbtable)
            else:
                x.Evaluate(symbtable)

class NoOp(Node):
    def __init__(self):
        pass

    def Evaluate(self, symbtable):
        pass

class WhileNode(Node):
    def Evaluate(self, symbtable):
        while bool(self.children[0].Evaluate(symbtable)[0]) == True:
            ret = self.children[1].Evaluate(symbtable)
            if ret != None:
                return ret
        
class IfNode(Node): 
    def Evaluate(self, symbtable):
        if (self.children[0].Evaluate(symbtable)[1] == "string"):
            raise ValueError("ERRO: IF nao pode ser com somente uma string")
        if bool(self.children[0].Evaluate(symbtable)[0]) == True:
            return self.children[1].Evaluate(symbtable) 
        # Checa se tem else e roda ele
        elif len(self.children) == 3:
            return self.children[2].Evaluate(symbtable) 

class BoolVal(Node):
    def Evaluate(self, symbtable):
        if(self.value == "true"):
            return (True, "bool")
        else:
            return (False, "bool")

class StringVal(Node):        
    def Evaluate(self,symbtable):
        return (self.value, "string")

class FuncDec(Node):
    def __init__(self, val, args, nodelist, type):
        super().__init__(val=val, nodelist=nodelist)
        self.type = type
        self.args = args

    #Funcoes sao tuplas (args, commands, tipo)
    def Evaluate(self, symbtable):
        # Seta funcao na symboltable de funcoes
        symbtable.setFunc(self.value, self.args, self.children, self.type)

class FuncCall(Node):
    def Evaluate(self, symbtable):
        # Pega a funcao da functable
        funcReference = symbtable.getFunc(self.value)

        # Pega o valor dos argumentos da funcao
        # cria novo symboltable, pra funcao
        localtable = SymbolTable()
        # Copia as funcoes para a symboltable criada para manter referencia as funcoes declaradas
        localtable.functiontable = symbtable.functiontable

        #Funcoes sao tuplas (args, commands, tipo)
        if len(self.children) == len(funcReference[0]):
            # declara todos os argumentos em argRes.
            for argReal, argDec in zip(self.children, funcReference[0]):
                argEval = argReal.Evaluate(symbtable)

                if argEval[1] != argDec.type:
                    raise ValueError(f"ERRO: Funcao leva variavel de tipo {argDec.type}, mas foi passado {argEval[1]}")

                # Declara com tipo
                localtable.declare(argDec.value, argEval[1])
                # Seta com valor
                localtable.setter(argDec.value, argEval[0])

        else:
            raise ValueError(f"ERRO: Funcao leva {len(funcReference[0])} argumentos, mas foram passados {len(self.children)}")

        # Func reference 2 guarda todos os commandos
        for command in funcReference[1].children:
            commandRet = command.Evaluate(localtable)

            # Checa se chegou no return e se nao eh um return de funcao chamada dentro ou return de variavel
            if (command.value == "return" or commandRet != None) and command.value not in localtable.functiontable.keys() and type(command) != Identifier:
                # Checa se valor retornado eh igual ao tipo da funcao
                if commandRet[1] != funcReference[2]:
                    raise ValueError(f"ERRO: Return da funcao eh de tipo {funcReference[2]}, mas tentou retornar tipo {commandRet[1]}")

                return commandRet


class ReturnNode(Node):
    def Evaluate(self, symbtable):
        return self.children.Evaluate(symbtable)


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
    def parseFuncDefBlock():
        #Parser.tokens.selectNext()

        functions = []
        #Pegar todas as funcoes enquanto na for o final da arquivo
        while(Parser.tokens.actual.type != "EOF"):

            # function type
            if (Parser.tokens.actual.type in types):
                functype = Parser.tokens.actual.type
                Parser.tokens.selectNext()
                # function name
                if (Parser.tokens.actual.type == "identifier"):
                    funcname = Parser.tokens.actual.value
                    funcargs = []
                    Parser.tokens.selectNext()
                    # function args if any
                    if (Parser.tokens.actual.type == "OPENBR"):
                        Parser.tokens.selectNext()
                        # Procurar se o proximo token n for um fecha parenteses, temos argumentos
                        # if (Parser.tokens.actual.type != "CLOSEBR"):
                        #     # Procurar se tem um argumento
                        #     if(Parser.tokens.actual.type in types):
                        #         vartype = Parser.tokens.actual.type
                        #         Parser.tokens.selectNext()
                        #         if (Parser.tokens.actual.type == "identifier"):
                        #             varname = Parser.tokens.actual.value
                        #         else:
                        #             raise ValueError(f"ERRO: Esperava-se um idetificador mas recebeu {Parser.tokens.actual.value}")
                        #         # Add argumento na lista
                        #         funcargs.append(Identifier(varname,vartype))
                        #         # Select Next espera virgula
                        #         Parser.tokens.selectNext()
                        #         # Depois de achar o primeiro arg, loopar enquanto existir virgulas para pegar os outros
                        #         while(Parser.tokens.actual.type == "COMMA" and Parser.tokens.actual.type != "CLOSEBR"):
                        #             # Select next espera tipo
                        #             Parser.tokens.selectNext()
                        #             # Se acha tipo
                        #             vartype = Parser.tokens.actual.type
                        #             # Select next espera identificador
                        #             Parser.tokens.selectNext()
                        #             if (Parser.tokens.actual.type == "identifier"):
                        #                 varname = Parser.tokens.actual.value
                        #                 # Prox token eh virgula ou fecha par
                        #                 Parser.tokens.selectNext()
                        #             else:
                        #                 raise ValueError(f"ERRO: Esperava-se um identificador mas recebeu {Parser.tokens.actual.value}")
                        #             # Add argumento na lista
                        #             funcargs.append(Identifier(varname,vartype))    

                        while(Parser.tokens.actual.type != "CLOSEBR"):
                            # Se acha tipo
                            vartype = Parser.tokens.actual.type
                            
                            # Select next espera identificador
                            Parser.tokens.selectNext()
                            if (Parser.tokens.actual.type == "identifier"):
                                varname = Parser.tokens.actual.value
                                # Prox token eh virgula ou fecha par
                                
                                # Add argumento na lista
                                funcargs.append(Identifier(varname,vartype)) 

                                Parser.tokens.selectNext()
                                if (Parser.tokens.actual.type == "COMMA"):
                                    Parser.tokens.selectNext()
                                    if (Parser.tokens.actual.type == "CLOSEBR"):
                                        raise ValueError("ERRO: Esperava-se uma algum valor depois da virgula")

                            else:
                                raise ValueError(f"ERRO: Esperava-se um identificador mas recebeu {Parser.tokens.actual.value}")

                        # Se nao tiver fechar parenteses depois de tudo erro
                        if (Parser.tokens.actual.type != "CLOSEBR"):
                            raise ValueError(f"ERRO: Esperava-se ), mas recebeu: {Parser.tokens.actual.value}")
                                
                    else: 
                        raise ValueError(f"ERRO: Sem ( depois de declaracao de {functype}")
                    
                    # Select next para entrar em parse command com token == {
                    Parser.tokens.selectNext()
                    functions.append(FuncDec(funcname, funcargs, Parser.parseCommand(), functype))
                                

                else:
                    raise ValueError(f"ERRO: Declaracao de funcao {functype} sem nome")

            else:
                raise ValueError("ERRO: Sem tipo para uma funcao")

        return functions

            

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


        if (Parser.tokens.actual.type in types):
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
            identName = Parser.tokens.actual.value
            Parser.tokens.selectNext()
            # Se for = faz atrbuicao
            if (Parser.tokens.actual.type == "ASSIGN"):
                result = Identifier(identName)

                result = AssignOp("=", [result, Parser.parseOrExpression()])

                if (Parser.tokens.actual.type == "ENDL"):
                    Parser.tokens.selectNext()
                    return result

                else:
                    raise ValueError(f"ERRO, esperava-se um fim de linha com ; mas recebeu {Parser.tokens.actual.value}")

            # Se for ( faz chamada de funcao
            elif(Parser.tokens.actual.type == "OPENBR"):
                args = []
                # Seleciona o token subsequente do (
                Parser.tokens.selectNext()
                # Se for diferente de um fecha paretenses, pegar todos os argumentos
                if (Parser.tokens.actual.type != "CLOSEBR"):
                    # volta
                    Parser.tokens.position -= len(Parser.tokens.actual.value)
                    # Pega primeiro argumento
                    # args.append(Parser.parseOrExpression())
                    # Loopar enquanto tiver virgula
                    # while(Parser.tokens.actual.type == "COMMA" and Parser.tokens.actual.type != "CLOSEBR"):
                    #     args.append(Parser.parseOrExpression())
                    
                    while(Parser.tokens.actual.type != "CLOSEBR"):
                        args.append(Parser.parseOrExpression())

                # Depois de tudo espera-se um ) e um ; em seguida
                if(Parser.tokens.actual.type == "CLOSEBR"):
                    result = FuncCall(identName, args)
                    Parser.tokens.selectNext()
                    if (Parser.tokens.actual.type == "ENDL"):
                        Parser.tokens.selectNext()
                        return result

                    else:
                        raise ValueError(f"ERRO, esperava-se um fim de linha com ; mas recebeu {Parser.tokens.actual.value}")
                
                else:
                    raise ValueError(f"ERRO, esperava-se um ) mas recebeu {Parser.tokens.actual.value}")
                
            else:
                raise ValueError(f"ERRO, esperava-se uma atribuicao com = ou um abre parenteses (, mas recebeu {Parser.tokens.actual.type}")

        
        elif (Parser.tokens.actual.type == "println"): 
            result = PrintNode(Parser.tokens.actual.value, [Parser.parseOrExpression()])
            
            if (Parser.tokens.actual.type == "ENDL"):
                Parser.tokens.selectNext()
                return result
                
            else:
                raise ValueError(f"ERRO, esperava-se um fim de linha com ; mas recebeu {Parser.tokens.actual.value}")

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
            return NoOp()

        # Se for return
        elif (Parser.tokens.actual.type == "return"):
            # Cria return node com a expressao seguinte
            result = ReturnNode(Parser.tokens.actual.value, Parser.parseOrExpression())
            # Token depois do return deve ser ;
            if (Parser.tokens.actual.type == "ENDL"):
                Parser.tokens.selectNext()
                return result
                
            else:
                raise ValueError(f"ERRO, esperava-se um fim de linha com ; mas recebeu {Parser.tokens.actual.value}")
        
        # se nao cair em nenhum dos casos chama BLOCK
        else:
            #Parser.tokens.selectNext()

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
            identName = Parser.tokens.actual.value
            Parser.tokens.selectNext()
            # Checa se eh chamada de funcao ou so uma variavel
            # Se for funcao faz igual no command
            if (Parser.tokens.actual.type == "OPENBR"):
                args = []
                # Seleciona o token subsequente do (
                # Se for diferente de um fecha paretenses, pegar todos os argumentos
                
                Parser.tokens.selectNext()
                if (Parser.tokens.actual.type != "CLOSEBR"):
                    Parser.tokens.position -= len(Parser.tokens.actual.value)

                    # Pega primeiro argumento
                    # args.append(Parser.parseOrExpression())
                    # , 4, 5, 6,
                    # Loopar enquanto tiver virgula

                    # while(Parser.tokens.actual.type == "COMMA" and Parser.tokens.actual.type != "CLOSEBR"):
                    #     args.append(Parser.parseOrExpression())
                    while(Parser.tokens.actual.type != "CLOSEBR"):
                        args.append(Parser.parseOrExpression())

                # Depois de tudo espera-se um ) 
                if(Parser.tokens.actual.type == "CLOSEBR"):
                    result = FuncCall(identName, args)
                    Parser.tokens.selectNext()
                    # ;
                else:
                    raise ValueError(f"ERRO, esperava-se um ) mas recebeu {Parser.tokens.actual.value}")
            # Se for variavel so cria node de variavel
            else:        
                result = Identifier(identName)

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
            raise Exception(f'ERRO: Token invalido em factor --> {Parser.tokens.actual.value}')

        return result

    @staticmethod
    def run(code):
        ST = SymbolTable()

        nocommentstring = PrePro.filter(code.rstrip('\n'))
        nocommentstring = nocommentstring.replace("\n", "")
        Parser.tokens = Parser().tokens(origem = nocommentstring) 

        # Select next pra pegar o primeiro token
        Parser.tokens.selectNext()

        compiled = Parser().parseFuncDefBlock()

        # Da evaluate nas funcoes declaradas
        for node in compiled:
            node.Evaluate(ST)

        # Adicionar uma chamada ao main para rodar o programa
        # Se nao tiver main da erro
        if ("main" in ST.functiontable.keys()):
            # compiled.append(ST.getFunc("main"))
            FuncCall("main", []).Evaluate(ST)
        else:
            raise ValueError("ERRO: nao existe main no programa")

        # select next pois o programa sai em uma fechadura de } 
        # Parser.tokens.selectNext()

        # if Parser.tokens.actual.type == "EOF":
        #     return compiled.Evaluate(ST)
        # else:
        #     raise Exception('ERRO')
    
class PrePro():
    @staticmethod
    def filter(code):
        nocommentstring = re.sub(re.compile("/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/",re.DOTALL ) ,"" ,code).replace("\t", "")
        return nocommentstring
        

def main():
    c_file = sys.argv[1]
    with open (c_file, 'r') as file:
        program = file.read()

    if(len(sys.argv) < 2):
        raise Exception("Nao foi passado argumento pro arquivo")



    Parser().run(program)


if __name__ == "__main__":
    main()
