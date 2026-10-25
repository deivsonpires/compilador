from tokens import Token
from tab_simbol import Tab_Simbol


KEYWORDS = {
    "auto", "break", "case", "char", "const",
    "continue", "default", "do", "double", "else",
    "enum", "extern", "float", "for", "goto", "if",
    "int", "long", "register", "return", "short",
    "signed", "sizeof", "static", "struct", "switch",
    "typedef", "union", "unsigned", "void", "volatile",
    "while", "_Bool",
}

TYPE_KEYWORDS = {
    "char", "double", "float", "int", "long",
    "short", "signed", "unsigned", "void", "_Bool",
}

# Operadores com mais de um caractere vêm primeiro.
OPERATORS = {
    ">>=": "RIGHT_SHIFT_ASSIGN",
    "<<=": "LEFT_SHIFT_ASSIGN",
    "++": "INCREMENT",
    "--": "DECREMENT",
    "==": "EQUAL",
    "!=": "NOT_EQUAL",
    "<=": "LESS_EQUAL",
    ">=": "GREATER_EQUAL",
    "&&": "LOGICAL_AND",
    "||": "LOGICAL_OR",
    "->": "ARROW",
    "+=": "PLUS_ASSIGN",
    "-=": "MINUS_ASSIGN",
    "*=": "MULTIPLY_ASSIGN",
    "/=": "DIVIDE_ASSIGN",
    "%=": "MODULO_ASSIGN",
    "<<": "LEFT_SHIFT",
    ">>": "RIGHT_SHIFT",
    "&=": "BIT_AND_ASSIGN",
    "|=": "BIT_OR_ASSIGN",
    "^=": "BIT_XOR_ASSIGN",
}

SINGLE_SIMBOLS = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "MULTIPLY",
    "/": "DIVIDE",
    "%": "MODULO",
    "=": "ASSIGN",
    "<": "LESS",
    ">": "GREATER",
    "!": "LOGICAL_NOT",
    "&": "BIT_AND",
    "|": "BIT_OR",
    "^": "BIT_XOR",
    "~": "BIT_NOT",
    "?": "QUESTION",
    ":": "COLON",
    ";": "SEMICOLON",
    ",": "COMMA",
    ".": "DOT",
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    "[": "LBRACKET",
    "]": "RBRACKET",
    "#": "HASH",
}


class LexicalError(Exception):
    pass


def lexer(source, tab_simbol=None):
    if tab_simbol is None:
        tab_simbol = Tab_Simbol()

    tokens = []
    i = 0
    line = 1
    column = 1
    length = len(source)

    def add_token(token_type, value, token_line, token_column):
        tokens.append(
            Token(token_type, value, token_line, token_column)
        )

    while i < length:
        char = source[i]

        # Ignora espaços, tabulações e quebras de linha.
        if char.isspace():
            if char == "\n":
                line += 1
                column = 1
            else:
                column += 1

            i += 1
            continue

        start_line = line
        start_column = column

        # Comentário de uma linha: // ...
        if source.startswith("//", i):
            while i < length and source[i] != "\n":
                i += 1
                column += 1
            continue

        # Comentário de bloco: /* ... */
        if source.startswith("/*", i):
            i += 2
            column += 2
            closed = False

            while i < length:
                if source.startswith("*/", i):
                    i += 2
                    column += 2
                    closed = True
                    break

                if source[i] == "\n":
                    line += 1
                    column = 1
                    i += 1
                else:
                    i += 1
                    column += 1

            if not closed:
                raise LexicalError(
                    f"Comentário de bloco não terminado "
                    f"na linha {start_line}, "
                    f"coluna {start_column}"
                )

            continue

        # Identificadores e palavras reservadas.
        if char.isalpha() or char == "_":
            start = i

            while i < length and (
                source[i].isalnum() or source[i] == "_"
            ):
                i += 1
                column += 1

            value = source[start:i]

            if value in KEYWORDS:
                token_type = "KEYWORD"
                category = (
                    "TYPE_KEYWORD"
                    if value in TYPE_KEYWORDS
                    else "RESERVED_WORD"
                )
            else:
                token_type = "IDENTIFIER"
                category = "IDENTIFIER"

            tab_simbol.add(value, category, token_type)
            add_token(token_type, value, start_line, start_column)
            continue

        # Números inteiros e decimais simples.
        if char.isdigit():
            start = i
            is_float = False

            while i < length and source[i].isdigit():
                i += 1
                column += 1

            if (
                i < length
                and source[i] == "."
                and i + 1 < length
                and source[i + 1].isdigit()
            ):
                is_float = True
                i += 1
                column += 1

                while i < length and source[i].isdigit():
                    i += 1
                    column += 1

            value = source[start:i]
            token_type = "FLOAT" if is_float else "INTEGER"
            add_token(token_type, value, start_line, start_column)
            continue

        # Strings entre aspas duplas.
        if char == '"':
            start = i
            i += 1
            column += 1
            closed = False

            while i < length:
                if source[i] == "\\":
                    # Trata sequências escapadas, como \" e \n.
                    if i + 1 >= length:
                        break

                    if source[i + 1] == "\n":
                        raise LexicalError(
                            f"Quebra de linha em string "
                            f"na linha {line}, coluna {column}"
                        )

                    i += 2
                    column += 2
                    continue

                if source[i] == '"':
                    i += 1
                    column += 1
                    closed = True
                    break

                if source[i] == "\n":
                    raise LexicalError(
                        f"String não terminada na linha "
                        f"{start_line}, coluna {start_column}"
                    )

                i += 1
                column += 1

            if not closed:
                raise LexicalError(
                    f"String não terminada na linha "
                    f"{start_line}, coluna {start_column}"
                )

            add_token(
                "STRING", source[start:i], start_line, start_column
            )
            continue

        # Caractere entre aspas simples.
        if char == "'":
            start = i
            i += 1
            column += 1
            closed = False

            while i < length:
                if source[i] == "\\":
                    if i + 1 >= length:
                        break
                    if source[i + 1] == "\n":
                        break

                    i += 2
                    column += 2
                    continue

                if source[i] == "'":
                    i += 1
                    column += 1
                    closed = True
                    break

                if source[i] == "\n":
                    break

                i += 1
                column += 1

            if not closed:
                raise LexicalError(
                    f"Caractere não terminado na linha "
                    f"{start_line}, coluna {start_column}"
                )

            add_token(
                "CHAR_LITERAL",
                source[start:i],
                start_line,
                start_column,
            )
            continue

        # Operadores: tenta reconhecer primeiro o mais longo.
        matched = False

        for size in (3, 2):
            candidate = source[i:i + size]

            if candidate in OPERATORS:
                add_token(
                    OPERATORS[candidate],
                    candidate,
                    start_line,
                    start_column,
                )
                i += size
                column += size
                matched = True
                break

        if matched:
            continue

        # Símbolos de um único caractere.
        if char in SINGLE_SIMBOLS:
            add_token(
            SINGLE_SIMBOLS[char],
                char,
                start_line,
                start_column,
            )
            i += 1
            column += 1
            continue

        # Qualquer caractere não reconhecido gera erro.
        raise LexicalError(
            f"Caractere inválido {char!r} "
            f"na linha {line}, coluna {column}"
        )

    add_token("EOF", "", line, column)
    return tokens
