from dataclasses import dataclass
from typing import Optional

@dataclass
class Simbol:
    lexeme: str
    category: str
    token_type: str
    insertion_order: int
    declared_type: Optional[str] = None


class Tab_Simbol:
    def __init__(self):
        self._simbol = {}

    def add(self, lexeme: str, category: str, token_type: str, declared_type: Optional[str] = None):
        simbol = self._simbol.get(lexeme)

        if simbol is not None:
            if declared_type is not None:
                simbol.declared_type = declared_type
            return simbol

        ordem = len(self._simbol) + 1
        simbol = Simbol(lexeme, category, token_type, ordem, declared_type)
        self._simbol[lexeme] = simbol
        return simbol

    def lookup(self, lexeme: str):
        return self._simbol.get(lexeme)

    def all_symbol(self):
        return list(self._simbol.values())

    def display(self):
        print("\n=== TABELA DE SÍMBOLOS ===")
        header = f"{'ID':<6}{'Lexema':<18}{'Categoria':<16}{'Tipo Token':<20}{'Tipo Declarado':<15}"
        print(header)
        print("-" * len(header))

        for simbol in self.all_symbol():
            print(
                f"#{simbol.insertion_order:<5}"
                f"{simbol.lexeme:<18}"
                f"{simbol.category:<16}"
                f"{simbol.token_type:<20}"
                f"{simbol.declared_type or '-':<15}"
            )