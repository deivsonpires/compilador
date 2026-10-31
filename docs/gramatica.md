# Gramática: o que o parser aceita
O parser entende dois comandos:
atribuição e declaração. O resto (printf, if, while, funções) ele ignora.

## Como ler a BNF
-> `::=` quer dizer "é formado por"
-> `[ ]` quer dizer "opcional"
-> `*` quer dizer "pode repetir"
-> `|` quer dizer "ou"

## Atribuição
-> Um nome, o `=`, uma conta e o `;`
-> Exemplo: `x = a + 5;`
-> `<Atribuicao> ::= ID "=" <Expressao> ";"`

## Declaração
-> Um tipo, um nome e, se quiser, um valor inicial
-> Exemplos: `int b;` e `int a = 10;`
-> `<Declaracao> ::= <tipo> ID [ "=" <Expressao> ] ";"`

## Expressão (a conta)
-> Termos ligados por `+` ou `-`
-> Exemplos: `a + 5` e `a + b - 3`
-> O barema mostra um só `+` ou `-`. O nosso aceita vários.
-> `<Expressao> ::= <termo> ( ("+" | "-") <termo> )*`

## Termo
-> Um nome, um número, um texto ou uma chamada de função
-> `<termo> ::= ID | NUM | STRING | <chamada>`

## Chamada de função
-> O nome, `(`, os argumentos separados por vírgula e `)`
-> Exemplo: `soma(a, b)`
-> `<chamada> ::= ID "(" [ <Expressao> ( "," <Expressao> )* ] ")"`

## Tipo
-> `int`, `float`, `char` ou `double`
-> `<tipo> ::= "int" | "float" | "char" | "double"`