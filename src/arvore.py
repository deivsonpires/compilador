# arvore.py - AST
#
# cada caixinha da arvore é um No. Ele guarda:
#   rotulo - o nome do nó ("Atribuicao", "ID", "NUM"...)
#   valor - os textos, se tiver ("x", "5"...)
#   filhos - os nós que ficam abaixo dele 
#   linha - a linha do codigo

from dataclasses import dataclass, field 
from typing import Optional


@dataclass
class No:
    rotulo: str
    valor: Optional[str] = None
    filhos: list["No"] = field(default_factory=list)
    linha: int=0

    def __str__(self):
        # Como o nó aparece escrito: "ID (x)" ou só "Atribuicao"
        if self.valor is not None:
            return f"{self.rotulo} ({self.valor})"
        return self.rotulo

    def exibir(self):
        # Desenha a árvore inteira a partir desse nó
        linhas = [str(self)]
        self._desenhar_filhos("", linhas)
        return "\n".join(linhas)

    def _desenhar_filhos(self, recuo, linhas):
        # Escreve uma linha para cada filho. O último filho usa └── e os
        # outros usam ├──. Depois cada filho desenha os filhos dele.
        # O recuo é "│   " se o pai ainda tem irmãos abaixo, e espaços
        # se não tem. É isso que deixa a árvore alinhada.
        for i, filho in enumerate(self.filhos):
            eh_ultimo = i == len(self.filhos) - 1
            conector = "└── " if eh_ultimo else "├── "
            linhas.append(recuo + conector + str(filho))
            filho._desenhar_filhos(recuo + ("    " if eh_ultimo else "│   "), linhas)