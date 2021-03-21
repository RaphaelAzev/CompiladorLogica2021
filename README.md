# CompiladorLogica2021
Compilador para a matéria Lógica da Computação 

![Image of DS](DS.png)

Para rodar o programa seguir o exemplo: python3 calculadora.py '3 + 3'

EBNF:

EXPRESSION = TERM, {("+" | "-"), TERM} ;

TERM = FACTOR, {("*" | "/"), FACTOR} ;

FACTOR = ("+" | "-") FACTOR | "(" EXPRESSION ")" | number ;

NUMBER = DIGIT, {DIGIT} ;

DIGIT = 0 | 1 | 2 | 3 ... | 9 ;
