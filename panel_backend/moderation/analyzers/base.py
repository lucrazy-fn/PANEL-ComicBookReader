"""
Contrato que todo analisador de risco precisa seguir.

A ideia central do ponto 8 do pedido original: o ModerationService nunca
sabe COMO um analisador decide algo — só chama `.analyze(submission)` e
recebe um AnalyzerFinding de volta. Isso permite:

  - trocar o analisador de regras por um baseado em IA sem tocar no service
  - rodar vários analisadores em paralelo e combinar os resultados
  - desligar um analisador problemático sem quebrar os outros
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from panel_backend.moderation.models import AnalyzerFinding, PublicationSubmission


class BaseAnalyzer(ABC):
    """Toda nova forma de analisar risco (regras, IA, comparação de hash, etc.) implementa isso."""

    #: nome curto usado em logs e no campo `analyzer_name` do finding
    name: str = "base"

    @abstractmethod
    def analyze(self, submission: PublicationSubmission) -> AnalyzerFinding:
        """
        Recebe os dados da submissão e retorna UM finding.
        Nunca deve lançar exceção por "achar" risco — isso é modelado no
        próprio retorno (risk_level). Exceções devem ser reservadas para
        falhas reais (ex: analisador externo fora do ar).
        """
        raise NotImplementedError

    def is_available(self) -> bool:
        """
        Permite ao analisador se auto-desabilitar (ex: falta variável de
        ambiente com chave de API). O service deve pular analisadores
        indisponíveis em vez de derrubar toda a triagem.
        """
        return True
