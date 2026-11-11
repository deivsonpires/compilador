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

    def analisar_programa(self):
        # Lê comando por comando até o fim do arquivo
        raiz = No("Programa")
        while self._atual().tipo != "FIM_DE_ARQUIVO":
            try:
                comando = self._comando()
            except ErroSintatico as erro:
                self.erros.append(erro)   # guarda o erro...
                break                     # ...e para por aqui
            if comando is not None:
                raiz.filhos.append(comando)
        return raiz

    def _comando(self):
        # Descobre que comando começa agora, olhando os próximos tokens
        token = self._atual()
        proximo = self.tokens[self.pos + 1]

        # "tipo nome ..." -> declaração
        if (token.tipo == "PALAVRA_RESERVADA" and token.lexema in TIPOS
                and proximo.tipo == "IDENTIFICADOR"
                and self.tokens[self.pos + 2].lexema not in NAO_E_DECLARACAO):
            return self._declaracao()

        # "nome =" -> atribuição
        if token.tipo == "IDENTIFICADOR" and proximo.lexema == "=":
            return self._atribuicao()

        # Qualquer outra coisa (printf, if, funções...) não é da nossa
        # gramática: pula este token e segue
        self._avancar()
        return None    

    
    

    def _atribuicao(self):
        # Atribuicao: ID "=" Expressao ";"
        nome = self._avancar()
        igual = self._avancar()   # já sabemos que é o "="
        expressao = self._expressao()
        self._esperar(";")
        return No("Atribuicao", linha=nome.linha, filhos=[
            No("ID", nome.lexema, linha=nome.linha),
            No("OP_ATRIB", igual.lexema, linha=igual.linha),
            expressao,
        ])

    def _declaracao(self):
        # Declaracao: tipo ID [ "=" Expressao ] ";"
        tipo = self._avancar()
        nome = self._avancar()    # já sabemos que é um identificador
        no = No("Declaracao", linha=tipo.linha, filhos=[
            No("TIPO", tipo.lexema, linha=tipo.linha),
            No("ID", nome.lexema, linha=nome.linha),
        ])
        # Parte opcional: só lê "= valor" se o próximo token for "="
        if self._atual().lexema == "=":
            igual = self._avancar()
            no.filhos.append(No("OP_ATRIB", igual.lexema, linha=igual.linha))
            no.filhos.append(self._expressao())
        self._esperar(";")
        return no


    def _expressao(self):
        # Expressao: termo ( ("+" | "-") termo )*
        # Pega o primeiro termo. Enquanto vier + ou -, junta com o próximo.
        esquerda = self._termo()
        while self._atual().lexema in ("+", "-"):
            operador = self._avancar()
            direita = self._termo()
            esquerda = No("Expressao", operador.lexema, [esquerda, direita], operador.linha)
        return esquerda

    def _termo(self):
        # termo: ID | NUM | STRING | chamada de função
        token = self._atual()
        if token.tipo == "IDENTIFICADOR":
            self._avancar()
            if self._atual().lexema == "(":
                return self._chamada(token)
            return No("ID", token.lexema, linha=token.linha)
        if token.tipo == "NUMERO":
            self._avancar()
            return No("NUM", token.lexema, linha=token.linha)
        if token.tipo == "STRING":
            self._avancar()
            return No("STRING", token.lexema, linha=token.linha)
        raise self._erro("identificador ou número")

    def _chamada(self, nome):
        # Chamada de função: nome ( argumento , argumento ... )
        self._avancar()                    # consome o "("
        chamada = No("Chamada", nome.lexema, linha=nome.linha)
        if self._atual().lexema != ")":    # tem argumentos
            chamada.filhos.append(self._expressao())
            while self._atual().lexema == ",":
                self._avancar()
                chamada.filhos.append(self._expressao())
        self._esperar(")")
        return chamada



def analisar_sintatico(tokens):
    # Função que o main.py chama. Devolve (árvore, lista de erros).
    parser = Parser(tokens)
    arvore = parser.analisar_programa()
    return arvore, parser.erros

