# semantico.py - análise semântica (Opção 1: Compatibilidade de Tipos)
#
# O que o analisador semântico faz:
#   1. Percorre os comandos da árvore (AST) montada pelo parser.
#   2. Quando encontra uma declaração com valor (int x = "oi";) ou uma
#      atribuição (x = "oi";), consulta o tipo da variável na Tabela de Símbolos.
#   3. Descobre o tipo do valor que está sendo atribuído e verifica se os
#      dois tipos são compatíveis.


class AnalisadorSemantico:
    def __init__(self, tabela_simbolos):
        self.tabela = tabela_simbolos  # tabela já preenchida pelo lexer
        self.erros = []                # lista para guardar os erros encontrados

    def analisar(self, arvore):
        # Percorre cada comando dentro da raiz "Programa" da árvore
        for comando in arvore.filhos:
            if comando.rotulo == "Declaracao":
                self._verificar_declaracao(comando)
            elif comando.rotulo == "Atribuicao":
                self._verificar_atribuicao(comando)

        return self.erros

    def _verificar_declaracao(self, comando):
        # Na árvore do parser, uma declaração sem valor tem 2 filhos: [TIPO, ID]
        # Uma declaração com valor tem 4 filhos: [TIPO, ID, OP_ATRIB, Expressao]
        if len(comando.filhos) == 4:
            no_id = comando.filhos[1]
            no_expressao = comando.filhos[3]
            self._checar_compatibilidade(no_id.valor, no_expressao, comando.linha)

    def _verificar_atribuicao(self, comando):
        # Na árvore do parser, uma atribuição tem 3 filhos: [ID, OP_ATRIB, Expressao]
        no_id = comando.filhos[0]
        no_expressao = comando.filhos[2]
        self._checar_compatibilidade(no_id.valor, no_expressao, comando.linha)

    def _checar_compatibilidade(self, nome_variavel, no_expressao, linha):
        # Busca a variável na Tabela de Símbolos
        simbolo = self.tabela.lookup(nome_variavel)

        # Se a variável não estiver na tabela ou não tiver tipo, não há o que comparar
        if simbolo is None or simbolo.declared_type is None:
            return

        tipo_variavel = simbolo.declared_type
        tipo_valor = self._descobrir_tipo(no_expressao)

        # Se não foi possível identificar o tipo da expressão, encerra a verificação
        if tipo_valor is None:
            return

        # Se os tipos não forem compatíveis, registra o erro semântico
        if not self._tipos_sao_compativeis(tipo_variavel, tipo_valor):
            mensagem = (
                f"Incompatibilidade de tipos na linha {linha}: "
                f"Não é possível atribuir {tipo_valor} a um tipo {tipo_variavel}."
            )
            self.erros.append(mensagem)

    def _descobrir_tipo(self, no):
        # Descobre qual é o tipo de um nó da expressão
        if no.rotulo == "STRING":
            # Aspas simples ('a') representam char; aspas duplas ("texto") representam String
            if no.valor.startswith("'"):
                return "char"
            return "String"

        if no.rotulo == "NUM":
            # Se tiver ponto decimal, é float; caso contrário, é int
            if "." in no.valor:
                return "float"
            return "int"

        if no.rotulo == "ID":
            # Procura o tipo da variável usada dentro da expressão
            simbolo = self.tabela.lookup(no.valor)
            if simbolo is not None:
                return simbolo.declared_type
            return None

        if no.rotulo == "Expressao":
            # Expressão matemática (ex: a + b): verifica o tipo dos dois lados
            tipo_esquerda = self._descobrir_tipo(no.filhos[0])
            tipo_direita = self._descobrir_tipo(no.filhos[1])

            if tipo_esquerda == "String" or tipo_direita == "String":
                return "String"

            if tipo_esquerda is None or tipo_direita is None:
                return None

            if tipo_esquerda in ("float", "double") or tipo_direita in ("float", "double"):
                return "float"

            return "int"

        if no.rotulo == "Chamada":
            # Procura o tipo de retorno da função na tabela de símbolos
            simbolo = self.tabela.lookup(no.valor)
            if simbolo is not None:
                return simbolo.declared_type
            return None

        return None

    def _tipos_sao_compativeis(self, tipo_variavel, tipo_valor):
        # Tipos idênticos são sempre compatíveis (ex: int com int, float com float)
        if tipo_variavel == tipo_valor:
            return True

        # Variáveis decimais (float ou double) aceitam receber números inteiros (int)
        if tipo_variavel in ("float", "double") and tipo_valor in ("int", "float", "double"):
            return True

        # Qualquer outra combinação (ex: int recebendo String ou float) é incompatível
        return False


def analisar_semantico(arvore, tabela_simbolos):
    # Função que o main.py chama. Devolve a lista de erros semânticos.
    analisador = AnalisadorSemantico(tabela_simbolos)
    return analisador.analisar(arvore)