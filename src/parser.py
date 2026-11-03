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


# Um tipo de erro (igual ao ErroLexico do lexer)
class ErroSintatico(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens   # a lista de tokens que o lexer entregou
        self.pos = 0           # posição do token da vez (começa no primeiro)
        self.erros = []        # erros encontrados

    def _atual(self):
        # O token da vez
        return self.tokens[self.pos]

    def _avancar(self):
        # Devolve o token da vez e passa para o próximo
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def _erro(self, esperado):
        # Monta o erro: "Esperado ';', encontrado 'a' na linha 3, coluna 1"
        token = self._atual()
        if token.tipo == "FIM_DE_ARQUIVO":
            encontrado = "fim do arquivo"
        else:
            encontrado = repr(token.lexema)
        return ErroSintatico(
            f"Esperado {esperado}, encontrado {encontrado} "
            f"na linha {token.linha}, coluna {token.coluna}"
        )

    def _esperar(self, texto):
        # Exige um token com este texto (";" ou ")"): se for ele, consome;
        # senão, dá erro
        if self._atual().lexema == texto:
            return self._avancar()
        raise self._erro(f"'{texto}'")