# Analisador de Código C em Python

Front-end de um compilador simplificado para a linguagem C desenvolvido em Python. O programa lê arquivos-fonte (`.c`), executa as etapas de análise **léxica**, **sintática** e **semântica**, exibe no terminal a lista de tokens, a tabela de símbolos e a Árvore Sintática Abstrata (AST), além de apontar todos os erros encontrados com linha e coluna.

## Erros Captados por Análise

### 1. Análise Léxica (`src/lexer.py`)
* **Caracteres inválidos:** Símbolos que não pertencem ao alfabeto da linguagem (ex.: `@`, `$`).
* **Identificadores inválidos:** Identificadores iniciados por dígitos (ex.: `3valor`).
* **Números malformados:** Valores com múltiplos pontos decimais ou ponto sem casas decimais (ex.: `20.3.4`, `15.`).
* **Strings e caracteres não fechados:** Aspas duplas ou simples abertas sem fechamento até o fim da linha (ex.: `"texto`, `'a`).
* **Literais `char` inválidos:** Caractere vazio (`''`) ou com mais de um caractere (`'abc'`).
* **Comentários de bloco não fechados:** Abertura `/*` sem o fechamento `*/` até o fim do arquivo.

### 2. Análise Sintática (`src/parser.py` e `src/arvore.py`)
* **Delimitadores e pontuação ausentes:** Falta de `;` ao final de instruções ou parênteses `)` não fechados em expressões e chamadas de função.
* **Comandos e expressões malformados:** Tokens inesperados na estrutura de declarações, atribuições ou operandos inválidos, informando o elemento esperado, o encontrado, a linha e a coluna.

### 3. Análise Semântica (`src/semantic.py`)
* **Variável não declarada:** Uso de variáveis em expressões ou atribuições antes de sua declaração prévia.
* **Incompatibilidade de tipos:** Atribuição de valores incompatíveis com o tipo declarado da variável (ex.: atribuir `String` ou `char` a um `int`, ou `float` a `int`). *(Conversões implícitas de `int` para `float`/`double` são aceitas).*

## Estrutura do Projeto

```text
├── docs/  
│   ├── Compilador.pdf                  # Documentação detalhando a responsabilidade de cada arquivo
├── programas/                      # Programas em C (.c) para execução e testes de erro
│   ├── programa.c
│   ├── programa_ava.c
│   ├── programa_erro_lex.c
│   ├── programa_erro_seman.c
│   └── programa_erro_sintatico.c
└── src/                            # Código-fonte do compilador
    ├── arvore.py
    ├── lexer.py
    ├── main.py
    ├── parser.py
    ├── semantic.py
    ├── tab_simbol.py
    └── tokens.py
```

## Como Executar

### Pré-requisitos
* **Python 3.10+** (o projeto utiliza apenas módulos nativos da biblioteca padrão, sem dependências externas).

### Comando no terminal
A partir da raiz do projeto, execute:

```bash
python src/main.py programas/nome_do_arquivo.c
```

Exemplo com um dos arquivos de teste:

```bash
python src/main.py programas/programa.c
```

