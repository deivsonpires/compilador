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
        self._next_order = 1

    def add(self, lexeme, category, token_type, declared_type=None):
        # Evita duplicar um símbolo já registrado.
        if lexeme in self._simbol:
            simbol = self._simbol[lexeme]
            if declared_type is not None:
                simbol.declared_type = declared_type
            return simbol

        simbol = Simbol(
            lexeme=lexeme,
            category=category,
            token_type=token_type,
            insertion_order=self._next_order,
            declared_type=declared_type,
        )

        self._simbol[lexeme] = simbol
        self._next_order += 1

        return simbol

    def lookup(self, lexeme):
        return self._simbol.get(lexeme)

    def set_declared_type(self, lexeme, declared_type):
        simbol = self.lookup(lexeme)

        if simbol is None:
            return False

        simbol.declared_type = declared_type
        return True

    def all_symbol(self):
        return list(self._simbol.values())

    def display(self):
        print("\n=== TABELA DE SÍMBOLOS ===")

        print(
            f"{'ID':<8}"
            f"{'Lexema':<18}"
            f"{'Categoria':<20}"
            f"{'Tipo de token':<18}"
            f"{'Tipo declarado':<18}"
        )

        print("-" * 82)

        for simbol in self.all_symbol():
            declared_type = simbol.declared_type or "-"

            print(
                f"#{simbol.insertion_order:<7}"
                f"{simbol.lexeme:<18}"
                f"{simbol.category:<20}"
                f"{simbol.token_type:<18}"
                f"{declared_type:<18}"
            )
