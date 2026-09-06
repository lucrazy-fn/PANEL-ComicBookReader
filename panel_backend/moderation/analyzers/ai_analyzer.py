"""
Esqueleto do futuro analisador baseado em IA externa (visão computacional,
comparação de capa, análise de texto extraído, etc.).

Propositalmente NÃO implementado ainda — o pedido original foi priorizar
a arquitetura antes de uma solução complexa. Isso aqui existe para provar
que o encaixe funciona: quando alguém implementar `_call_provider`, nada
no resto do sistema (service.py, rotas da API) precisa mudar.

Nunca coloque chaves de API aqui no código. Elas vêm de variável de
ambiente (ver panel_backend/moderation/config.py).
"""

from __future__ import annotations

from panel_backend.moderation.analyzers.base import BaseAnalyzer
from panel_backend.moderation.config import ModerationConfig
from panel_backend.moderation.models import (
    AnalyzerFinding,
    PublicationSubmission,
    RiskLevel,
)


class AIAnalyzer(BaseAnalyzer):
    name = "ai_analyzer_v0"

    def __init__(self, config: ModerationConfig | None = None):
        self._config = config or ModerationConfig.from_env()

    def is_available(self) -> bool:
        # Se não houver chave configurada, o service pula este analisador
        # em vez de quebrar a triagem inteira.
        return bool(self._config.ai_api_key)

    def analyze(self, submission: PublicationSubmission) -> AnalyzerFinding:
        if not self.is_available():
            return AnalyzerFinding(
                analyzer_name=self.name,
                risk_level=RiskLevel.LOW,
                confidence=0.0,
                reasons=["Analisador de IA não configurado (sem chave de API); ignorado."],
            )

        # TODO (v2): implementar a chamada real ao provedor configurado em
        # self._config.ai_provider, usando self._config.ai_api_key.
        # A resposta do provedor deve ser convertida para AnalyzerFinding
        # aqui dentro — o resto do sistema nunca deve saber qual provedor
        # está sendo usado.
        raise NotImplementedError(
            "AIAnalyzer ainda não está implementado — isto é só a estrutura "
            "para o service.py conseguir plugar um analisador de IA no "
            "futuro sem exigir mudanças em outros arquivos."
        )
