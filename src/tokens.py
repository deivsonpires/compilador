from dataclasses import dataclass

@dataclass
class Token:
    tipo: str
    lexema: str
    linha: int
    coluna: int