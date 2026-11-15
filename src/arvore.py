from dataclasses import dataclass, field 
from typing import Optional

@dataclass
class No:
    rotulo: str
    valor: Optional[str] = None
    filhos: list["No"] = field(default_factory=list)
    linha: int=0

    def __str__(self):
        if self.valor is not None:
            return f"{self.rotulo} ({self.valor})"
        return self.rotulo

    def exibir(self):
        linhas = [str(self)]
        self._desenhar_filhos("", linhas)
        return "\n".join(linhas)

    def _desenhar_filhos(self, recuo, linhas):
        for i, filho in enumerate(self.filhos):
            eh_ultimo = i == len(self.filhos) - 1
            conector = "└── " if eh_ultimo else "├── "
            linhas.append(recuo + conector + str(filho))
            filho._desenhar_filhos(recuo + ("    " if eh_ultimo else "│   "), linhas)