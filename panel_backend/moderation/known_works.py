"""
Base de "obras conhecidas" usada para comparar título/autor da submissão.

ATENÇÃO: a lista `_SEED_KNOWN_WORKS` abaixo é só um EXEMPLO MÍNIMO para a
triagem não ficar totalmente cega no dia 1. Ela está longe de ser uma
lista real de obras protegidas — não use isso como base jurídica de nada.
Em produção, isso deveria vir de uma fonte mantida (arquivo de config
carregado externamente, ou serviço de terceiros), nunca hardcoded no
código-fonte igual está aqui na v1.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass(frozen=True)
class KnownWork:
    title: str
    publisher: str = ""
    aliases: tuple[str, ...] = ()


# Exemplo mínimo — troque por um arquivo externo (KNOWN_WORKS_FILE) assim
# que houver uma lista de verdade para carregar.
_SEED_KNOWN_WORKS: list[KnownWork] = [
    KnownWork("Batman", "DC Comics"),
    KnownWork("Spider-Man", "Marvel", aliases=("Homem-Aranha",)),
    KnownWork("One Piece", "Shueisha"),
    KnownWork("Naruto", "Shueisha"),
    KnownWork("Dragon Ball", "Shueisha"),
    KnownWork("Turma da Mônica", "Mauricio de Sousa Produções"),
]


class KnownWorksRepository:
    """
    Interface simples de leitura. Troca de fonte de dados (arquivo local
    -> banco -> serviço externo) não deve exigir mudanças no analisador
    que a consome.
    """

    def __init__(self, works: list[KnownWork] | None = None):
        self._works = works if works is not None else list(_SEED_KNOWN_WORKS)

    @classmethod
    def from_env_or_seed(cls) -> "KnownWorksRepository":
        """
        Carrega de um JSON externo se KNOWN_WORKS_FILE estiver definido;
        cai para a lista-semente caso contrário.
        """
        path = os.environ.get("KNOWN_WORKS_FILE")
        if path and os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            works = [
                KnownWork(
                    title=item["title"],
                    publisher=item.get("publisher", ""),
                    aliases=tuple(item.get("aliases", [])),
                )
                for item in raw
            ]
            return cls(works)
        return cls()

    def best_match(self, text: str) -> tuple[KnownWork, float] | None:
        """
        Retorna a obra conhecida mais parecida com `text` e a similaridade
        (0.0-1.0), ou None se a lista estiver vazia. Comparação simples por
        string — suficiente para uma v1, não é reconhecimento semântico.
        """
        if not text or not self._works:
            return None

        text_norm = text.strip().lower()
        best: tuple[KnownWork, float] | None = None

        for work in self._works:
            candidates = (work.title, *work.aliases)
            for candidate in candidates:
                score = SequenceMatcher(None, text_norm, candidate.lower()).ratio()
                if best is None or score > best[1]:
                    best = (work, score)

        return best
