# parser.py - análise sintática
#
# O que o parser faz: confere se os tokens estão na ordem certa
# e monta a árvore (AST) de cada comando.
#
# Ele entende só dois comandos (as regras estão em docs/gramatica.md):
#   Atribuicao:  x = a + 5;
#   Declaracao:  int a;    ou    int a = 10;
# Todo o resto (printf, if, while, funções...) ele ignora.

from arvore import No

# Tipos que começam uma declaração

TIPOS = {"int", "float", "char", "double"}

# Se depois de "tipo nome" vier um destes, não é uma declaração simples
# (é uma função, um parâmetro ou um vetor). O parser ignora.

NAO_E_DECLARACAO = {"(", ")", ",", "["}


# Um tipo de erro nosso (igual ao ErroLexico do lexer)
class ErroSintatico(Exception):
    pass