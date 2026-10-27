# Gramática do analisador sintático

Notação BNF. `*` = zero ou mais, `[ ]` = opcional, `|` = ou.

```
<Programa>    ::= <Comando>* EOF
<Comando>     ::= <Declaracao> | <Atribuicao>
<Declaracao>  ::= <tipo> ID [ "=" <Expressao> ] ";"
<Atribuicao>  ::= ID "=" <Expressao> ";"
<Expressao>   ::= <Termo> ( ("+" | "-") <Termo> )*
<Termo>       ::= <Fator> ( ("*" | "/" | "%") <Fator> )*
<Fator>       ::= ID | NUM | CHAR | STRING | "(" <Expressao> ")"
<tipo>        ::= "int" | "float" | "char" | "double"
```