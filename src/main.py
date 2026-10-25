
import sys
from pathlib import Path

from lexer import lexer, LexicalError
from tab_simbol import Tab_Simbol


def display_tokens(tokens):
    print("\n=== LISTA DE TOKENS ===")

    print(
        f"{'Tipo':<22}"
        f"{'Lexema':<24}"
        f"{'Linha':<10}"
        f"{'Coluna':<10}"
    )

    print("-" * 66)

    for token in tokens:
        print(
            f"{token.type:<22}"
            f"{token.value!r:<24}"
            f"{token.line:<10}"
            f"{token.column:<10}"
        )


def main():
    if len(sys.argv) != 2:
        print(
            "Uso: python src/main.py <arquivo.c>"
        )
        return 1

    source_path = Path(sys.argv[1])

    if not source_path.is_file():
        print(
            f"Erro: arquivo não encontrado: {source_path}"
        )
        return 1

    if source_path.suffix.lower() != ".c":
        print("Erro: informe um arquivo com extensão .c")
        return 1

    try:
        source = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"Erro ao ler o arquivo: {error}")
        return 1

    tab_simbol = Tab_Simbol()

    try:
        tokens = lexer(source, tab_simbol)
    except LexicalError as error:
        print(f"\n[ERRO LÉXICO] {error}")
        return 1

    print(f"Arquivo analisado: {source_path}")
    display_tokens(tokens)
    tab_simbol.display()

    print("\nAnálise léxica concluída com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
