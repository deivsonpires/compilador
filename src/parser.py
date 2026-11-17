from arvore import No
from lexer import TIPOS_DADOS

NAO_E_DECLARACAO = {"(", ")", ",", "["}

class ErroSintatico(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.erros = []

    def _atual(self):
        return self.tokens[self.pos]

    def _avancar(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def _erro(self, esperado):
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
        if self._atual().lexema == texto:
            return self._avancar()
        raise self._erro(f"'{texto}'")

    def analisar_programa(self):
        raiz = No("Programa")
        while self._atual().tipo != "FIM_DE_ARQUIVO":
            try:
                comando = self._comando()
            except ErroSintatico as erro:
                self.erros.append(erro)
                continue
            if comando is not None:
                raiz.filhos.append(comando)
        return raiz

    def _comando(self):
        token = self._atual()
        proximo = self.tokens[self.pos + 1]
        if (token.tipo == "PALAVRA_RESERVADA" and token.lexema in TIPOS_DADOS
                and proximo.tipo == "IDENTIFICADOR"
                and self.tokens[self.pos + 2].lexema not in NAO_E_DECLARACAO):
            return self._declaracao()
        if token.tipo == "IDENTIFICADOR" and proximo.lexema == "=":
            return self._atribuicao()
        if token.lexema == "return":
            return self._retorno()
        if token.tipo == "IDENTIFICADOR" and proximo.lexema == "(":
            argumento = self.tokens[self.pos + 2]
            if argumento.tipo == "PALAVRA_RESERVADA" and argumento.lexema in TIPOS_DADOS:
                self._avancar()
                return None
            return self._chamada_como_comando()
        self._avancar()
        return None

    def _retorno(self):
        self._avancar()
        if self._atual().lexema not in (";", "}") and self._atual().tipo != "FIM_DE_ARQUIVO":
            self._expressao()
        self._esperar(";")
        return None

    def _chamada_como_comando(self):
        chamada = self._avancar()
        self._chamada(chamada)
        if self._atual().lexema == "{":
            return None
        self._esperar(";")
        return None

    def _atribuicao(self):
        nome = self._avancar()
        igual = self._avancar()
        expressao = self._expressao()
        self._esperar(";")
        return No("Atribuicao", linha=nome.linha, filhos=[
            No("ID", nome.lexema, linha=nome.linha),
            No("OP_ATRIB", igual.lexema, linha=igual.linha),
            expressao,
        ])

    def _declaracao(self):
        tipo = self._avancar()
        nome = self._avancar()
        no = No("Declaracao", linha=tipo.linha, filhos=[
            No("TIPO", tipo.lexema, linha=tipo.linha),
            No("ID", nome.lexema, linha=nome.linha),
        ])
        if self._atual().lexema == "=":
            igual = self._avancar()
            no.filhos.append(No("OP_ATRIB", igual.lexema, linha=igual.linha))
            no.filhos.append(self._expressao())
        self._esperar(";")
        return no

    def _expressao(self):
        esquerda = self._multiplicacao()
        while self._atual().lexema in ("+", "-"):
            operador = self._avancar()
            direita = self._multiplicacao()
            esquerda = No("Expressao", operador.lexema, [esquerda, direita], operador.linha)
        return esquerda

    def _multiplicacao(self):
        esquerda = self._termo()
        while self._atual().lexema in ("*", "/", "%"):
            operador = self._avancar()
            direita = self._termo()
            esquerda = No("Expressao", operador.lexema, [esquerda, direita], operador.linha)
        return esquerda

    def _termo(self):
        token = self._atual()
        if token.lexema == "-" and self.tokens[self.pos + 1].tipo == "NUMERO":
            self._avancar()
            numero = self._avancar()
            return No("NUM", "-" + numero.lexema, linha=token.linha)
        if token.lexema == "(":
            self._avancar()
            expr = self._expressao()
            self._esperar(")")
            return expr
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
        raise self._erro("identificador, número ou '('")

    def _chamada(self, nome):
        self._avancar()
        chamada = No("Chamada", nome.lexema, linha=nome.linha)
        if self._atual().lexema != ")":
            chamada.filhos.append(self._expressao())
            while self._atual().lexema == ",":
                self._avancar()
                chamada.filhos.append(self._expressao())
        self._esperar(")")
        return chamada

def analisar_sintatico(tokens):
    parser = Parser(tokens)
    arvore = parser.analisar_programa()
    return arvore, parser.erros