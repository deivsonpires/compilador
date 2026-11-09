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
    ("COMENTARIOS",  r'#.*|//.*|/\*[\s\S]*?\*/|[ \t]+'),
    ("ESPACOS",      r'\n'),
    ("STRING",       r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\''),
    ("NUMERO",       r'\d+(\.\d+)?'),
    ("OPERADOR",     r'\+\+|--|==|!=|<=|>=|&&|\|\||\+=|-=|\*=|/=|%=|\+|-|\*|/|%|=|<|>|!'),
    ("DELIMITADOR",  r'[;,()\{\}\[\]\.:]'),
    ("IDENTIFICADOR",r'[a-zA-Z_][a-zA-Z0-9_]*'),
]

# Mantemos a classe de exceção caso queira usar para erros fatais no futuro, 
# mas não a usaremos para caracteres inválidos agora.
class ErroLexico(Exception):
    pass


class AnalisadorLexico:
    def __init__(self, codigo: str):
        self.codigo = codigo
        self.posicao = 0
        self.linha = 1
        self.coluna = 1
        self.tokens = []
        self.erros = [] # <--- Nova lista para guardar os erros léxicos
        
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

    def analisar(self) -> list[Token]:
        while self.posicao < len(self.codigo):
            reconheceu = False

            for tipo, regex in self.regras_compiladas:
                match = regex.match(self.codigo, self.posicao)

                if match:
                    lexema = match.group(0)

                    if tipo == "COMENTARIOS":
                        self._atualizar_posicao(lexema)
                        reconheceu = True
                        break

                    if tipo == "ESPACOS":
                        self.linha += 1
                        self.coluna = 1
                        self.posicao += 1
                        reconheceu = True
                        break

                    if tipo == "IDENTIFICADOR":
                        tipo_token = "PALAVRA_RESERVADA" if lexema in PALAVRAS_RESERVADAS else "IDENTIFICADOR"
                        self.tokens.append(Token(tipo_token, lexema, self.linha, self.coluna))
                    else:
                        self.tokens.append(Token(tipo, lexema, self.linha, self.coluna))

                    self._atualizar_posicao(lexema)
                    reconheceu = True
                    break

            if not reconheceu:
                # RECUPERAÇÃO DE ERRO:
                caractere_invalido = self.codigo[self.posicao]
                
                # 1. Guarda a mensagem na lista de erros em vez de dar 'raise'
                self.erros.append(f"[ERRO LÉXICO] Caractere inválido '{caractere_invalido}' na linha {self.linha}, coluna {self.coluna}")
                
                # 2. Ignora o caractere inválido avançando o cursor em 1
                self.posicao += 1
                self.coluna += 1


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
                token_type="IDENTIFICADOR",
                declared_type=tipo_atual,
            )

            if proximo and proximo.lexema != ",":
                tipo_atual = None


# ATENÇÃO: A função principal agora retorna uma tupla com (tokens, erros)
def analisar_lexico(codigo: str, tabela_simbolos: Tab_Simbol | None = None) -> tuple[list[Token], list[str]]:
    if tabela_simbolos is None:
        tabela_simbolos = Tab_Simbol()

    analisador = AnalisadorLexico(codigo)
    tokens = analisador.analisar()
    _popular_tabela_simbolos(tokens, tabela_simbolos)
    
    # Retorna tanto os tokens quanto a lista de erros capturados
    return tokens, analisador.erros


lexer = analisar_lexico