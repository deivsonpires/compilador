import sys
from pathlib import Path

from lexer import analisar_lexico
from parser import analisar_sintatico
from semantic import analisar_semantico
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

def exibir_arvore(arvore, erros):
    print("\n=== ANÁLISE SINTÁTICA - AST ===")

    if arvore.filhos:
        for comando in arvore.filhos:
            print(comando.exibir())
            print()
    else:
        print("(nenhum comando reconhecido)")

    for erro in erros:
        print(f"[ERRO SINTÁTICO] {erro}")

def exibir_semantico(erros):
    print("\n=== ANÁLISE SEMÂNTICA ===")

    if erros:
        for erro in erros:
            print(f"[ERRO SEMÂNTICO] {erro}")
    else:
        print("Análise semântica concluída com sucesso. Nenhum erro encontrado.")

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
        codigo = caminho_fonte.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeError) as erro:
        print(f"Erro ao ler o arquivo: {erro}")
        return 1

    tabela_simbolos = Tab_Simbol()

    tokens, erros_lexicos = analisar_lexico(codigo, tabela_simbolos)

    print(f"Arquivo analisado: {caminho_fonte}")
    
    exibir_tokens(tokens)
    tabela_simbolos.display()

    if erros_lexicos:
        print("\n=== ERROS LÉXICOS ===")
        for erro in erros_lexicos:
            print(erro)
        print("\nAnálise léxica concluída com erros.")
    else:
        print("\nAnálise léxica concluída com sucesso.")

    arvore, erros_sintaticos = analisar_sintatico(tokens)
    exibir_arvore(arvore, erros_sintaticos)

    erros_semanticos = analisar_semantico(arvore, tabela_simbolos)
    exibir_semantico(erros_semanticos)

    if erros_lexicos or erros_sintaticos or erros_semanticos:
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())