try:
    from .tokens import Token
    from .tab_simbol import Tab_Simbol
except ImportError:  # pragma: no cover - compatibilidade ao executar o script diretamente
    from tokens import Token
    from tab_simbol import Tab_Simbol


# Palavras-chave padrão da linguagem C
PALAVRAS_CHAVE = {
    "int", "float", "char", "double", "void",
    "if", "else", "while", "for", "return",
    "break", "continue", "struct", "switch",
    "case", "default", "do", "sizeof",
}

# Tipos primitivos de dados
TIPOS_DADOS = {"int", "float", "char", "double", "void"}

# Operadores padrão da linguagem C (aritméticos, relacionais, lógicos e atribuição)
OPERADORES = {
    "++", "--", "==", "!=", "<=", ">=", "&&", "||",
    "+=", "-=", "*=", "/=", "%=",
    "+", "-", "*", "/", "%", "=", "<", ">", "!",
}

# Delimitadores padrão
DELIMITADORES = {
    ";", ",", "(", ")", "{", "}", "[", "]", ".", "#", ":",
}


class ErroLexico(Exception):
    """Exceção levantada para erros durante a análise léxica."""
    pass


def _popular_tabela_simbolos(tokens: list[Token], tabela_simbolos: Tab_Simbol):
    """Classifica identificadores e palavras reservadas para popular a tabela de símbolos."""
    dentro_parametros = False
    tipo_atual = None
    linha_diretiva = -1

    for i, token in enumerate(tokens):
        # Reconhecimento de diretivas de pré-processador (ex: #include <stdio.h>)
        if token.tipo == "DELIMITADOR" and token.lexema == "#":
            linha_diretiva = token.linha
            continue

        if token.linha != linha_diretiva:
            linha_diretiva = -1

        if token.tipo == "PALAVRA_CHAVE":
            if token.lexema in TIPOS_DADOS:
                tipo_atual = token.lexema

            tabela_simbolos.add(
                lexeme=token.lexema,
                category="Palavra Reservada",
                token_type="PALAVRA_CHAVE",
                declared_type=token.lexema if token.lexema in TIPOS_DADOS else "-",
            )

        elif token.tipo == "IDENTIFICADOR":
            proximo = tokens[i + 1] if i + 1 < len(tokens) else None

            if token.linha == linha_diretiva:
                tipo_lex = "Diretiva" if token.lexema == "include" else "Biblioteca"
                tipo_dec = "-"
            elif proximo and proximo.lexema == "(":
                tipo_lex = "Função"
                tipo_dec = tipo_atual if tipo_atual else "-"
            elif dentro_parametros and tipo_atual:
                tipo_lex = "Parâmetro"
                tipo_dec = tipo_atual
            elif tipo_atual:
                tipo_lex = "Variável"
                tipo_dec = tipo_atual
            else:
                tipo_lex = "Variável"
                tipo_dec = "-"

            tabela_simbolos.add(
                lexeme=token.lexema,
                category=tipo_lex,
                token_type="IDENTIFICADOR",
                declared_type=tipo_dec,
            )

            # Se o próximo não for vírgula (que mantém tipo em `int a, b;`), limpa tipo_atual
            if proximo and proximo.lexema != ",":
                tipo_atual = None

        elif token.tipo == "DELIMITADOR":
            if token.lexema == "(":
                anterior = tokens[i - 1] if i > 0 else None
                if anterior and anterior.tipo == "IDENTIFICADOR":
                    dentro_parametros = True
            elif token.lexema == ")":
                dentro_parametros = False
                tipo_atual = None
            elif token.lexema == ";":
                tipo_atual = None


def analisar_lexico(codigo: str, tabela_simbolos: Tab_Simbol | None = None) -> list[Token]:
    """Executa a análise léxica do código-fonte em C.
    
    Identifica tokens (PALAVRA_CHAVE, IDENTIFICADOR, OPERADOR, DELIMITADOR,
    NÚMERO, STRING e FIM_DE_ARQUIVO) e preenche a Tabela de Símbolos.
    """
    if tabela_simbolos is None:
        tabela_simbolos = Tab_Simbol()

    tokens = []
    indice = 0
    linha = 1
    coluna = 1
    tamanho = len(codigo)

    while indice < tamanho:
        caractere = codigo[indice]

        # 1. Espaços em branco e quebras de linha
        if caractere.isspace():
            if caractere == "\n":
                linha += 1
                coluna = 1
            else:
                coluna += 1
            indice += 1
            continue

        linha_inicial = linha
        coluna_inicial = coluna

        # 2. Comentários de linha única (//)
        if codigo.startswith("//", indice):
            while indice < tamanho and codigo[indice] != "\n":
                indice += 1
                coluna += 1
            continue

        # 3. Comentários de bloco (/* ... */)
        if codigo.startswith("/*", indice):
            indice += 2
            coluna += 2
            fechado = False

            while indice < tamanho:
                if codigo.startswith("*/", indice):
                    indice += 2
                    coluna += 2
                    fechado = True
                    break
                if codigo[indice] == "\n":
                    linha += 1
                    coluna = 1
                    indice += 1
                else:
                    indice += 1
                    coluna += 1

            if not fechado:
                raise ErroLexico(
                    f"Comentário de bloco não terminado na linha {linha_inicial}, coluna {coluna_inicial}"
                )
            continue

        # 4. Identificadores e Palavras-chave
        if caractere.isalpha() or caractere == "_":
            inicio = indice
            while indice < tamanho and (codigo[indice].isalnum() or codigo[indice] == "_"):
                indice += 1
                coluna += 1

            valor = codigo[inicio:indice]
            tipo = "PALAVRA_CHAVE" if valor in PALAVRAS_CHAVE else "IDENTIFICADOR"
            tokens.append(Token(tipo, valor, linha_inicial, coluna_inicial))
            continue

        # 5. Números (inteiros e decimais)
        if caractere.isdigit():
            inicio = indice
            while indice < tamanho and codigo[indice].isdigit():
                indice += 1
                coluna += 1

            if (
                indice < tamanho
                and codigo[indice] == "."
                and indice + 1 < tamanho
                and codigo[indice + 1].isdigit()
            ):
                indice += 1
                coluna += 1
                while indice < tamanho and codigo[indice].isdigit():
                    indice += 1
                    coluna += 1

            tokens.append(Token("NÚMERO", codigo[inicio:indice], linha_inicial, coluna_inicial))
            continue

        # 6. Strings e Caracteres literais ("..." ou '...')
        if caractere in ('"', "'"):
            delimitador_str = caractere
            inicio = indice
            indice += 1
            coluna += 1
            fechado = False

            while indice < tamanho:
                if codigo[indice] == "\\":
                    indice += 2
                    coluna += 2
                    continue
                if codigo[indice] == delimitador_str:
                    indice += 1
                    coluna += 1
                    fechado = True
                    break
                if codigo[indice] == "\n":
                    break
                indice += 1
                coluna += 1

            if not fechado:
                raise ErroLexico(
                    f"Literal não terminado na linha {linha_inicial}, coluna {coluna_inicial}"
                )

            tokens.append(Token("STRING", codigo[inicio:indice], linha_inicial, coluna_inicial))
            continue

        # 7. Operadores (compostos de 2 caracteres primeiro, depois de 1 caractere)
        operador_encontrado = False
        for tam in (2, 1):
            candidato = codigo[indice:indice + tam]
            if candidato in OPERADORES:
                tokens.append(Token("OPERADOR", candidato, linha_inicial, coluna_inicial))
                indice += tam
                coluna += tam
                operador_encontrado = True
                break

        if operador_encontrado:
            continue

        # 8. Delimitadores
        if caractere in DELIMITADORES:
            tokens.append(Token("DELIMITADOR", caractere, linha_inicial, coluna_inicial))
            indice += 1
            coluna += 1
            continue

        # 9. Caractere inválido
        raise ErroLexico(
            f"Caractere inválido {caractere!r} na linha {linha}, coluna {coluna}"
        )

    # Token de final de arquivo
    tokens.append(Token("FIM_DE_ARQUIVO", "", linha, coluna))

    # Preenche a Tabela de Símbolos com os identificadores e palavras-chave
    _popular_tabela_simbolos(tokens, tabela_simbolos)

    return tokens


# Aliases para compatibilidade
LexicalError = ErroLexico
lexer = analisar_lexico