"""
Modelos de dados do sistema de moderação.

Este módulo define apenas estruturas de dados (sem lógica de negócio).
A lógica de decisão vive em `service.py` e nos analisadores em `analyzers/`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ModerationStatus(str, Enum):
    """
    Status final de uma publicação após a triagem.

    IMPORTANTE: nenhum desses status representa uma conclusão jurídica.
    'approved' significa apenas "baixo risco identificado pela triagem
    automática", nunca "confirmado como legal".
    """
    APPROVED = "approved"                # baixo risco — publicação liberada
    PENDING_REVIEW = "pending_review"     # indícios de risco — aguarda revisão humana
    REJECTED = "rejected"                 # fortes indícios de conteúdo não permitido


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class PublicationSubmission:
    """
    Dados enviados pelo usuário ao tentar publicar um quadrinho.
    Isso é o "input" da moderação — nada aqui é gerado pelo sistema.
    """
    user_id: str
    title: str
    author: str
    description: str
    tags: list[str] = field(default_factory=list)

    # Declaração feita pelo próprio usuário no momento do envio.
    authorship_declared: bool = False          # "eu sou o autor" ou
    authorization_declared: bool = False        # "tenho autorização para publicar"
    license: Optional[str] = None               # ex: "CC-BY-4.0", "Domínio Público", None

    # Metadados técnicos do arquivo (extraídos automaticamente, não digitados)
    file_name: Optional[str] = None
    file_hash: Optional[str] = None              # hash do conteúdo, útil p/ dedupe/similaridade
    cover_image_bytes: Optional[bytes] = None
    embedded_metadata: dict = field(default_factory=dict)  # ex: ComicInfo.xml, EXIF, etc.

    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AnalyzerFinding:
    """
    Resultado de UM analisador individual (ver analyzers/base.py).
    O ModerationService combina vários findings num ModerationResult.
    """
    analyzer_name: str
    risk_level: RiskLevel
    confidence: float           # 0.0 a 1.0 — confiança do próprio analisador no achado
    reasons: list[str]          # justificativa interna, legível por humano (não jurídica)
    matched_signals: dict = field(default_factory=dict)  # dados brutos p/ auditoria/debug


@dataclass
class ModerationResult:
    """
    Resultado final e consolidado da triagem — o que o resto do sistema usa.
    """
    submission_user_id: str
    status: ModerationStatus
    risk_level: RiskLevel
    confidence: float
    internal_justification: str      # texto interno, para logs e revisão humana
    findings: list[AnalyzerFinding]
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def public_message(self) -> str:
        """
        Mensagem segura para mostrar ao usuário final.
        NUNCA usar internal_justification diretamente na UI — ela pode
        conter linguagem técnica que soa como veredito jurídico.
        """
        if self.status == ModerationStatus.APPROVED:
            return (
                "Sua publicação passou pela triagem automática inicial e foi "
                "liberada. Isso não é uma confirmação legal de autoria — "
                "publicações podem ser removidas posteriormente se houver "
                "denúncia ou nova análise."
            )
        if self.status == ModerationStatus.PENDING_REVIEW:
            return (
                "Sua publicação está em análise antes de ficar visível na "
                "comunidade. Isso é rotina para parte dos envios e não "
                "significa que algo foi feito de errado."
            )
        return (
            "Não foi possível publicar este conteúdo no momento. Se você "
            "acredita que isso é um engano, é possível abrir um recurso."
        )
