# Gramática do analisador sintático

Notação BNF. `*` = zero ou mais, `[ ]` = opcional, `|` = ou.

O lexer apresenta os tokens pelas categorias gerais:
`PALAVRA_CHAVE`, `DELIMITADOR`, `IDENTIFICADOR`, `STRING`, `NÚMERO` e
`OPERADOR_LÓGICO`. Literais de caractere e de texto pertencem à categoria
`STRING`.

```
<Programa>    ::= <Comando>* EOF
<Comando>     ::= <Declaracao> | <Atribuicao>
<Declaracao>  ::= <tipo> ID [ "=" <Expressao> ] ";"
<Atribuicao>  ::= ID "=" <Expressao> ";"
<Expressao>   ::= <Termo> ( ("+" | "-") <Termo> )*
<Termo>       ::= <Fator> ( ("*" | "/" | "%") <Fator> )*
<Fator>       ::= IDENTIFICADOR | NÚMERO | STRING | "(" <Expressao> ")"
<tipo>        ::= "int" | "float" | "char" | "double"
```