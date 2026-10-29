"""
Árvore Sintática Abstrata (AST).
Cada nó tem um rótulo (ex.: "Atribuicao"), um valor opcional (ex.: "x")
e uma lista de filhos. Este arquivo só DESCREVE a árvore e sabe se
desenhar no terminal. Quem constrói a árvore é o parser (parser.py).
"""


from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Node:
    label: str                       # tipo do nó: "Atribuicao", "ID", "NUM"...
    value: Optional[str] = None      # texto do token: "x" (None nos nós internos)
    children: list["Node"] = field(default_factory=list)
    line: int = 0                    # linha do código, útil para mensagens

    def __str__(self):
        if self.value is not None:
            return f"{self.label} ({self.value})"
        return self.label

    def display(self):
        """Desenha a árvore inteira a partir deste nó, com ├── e └──."""
        lines = [str(self)]
        self._draw_children("", lines)
        return "\n".join(lines)

    def _draw_children(self, prefix, lines):
        for i, child in enumerate(self.children):
            is_last = i == len(self.children) - 1
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + str(child))
            # Recursão: o filho desenha os filhos dele, com recuo maior.
            child._draw_children(prefix + ("    " if is_last else "│   "), lines)