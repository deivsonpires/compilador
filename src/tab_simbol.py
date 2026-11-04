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
    """Tabela de símbolos: guarda cada lexema uma única vez, na ordem de inserção."""

    def __init__(self):
        self._simbol = {}

    # --- Operações principais ----------------------------------------------

    def add(self, lexeme, category, token_type, declared_type=None):
        """Insere o símbolo. Se já existir, só atualiza o tipo declarado (quando informado)."""
        simbol = self._simbol.get(lexeme)

        if simbol is not None:
            if declared_type is not None:
                simbol.declared_type = declared_type
            return simbol

        ordem = len(self._simbol) + 1
        simbol = Simbol(lexeme, category, token_type, ordem, declared_type)
        self._simbol[lexeme] = simbol
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

    # --- Exibição ----------------------------------------------------------

    def _formatar_linha(self, id_, lexema, categoria, tipo_token, tipo_declarado):
        return f"{id_:<8}{lexema:<18}{categoria:<20}{tipo_token:<18}{tipo_declarado:<18}"

    def display(self):
        print("\n=== TABELA DE SÍMBOLOS ===")
        print(self._formatar_linha("ID", "Lexema", "Categoria", "Tipo de token", "Tipo declarado"))
        print("-" * 82)

        for simbol in self.all_symbol():
            print(self._formatar_linha(
                f"#{simbol.insertion_order}",
                simbol.lexeme,
                simbol.category,
                simbol.token_type,
                simbol.declared_type or "-",
            ))