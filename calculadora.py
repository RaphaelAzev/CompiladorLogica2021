import sys

def get_type(token):
    if token.isdigit() == True:
        return "INT"
    elif token == "+":
        return "PLUS"
    elif token == "-":
        return "MINUS"
    elif token == " ":
        return "SPACE"

def main():
    operation = sys.argv[1]
    #operation = '3+3+3'
    if operation == '':
        raise ValueError('ERRO: nao existe operacao')
    result = 0
    number = ""
    x = 0
    op_flag = "PLUS"
    while x in range(len(operation)):
        
        while (x != len(operation) and get_type(operation[x]) == "INT"):
            number = number + operation[x]
            x += 1
            while (x != len(operation) and get_type(operation[x]) == "SPACE"):
                x += 1
                if x != len(operation) and get_type(operation[x]) == "INT":
                    raise ValueError('ERRO numeros com espaco entre eles sem operadores')


        while (x != len(operation) and get_type(operation[x]) == "SPACE"):
            x += 1
    

        if (number != "" and op_flag == "PLUS"):
            result += int(number)
            number = ""
            op_flag = None
        elif (number != "" and op_flag == "MINUS"):
            result -= int(number)
            number = ""
            op_flag = None

        if x != len(operation) and get_type(operation[x]) == "PLUS":
            if (op_flag != None and number == ""):
                raise ValueError('ERRO: operadores em sequencia')
            op_flag = "PLUS"
            x += 1
        elif x != len(operation) and get_type(operation[x]) == "MINUS":
            if (op_flag != None and number == ""):
                raise ValueError('ERRO: operadores em sequencia')
            op_flag = "MINUS"
            x += 1

    if (op_flag != None):
        raise ValueError('ERRO: Operador nao consumido')

    print(result)
        
if __name__ == "__main__":
    main()
    
