import re
from tokens import Token
from tab_simbol import Tab_Simbol

TIPOS_DADOS = {
    "char", "double", "float", "int", "long",
    "short", "signed", "unsigned", "void"
}

PALAVRAS_RESERVADAS = TIPOS_DADOS | {
    "auto", "break", "case", "const", "continue",
    "default", "do", "else", "enum", "extern",
    "for", "goto", "if", "register", "return",
    "sizeof", "static", "struct", "switch", "typedef",
    "union", "volatile", "while"
}

REGRAS_REGEX = [
    ("COMENTARIOS",  r'#.*|//.*|/\*[\s\S]*?\*/|/\*[\s\S]*'),
    ("ESPACOS",      r'[ \t\n]+'),
    ("STRING",       r'"([^"\\\n]|\\.)*"?|\'([^\'\\\n]|\\.)*\'?'),
    ("NUMERO",       r'\d+[a-zA-Z0-9_.]*'),
    ("OPERADOR",     r'\+\+|--|==|!=|<=|>=|&&|&|\|\||\||<<|>>|\+=|-=|\*=|/=|%=|\+|-|\*|/|%|=|<|>|!|~|\^|\?'),
    ("DELIMITADOR",  r'[;,()\{\}\[\]\.:]'),
    ("IDENTIFICADOR",r'[a-zA-Z_][a-zA-Z0-9_]*'),
]

class AnalisadorLexico:
    def __init__(self, codigo: str):
        self.codigo = codigo
        self.posicao = 0
        self.linha = 1
        self.coluna = 1
        self.tokens = []
        self.erros = []
        self.regras_compiladas = [
            (tipo, re.compile(padrao)) for tipo, padrao in REGRAS_REGEX
        ]

    def _registrar_erro(self, mensagem: str):
        self.erros.append(
            f"[ERRO LÉXICO] {mensagem} na linha {self.linha}, coluna {self.coluna}"
        )

    def _atualizar_posicao(self, lexema: str):
        quebras = lexema.count("\n")
        if quebras > 0:
            self.linha += quebras
            self.coluna = len(lexema.split("\n")[-1]) + 1
        else:
            self.coluna += len(lexema)
        self.posicao += len(lexema)

    def _aspas_fechadas(self, lexema: str, aspa: str) -> bool:
        if len(lexema) < 2 or not lexema.endswith(aspa):
            return False

        barras = 0
        indice = len(lexema) - 2
        while indice >= 1 and lexema[indice] == "\\":
            barras += 1
            indice -= 1

        return barras % 2 == 0

    def _validar_comentario(self, lexema: str):
        if lexema.startswith("/*"):
            if len(lexema) < 4 or not lexema.endswith("*/"):
                self._registrar_erro("Comentário de bloco não fechado")

    def _validar_string(self, lexema: str) -> bool:
        aspa = lexema[0]

        if not self._aspas_fechadas(lexema, aspa):
            self._registrar_erro(f"String ou caractere não fechado '{lexema}'")
            return False

        if aspa == "'":
            conteudo = lexema[1:-1]
            eh_escape = len(conteudo) == 2 and conteudo.startswith("\\")
            if len(conteudo) != 1 and not eh_escape:
                self._registrar_erro(f"Caractere inválido '{lexema}'")
                return False

        return True

    def _validar_numero(self, lexema: str) -> bool:
        for caractere in lexema:
            if caractere.isalpha() or caractere == "_":
                self._registrar_erro(f"Identificador inválido '{lexema}'")
                return False

        if lexema.count(".") > 1 or lexema.endswith("."):
            self._registrar_erro(f"Número malformado '{lexema}'")
            return False

        return True

    def _validar_lexema(self, tipo: str, lexema: str) -> bool:
        if tipo == "COMENTARIOS":
            self._validar_comentario(lexema)
            return False
        if tipo == "ESPACOS":
            return False
        if tipo == "STRING":
            return self._validar_string(lexema)
        if tipo == "NUMERO":
            return self._validar_numero(lexema)
        return True

    def analisar(self) -> list[Token]:
        while self.posicao < len(self.codigo):
            reconheceu = False

            for tipo, regex in self.regras_compiladas:
                match = regex.match(self.codigo, self.posicao)
                if match:
                    lexema = match.group(0)
                    gerar_token = self._validar_lexema(tipo, lexema)

                    if gerar_token:
                        tipo_token = tipo
                        if tipo == "IDENTIFICADOR" and lexema in PALAVRAS_RESERVADAS:
                            tipo_token = "PALAVRA_RESERVADA"
                        self.tokens.append(Token(tipo_token, lexema, self.linha, self.coluna))

                    self._atualizar_posicao(lexema)
                    reconheceu = True
                    break

            if not reconheceu:
                caractere_invalido = self.codigo[self.posicao]
                self._registrar_erro(f"Caractere inválido '{caractere_invalido}'")
                self._atualizar_posicao(caractere_invalido)

        self.tokens.append(Token("FIM_DE_ARQUIVO", "", self.linha, self.coluna))
        return self.tokens

def _descobrir_categoria(proximo: Token | None, dentro_parametros: bool, tipo_atual: str | None) -> str:
    if proximo and proximo.lexema == "(":
        return "Função"
    if dentro_parametros and tipo_atual:
        return "Parâmetro"
    return "Variável"

def _popular_tabela_simbolos(tokens: list[Token], tabela_simbolos: Tab_Simbol):
    dentro_parametros = False
    tipo_atual = None

    for i, token in enumerate(tokens):
        anterior = tokens[i - 1] if i > 0 else None
        proximo = tokens[i + 1] if i + 1 < len(tokens) else None

        if token.tipo == "DELIMITADOR":
            if token.lexema == "(" and anterior and anterior.tipo == "IDENTIFICADOR":
                dentro_parametros = True
            elif token.lexema == ")":
                dentro_parametros = False
                tipo_atual = None
            elif token.lexema in (";", "{", "}"):
                tipo_atual = None

        elif token.tipo == "PALAVRA_RESERVADA" and token.lexema in TIPOS_DADOS:
            tipo_atual = token.lexema

        elif token.tipo == "IDENTIFICADOR":
            categoria = _descobrir_categoria(proximo, dentro_parametros, tipo_atual)
            simbolo = tabela_simbolos.add(
                lexeme=token.lexema,
                category=categoria,
                tipo_token="IDENTIFICADOR",
                tipo_declarado=tipo_atual,
                linha=token.linha,
            )
            token.lexema = f"#{simbolo.ordem}"

def analisar_lexico(codigo: str, tabela_simbolos: Tab_Simbol | None = None) -> tuple[list[Token], list[str]]:
    if tabela_simbolos is None:
        tabela_simbolos = Tab_Simbol()

    analisador = AnalisadorLexico(codigo)
    tokens = analisador.analisar()
    _popular_tabela_simbolos(tokens, tabela_simbolos)
    return tokens, analisador.erros