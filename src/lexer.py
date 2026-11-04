from tokens import Token
from tab_simbol import Tab_Simbol


# ---------------------------------------------------------------------------
# Conjuntos da linguagem C
# ---------------------------------------------------------------------------

TIPOS_DADOS = {"int", "float", "char", "double", "void"}

PALAVRAS_CHAVE = TIPOS_DADOS | {
    "if", "else", "while", "for", "return",
    "break", "continue", "struct", "switch",
    "case", "default", "do", "sizeof",
}

OPERADORES = {
    "++", "--", "==", "!=", "<=", ">=", "&&", "||",
    "+=", "-=", "*=", "/=", "%=",
    "+", "-", "*", "/", "%", "=", "<", ">", "!",
}

DELIMITADORES = {";", ",", "(", ")", "{", "}", "[", "]", ".", "#", ":"}


class ErroLexico(Exception):
    """Exceção levantada para erros durante a análise léxica."""
    pass


# ---------------------------------------------------------------------------
# Analisador léxico
# ---------------------------------------------------------------------------

class AnalisadorLexico:
    """Percorre o código caractere a caractere e gera a lista de tokens."""

    def __init__(self, codigo: str):
        self.codigo = codigo
        self.indice = 0
        self.linha = 1
        self.coluna = 1
        self.tokens = []

    # --- Utilitários de navegação -----------------------------------------

    def _fim(self) -> bool:
        return self.indice >= len(self.codigo)

    def _atual(self) -> str:
        """Caractere atual ('' se chegou ao fim)."""
        return "" if self._fim() else self.codigo[self.indice]

    def _proximo(self) -> str:
        """Caractere seguinte ao atual ('' se não existir)."""
        posicao = self.indice + 1
        return self.codigo[posicao] if posicao < len(self.codigo) else ""

    def _comeca_com(self, texto: str) -> bool:
        return self.codigo.startswith(texto, self.indice)

    def _avancar(self, quantidade: int = 1):
        """Avança N caracteres, atualizando linha e coluna."""
        for _ in range(quantidade):
            if self._fim():
                return
            if self.codigo[self.indice] == "\n":
                self.linha += 1
                self.coluna = 1
            else:
                self.coluna += 1
            self.indice += 1

    def _adicionar_token(self, tipo: str, lexema: str, linha: int, coluna: int):
        self.tokens.append(Token(tipo, lexema, linha, coluna))

    # --- Leitores de cada tipo de token ------------------------------------
    # Cada leitor devolve True se reconheceu e consumiu algo, False caso contrário.

    def _ler_espacos(self) -> bool:
        if not self._atual().isspace():
            return False
        self._avancar()
        return True

    def _ler_comentario_linha(self) -> bool:
        if not self._comeca_com("//"):
            return False
        while not self._fim() and self._atual() != "\n":
            self._avancar()
        return True

    def _ler_comentario_bloco(self) -> bool:
        if not self._comeca_com("/*"):
            return False

        linha_inicial, coluna_inicial = self.linha, self.coluna
        self._avancar(2)

        while not self._fim() and not self._comeca_com("*/"):
            self._avancar()

        if self._fim():
            raise ErroLexico(
                f"Comentário de bloco não terminado na linha {linha_inicial}, coluna {coluna_inicial}"
            )

        self._avancar(2)
        return True

    def _ler_identificador(self) -> bool:
        caractere = self._atual()
        if not (caractere.isalpha() or caractere == "_"):
            return False

        linha_inicial, coluna_inicial = self.linha, self.coluna
        inicio = self.indice

        while self._atual().isalnum() or self._atual() == "_":
            self._avancar()

        valor = self.codigo[inicio:self.indice]
        tipo = "PALAVRA_CHAVE" if valor in PALAVRAS_CHAVE else "IDENTIFICADOR"
        self._adicionar_token(tipo, valor, linha_inicial, coluna_inicial)
        return True

    def _consumir_digitos(self):
        while self._atual().isdigit():
            self._avancar()

    def _ler_numero(self) -> bool:
        if not self._atual().isdigit():
            return False

        linha_inicial, coluna_inicial = self.linha, self.coluna
        inicio = self.indice

        self._consumir_digitos()

        # Parte decimal (só se houver dígito depois do ponto)
        if self._atual() == "." and self._proximo().isdigit():
            self._avancar()
            self._consumir_digitos()

        self._adicionar_token("NÚMERO", self.codigo[inicio:self.indice], linha_inicial, coluna_inicial)
        return True

    def _ler_string(self) -> bool:
        aspas = self._atual()
        if aspas not in ('"', "'"):
            return False

        linha_inicial, coluna_inicial = self.linha, self.coluna
        inicio = self.indice
        self._avancar()  # aspas de abertura

        fechado = False
        while not self._fim():
            caractere = self._atual()
            if caractere == "\\":
                self._avancar(2)  # pula o caractere escapado
            elif caractere == aspas:
                self._avancar()
                fechado = True
                break
            elif caractere == "\n":
                break
            else:
                self._avancar()

        if not fechado:
            raise ErroLexico(
                f"Literal não terminado na linha {linha_inicial}, coluna {coluna_inicial}"
            )

        self._adicionar_token("STRING", self.codigo[inicio:self.indice], linha_inicial, coluna_inicial)
        return True

    def _ler_operador(self) -> bool:
        # Tenta primeiro o operador de 2 caracteres (ex: "=="), depois o de 1 (ex: "=")
        for tamanho in (2, 1):
            candidato = self.codigo[self.indice:self.indice + tamanho]
            if candidato in OPERADORES:
                self._adicionar_token("OPERADOR", candidato, self.linha, self.coluna)
                self._avancar(len(candidato))
                return True
        return False

    def _ler_delimitador(self) -> bool:
        caractere = self._atual()
        if caractere not in DELIMITADORES:
            return False

        self._adicionar_token("DELIMITADOR", caractere, self.linha, self.coluna)
        self._avancar()
        return True

    # --- Execução ----------------------------------------------------------

    def analisar(self) -> list[Token]:
        # A ordem importa: comentários vêm antes dos operadores ("/" vs "//")
        leitores = [
            self._ler_espacos,
            self._ler_comentario_linha,
            self._ler_comentario_bloco,
            self._ler_identificador,
            self._ler_numero,
            self._ler_string,
            self._ler_operador,
            self._ler_delimitador,
        ]

        while not self._fim():
            for leitor in leitores:
                if leitor():
                    break
            else:  # nenhum leitor reconheceu o caractere
                raise ErroLexico(
                    f"Caractere inválido {self._atual()!r} na linha {self.linha}, coluna {self.coluna}"
                )

        self._adicionar_token("FIM_DE_ARQUIVO", "", self.linha, self.coluna)
        return self.tokens


# ---------------------------------------------------------------------------
# Tabela de símbolos
# ---------------------------------------------------------------------------

def _classificar_identificador(token, proximo, em_diretiva, dentro_parametros, tipo_atual):
    """Devolve (categoria, tipo_declarado) de um identificador.

    O tipo_declarado é None quando não há tipo conhecido naquele ponto.
    """
    if em_diretiva:
        categoria = "Diretiva" if token.lexema == "include" else "Biblioteca"
        return categoria, None
    if proximo and proximo.lexema == "(":
        return "Função", tipo_atual
    if dentro_parametros and tipo_atual:
        return "Parâmetro", tipo_atual
    return "Variável", tipo_atual


def _popular_tabela_simbolos(tokens: list[Token], tabela_simbolos: Tab_Simbol):
    """Classifica palavras reservadas e identificadores e os adiciona à tabela."""
    dentro_parametros = False
    tipo_atual = None
    linha_diretiva = -1

    for i, token in enumerate(tokens):
        anterior = tokens[i - 1] if i > 0 else None
        proximo = tokens[i + 1] if i + 1 < len(tokens) else None

        if token.tipo == "DELIMITADOR":
            if token.lexema == "#":
                linha_diretiva = token.linha
            elif token.lexema == "(" and anterior and anterior.tipo == "IDENTIFICADOR":
                dentro_parametros = True
            elif token.lexema == ")":
                dentro_parametros = False
                tipo_atual = None
            elif token.lexema == ";":
                tipo_atual = None

        elif token.tipo == "PALAVRA_CHAVE":
            # Palavras reservadas NÃO entram na tabela; só guardamos o tipo
            # (ex: `int`) para classificar o identificador que vem depois.
            if token.lexema in TIPOS_DADOS:
                tipo_atual = token.lexema

        elif token.tipo == "IDENTIFICADOR":
            em_diretiva = token.linha == linha_diretiva
            categoria, tipo_declarado = _classificar_identificador(
                token, proximo, em_diretiva, dentro_parametros, tipo_atual
            )

            tabela_simbolos.add(
                lexeme=token.lexema,
                category=categoria,
                token_type="IDENTIFICADOR",
                declared_type=tipo_declarado,
            )

            # Mantém o tipo só se vier vírgula (ex: `int a, b;`)
            if proximo and proximo.lexema != ",":
                tipo_atual = None


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

def analisar_lexico(codigo: str, tabela_simbolos: Tab_Simbol | None = None) -> list[Token]:
    """Executa a análise léxica do código C e preenche a Tabela de Símbolos."""
    if tabela_simbolos is None:
        tabela_simbolos = Tab_Simbol()

    tokens = AnalisadorLexico(codigo).analisar()
    _popular_tabela_simbolos(tokens, tabela_simbolos)
    return tokens


# Aliases para compatibilidade
LexicalError = ErroLexico
lexer = analisar_lexico