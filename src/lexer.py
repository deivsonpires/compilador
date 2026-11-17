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
    ("COMENTARIOS",  r'#.*|//.*|/\*[\s\S]*?\*/'),
    ("ESPACOS",      r'[ \t\n]+'),
    ("STRING",       r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\''),
    ("NUMERO",       r'\d+(\.\d+)?'),
    ("OPERADOR",     r'\+\+|--|==|!=|<=|>=|&&|&|\|\||\+=|-=|\*=|/=|%=|\+|-|\*|/|%|=|<|>|!'),
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

    def _atualizar_posicao(self, lexema: str):
        quebras = lexema.count("\n")
        if quebras > 0:
            self.linha += quebras
            self.coluna = len(lexema.split("\n")[-1]) + 1
        else:
            self.coluna += len(lexema)
        self.posicao += len(lexema)

    def _ler_identificador_invalido(self, lexema_numero: str):
        fim = self.posicao + len(lexema_numero)
        if fim >= len(self.codigo):
            return None
        proximo = self.codigo[fim]
        if not (proximo.isalpha() or proximo == "_"):
            return None
        while fim < len(self.codigo) and (self.codigo[fim].isalnum() or self.codigo[fim] == "_"):
            fim += 1
        return self.codigo[self.posicao:fim]

    def analisar(self) -> list[Token]:
        while self.posicao < len(self.codigo):
            reconheceu = False
            for tipo, regex in self.regras_compiladas:
                match = regex.match(self.codigo, self.posicao)
                if match:
                    lexema = match.group(0)
                    if tipo == "NUMERO":
                        invalido = self._ler_identificador_invalido(lexema)
                        if invalido is not None:
                            self.erros.append(f"[ERRO LÉXICO] Identificador inválido '{invalido}' na linha {self.linha}, coluna {self.coluna}")
                            self._atualizar_posicao(invalido)
                            reconheceu = True
                            break
                    if tipo not in ("COMENTARIOS", "ESPACOS"):
                        tipo_token = "PALAVRA_RESERVADA" if tipo == "IDENTIFICADOR" and lexema in PALAVRAS_RESERVADAS else tipo
                        self.tokens.append(Token(tipo_token, lexema, self.linha, self.coluna))
                    self._atualizar_posicao(lexema)
                    reconheceu = True
                    break
            if not reconheceu:
                caractere_invalido = self.codigo[self.posicao]
                self.erros.append(f"[ERRO LÉXICO] Caractere inválido '{caractere_invalido}' na linha {self.linha}, coluna {self.coluna}")
                self._atualizar_posicao(caractere_invalido)
        self.tokens.append(Token("FIM_DE_ARQUIVO", "", self.linha, self.coluna))
        return self.tokens

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
            elif token.lexema == ";":
                tipo_atual = None
        elif token.tipo == "PALAVRA_RESERVADA":
            if token.lexema in TIPOS_DADOS:
                tipo_atual = token.lexema
        elif token.tipo == "IDENTIFICADOR":
            if proximo and proximo.lexema == "(":
                categoria = "Função"
            elif dentro_parametros and tipo_atual:
                categoria = "Parâmetro"
            else:
                categoria = "Variável"
            tabela_simbolos.add(
                lexeme=token.lexema,
                category=categoria,
                tipo_token="IDENTIFICADOR",
                tipo_declarado=tipo_atual,
            )
            if proximo and proximo.lexema != ",":
                tipo_atual = None

def analisar_lexico(codigo: str, tabela_simbolos: Tab_Simbol | None = None) -> tuple[list[Token], list[str]]:
    if tabela_simbolos is None:
        tabela_simbolos = Tab_Simbol()
    analisador = AnalisadorLexico(codigo)
    tokens = analisador.analisar()
    _popular_tabela_simbolos(tokens, tabela_simbolos)
    return tokens, analisador.erros