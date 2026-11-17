class AnalisadorSemantico:
    def __init__(self, tabela_simbolos):
        self.tabela = tabela_simbolos  
        self.erros = []                

    def analisar(self, arvore):
        for comando in arvore.filhos:
            if comando.rotulo == "Declaracao":
                self._verificar_declaracao(comando)
            elif comando.rotulo == "Atribuicao":
                self._verificar_atribuicao(comando)
        return self.erros

    def _verificar_declaracao(self, comando):
        if len(comando.filhos) == 4:
            no_id = comando.filhos[1]
            no_expressao = comando.filhos[3]
            self._checar_compatibilidade(no_id.valor, no_expressao, comando.linha)

    def _verificar_atribuicao(self, comando):
        no_id = comando.filhos[0]
        no_expressao = comando.filhos[2]
        self._checar_compatibilidade(no_id.valor, no_expressao, comando.linha)

    def _checar_compatibilidade(self, nome_variavel, no_expressao, linha):
        simbolo = self.tabela.lookup(nome_variavel)
        if simbolo is None or simbolo.tipo_declarado is None:
            return
        tipo_variavel = simbolo.tipo_declarado
        tipo_valor = self._descobrir_tipo(no_expressao)
        if tipo_valor is None:
            return
        if not self._tipos_sao_compativeis(tipo_variavel, tipo_valor):
            mensagem = (
                f"Incompatibilidade de tipos na linha {linha}: "
                f"Não é possível atribuir {tipo_valor} a um tipo {tipo_variavel}."
            )
            self.erros.append(mensagem)

    def _descobrir_tipo(self, no):
        if no.rotulo == "STRING":
            if no.valor.startswith("'"):
                return "char"
            return "String"
        if no.rotulo == "NUM":
            if "." in no.valor:
                return "float"
            return "int"
        if no.rotulo == "ID":
            simbolo = self.tabela.lookup(no.valor)
            if simbolo is not None:
                return simbolo.tipo_declarado
            return None
        if no.rotulo == "Expressao":
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
            simbolo = self.tabela.lookup(no.valor)
            if simbolo is not None:
                return simbolo.tipo_declarado
            return None
        return None

    def _tipos_sao_compativeis(self, tipo_variavel, tipo_valor):
        if tipo_variavel == tipo_valor:
            return True
        if tipo_variavel in ("float", "double") and tipo_valor in ("int", "float", "double"):
            return True
        return False

def analisar_semantico(arvore, tabela_simbolos):
    analisador = AnalisadorSemantico(tabela_simbolos)
    return analisador.analisar(arvore)