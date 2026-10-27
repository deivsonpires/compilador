
import sys
from pathlib import Path

from lexer import analisar_lexico, ErroLexico
from tab_simbol import Tab_Simbol


def exibir_tokens(tokens):
    print("\n=== LISTA DE TOKENS ===")

    print(
        f"{'Tipo':<22}"
        f"{'Lexema':<24}"
        f"{'Linha':<10}"
        f"{'Coluna':<10}"
    )

    print("-" * 66)

    for token in tokens:
        if token.tipo == "FIM_DE_ARQUIVO":
            continue

        print(
            f"{token.tipo:<22}"
            f"{token.lexema!r:<24}"
            f"{token.linha:<10}"
            f"{token.coluna:<10}"
        )


def main():
    reconfigurar_saida = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigurar_saida):
        reconfigurar_saida(encoding="utf-8")

    if len(sys.argv) != 2:
        print(
            "Uso: python src/main.py <arquivo.c>"
        )
        return 1

    caminho_fonte = Path(sys.argv[1])

    if not caminho_fonte.is_file():
        print(
            f"Erro: arquivo não encontrado: {caminho_fonte}"
        )
        return 1

    if caminho_fonte.suffix.lower() != ".c":
        print("Erro: informe um arquivo com extensão .c")
        return 1

    try:
        codigo = caminho_fonte.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as erro:
        print(f"Erro ao ler o arquivo: {erro}")
        return 1

    tabela_simbolos = Tab_Simbol()

    try:
        tokens = analisar_lexico(codigo, tabela_simbolos)
    except ErroLexico as erro:
        print(f"\n[ERRO LÉXICO] {erro}")
        return 1

    print(f"Arquivo analisado: {caminho_fonte}")
    exibir_tokens(tokens)
    tabela_simbolos.display()

    print("\nAnálise léxica concluída com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
