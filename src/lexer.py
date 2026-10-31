from tokens import Token
from tab_simbol import Tab_Simbol


PALAVRAS_RESERVADA = {
    "auto", "break", "case", "char", "const",
    "continue", "default", "do", "double", "else",
    "enum", "extern", "float", "for", "goto", "if",
    "int", "long", "register", "return", "short",
    "signed", "sizeof", "static", "struct", "switch",
    "typedef", "union", "unsigned", "void", "volatile",
    "while", "_Bool",
}

OPERADORES = {
    ">>=", "<<=", "++", "--", "==", "!=", "<=", ">=",
    "&&", "||", "->", "+=", "-=", "*=", "/=", "%=",
    "<<", ">>", "&=", "|=", "^=",
    "+", "-", "*", "/", "%", "=", "<", ">", "!",
    "&", "|", "^", "~",
}

DELIMITADORES = {
    "?", ":", ";", ",", ".", "(", ")", "{", "}",
    "[", "]", "#",
}


class ErroLexico(Exception):
    pass


def analisar_lexico(codigo, tabela_simbolos=None):
    if tabela_simbolos is None:
        tabela_simbolos = Tab_Simbol()

    tokens = []
    indice = 0
    linha = 1
    coluna = 1
    tamanho = len(codigo)

    def adicionar_token(tipo, valor, linha_token, coluna_token):
        tokens.append(Token(tipo, valor, linha_token, coluna_token))

    while indice < tamanho:
        caractere = codigo[indice]

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

        if codigo.startswith("//", indice):
            while indice < tamanho and codigo[indice] != "\n":
                indice += 1
                coluna += 1
            continue

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
                    f"Comentário de bloco não terminado "
                    f"na linha {linha_inicial}, "
                    f"coluna {coluna_inicial}"
                )

            continue

        if caractere.isalpha() or caractere == "_":
            inicio = indice

            while indice < tamanho and (
                codigo[indice].isalnum() or codigo[indice] == "_"
            ):
                indice += 1
                coluna += 1

            valor = codigo[inicio:indice]
            tipo = (
                "PALAVRA_RESERVADA"
                if valor in PALAVRAS_RESERVADA
                else "IDENTIFICADOR"
            )

            tabela_simbolos.add(valor, tipo, tipo)

            adicionar_token(tipo, valor, linha_inicial, coluna_inicial)
            continue

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

            adicionar_token(
                "NÚMERO",
                codigo[inicio:indice],
                linha_inicial,
                coluna_inicial,
            )
            continue

        if caractere == '"':
            inicio = indice
            indice += 1
            coluna += 1
            fechado = False

            while indice < tamanho:
                if codigo[indice] == "\\":
                    if indice + 1 >= tamanho:
                        break

                    if codigo[indice + 1] == "\n":
                        raise ErroLexico(
                            f"Quebra de linha em string "
                            f"na linha {linha}, coluna {coluna}"
                        )

                    indice += 2
                    coluna += 2
                    continue

                if codigo[indice] == '"':
                    indice += 1
                    coluna += 1
                    fechado = True
                    break

                if codigo[indice] == "\n":
                    raise ErroLexico(
                        f"String não terminada na linha "
                        f"{linha_inicial}, coluna {coluna_inicial}"
                    )

                indice += 1
                coluna += 1

            if not fechado:
                raise ErroLexico(
                    f"String não terminada na linha "
                    f"{linha_inicial}, coluna {coluna_inicial}"
                )

            adicionar_token(
                "STRING", codigo[inicio:indice], linha_inicial, coluna_inicial
            )
            continue

        if caractere == "'":
            inicio = indice
            indice += 1
            coluna += 1
            fechado = False

            while indice < tamanho:
                if codigo[indice] == "\\":
                    if indice + 1 >= tamanho or codigo[indice + 1] == "\n":
                        break

                    indice += 2
                    coluna += 2
                    continue

                if codigo[indice] == "'":
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
                    f"Caractere não terminado na linha "
                    f"{linha_inicial}, coluna {coluna_inicial}"
                )

            adicionar_token(
                "STRING", codigo[inicio:indice], linha_inicial, coluna_inicial
            )
            continue

        operador_encontrado = False

        for tamanho_operador in (3, 2, 1):
            candidato = codigo[indice:indice + tamanho_operador]

            if candidato in OPERADORES:
                adicionar_token(
                    "OPERADOR_LÓGICO",
                    candidato,
                    linha_inicial,
                    coluna_inicial,
                )
                indice += tamanho_operador
                coluna += tamanho_operador
                operador_encontrado = True
                break

        if operador_encontrado:
            continue

        if caractere in DELIMITADORES:
            adicionar_token(
                "DELIMITADOR",
                caractere,
                linha_inicial,
                coluna_inicial,
            )
            indice += 1
            coluna += 1
            continue

        raise ErroLexico(
            f"Caractere inválido {caractere!r} "
            f"na linha {linha}, coluna {coluna}"
        )

    adicionar_token("FIM_DE_ARQUIVO", "", linha, coluna)
    return tokens


# Mantém os nomes anteriores disponíveis para quem já importa o lexer.
LexicalError = ErroLexico
lexer = analisar_lexico
