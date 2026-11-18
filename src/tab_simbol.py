from dataclasses import dataclass
from typing import Optional

@dataclass
class Simbol:
    lexeme: str
    category: str
    tipo_token: str
    ordem: int
    tipo_declarado: Optional[str] = None
    linha_declaracao: Optional[int] = None

class Tab_Simbol:
    def __init__(self):
        self._simbol = {}

    def add(self, lexeme: str, category: str, tipo_token: str, tipo_declarado: Optional[str] = None, linha: Optional[int] = None):
        simbol = self._simbol.get(lexeme)
        if simbol is not None:
            if tipo_declarado is not None:
                simbol.tipo_declarado = tipo_declarado
                if simbol.linha_declaracao is None:
                    simbol.linha_declaracao = linha
            return simbol
        ordem = len(self._simbol) + 1
        simbol = Simbol(lexeme, category, tipo_token, ordem, tipo_declarado)
        if tipo_declarado is not None:
            simbol.linha_declaracao = linha
        self._simbol[lexeme] = simbol
        return simbol

    def lookup(self, lexeme: str):
        return self._simbol.get(lexeme)

    def lookup_id(self, id_texto: str):
        for simbol in self._simbol.values():
            if f"#{simbol.ordem}" == id_texto:
                return simbol
        return None

    def all_symbol(self):
        return list(self._simbol.values())

    def display(self):
        print("\n=== TABELA DE SÍMBOLOS ===")
        header = f"{'ID':<6}{'Lexema':<18}{'Categoria':<16}{'Tipo Token':<20}{'Tipo Declarado':<15}"
        print(header)
        print("-" * len(header))
        for simbol in self.all_symbol():
            print(
                f"#{simbol.ordem:<5}"
                f"{simbol.lexeme:<18}"
                f"{simbol.category:<16}"
                f"{simbol.tipo_token:<20}"
                f"{simbol.tipo_declarado or '-':<15}"
            )