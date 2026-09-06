"""
Configuração do módulo de moderação.

Regra do ponto 9 do pedido original: nenhuma chave de API no código-fonte.
Tudo vem de variável de ambiente. Em desenvolvimento local, use um arquivo
`.env` (não versionado — adicione ao .gitignore) e carregue com
`python-dotenv`, ou exporte as variáveis no terminal antes de rodar.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ModerationConfig:
    # Limiares gerais de decisão
    auto_reject_threshold: float = 0.6   # confiança mínima p/ status = rejected
    auto_pending_threshold: float = 0.3  # confiança mínima p/ status = pending_review

    # Configuração do futuro analisador de IA (opcional — ver ai_analyzer.py)
    ai_provider: str = ""     # ex: "anthropic", "openai" — nunca usado ainda na v1
    ai_api_key: str = ""      # lido de env, NUNCA hardcoded

    @classmethod
    def from_env(cls) -> "ModerationConfig":
        return cls(
            auto_reject_threshold=float(
                os.environ.get("MODERATION_AUTO_REJECT_THRESHOLD", 0.6)
            ),
            auto_pending_threshold=float(
                os.environ.get("MODERATION_AUTO_PENDING_THRESHOLD", 0.3)
            ),
            ai_provider=os.environ.get("MODERATION_AI_PROVIDER", ""),
            ai_api_key=os.environ.get("MODERATION_AI_API_KEY", ""),
        )
