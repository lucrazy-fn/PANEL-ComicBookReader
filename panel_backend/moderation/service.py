"""
ModerationService: ponto único de entrada do sistema de moderação.

Este é o único módulo que o resto do backend (rota de upload/publicação)
deveria importar. Ele:
  1. Roda todos os analisadores disponíveis sobre a submissão
  2. Combina os achados num único resultado
  3. Decide o status final (approved / pending_review / rejected)
  4. Persiste o registro para histórico/futura revisão manual
  5. Nunca decide "isto é ilegal" — só classifica risco (ver ModerationResult.public_message)
"""

from __future__ import annotations

from panel_backend.moderation.analyzers.ai_analyzer import AIAnalyzer
from panel_backend.moderation.analyzers.base import BaseAnalyzer
from panel_backend.moderation.analyzers.metadata_rules import MetadataRulesAnalyzer
from panel_backend.moderation.config import ModerationConfig
from panel_backend.moderation.models import (
    AnalyzerFinding,
    ModerationResult,
    ModerationStatus,
    PublicationSubmission,
    RiskLevel,
)
from panel_backend.moderation.storage import ModerationRecord, ModerationStore

_RISK_ORDER = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]


class ModerationService:
    def __init__(
        self,
        store: ModerationStore,
        analyzers: list[BaseAnalyzer] | None = None,
        config: ModerationConfig | None = None,
    ):
        self._store = store
        self._config = config or ModerationConfig.from_env()
        # Ordem dos analisadores na lista não importa para o resultado —
        # o pior risco encontrado por qualquer um deles prevalece.
        self._analyzers = analyzers or [
            MetadataRulesAnalyzer(),
            AIAnalyzer(self._config),
        ]

    def review(self, submission: PublicationSubmission) -> tuple[ModerationResult, ModerationRecord]:
        findings: list[AnalyzerFinding] = []

        for analyzer in self._analyzers:
            if not analyzer.is_available():
                continue
            try:
                findings.append(analyzer.analyze(submission))
            except NotImplementedError:
                # Analisadores ainda não implementados (ex: AIAnalyzer na v1)
                # são simplesmente pulados — não devem derrubar a triagem.
                continue
            except Exception as exc:  # noqa: BLE001
                # Falha real de um analisador (ex: API externa fora do ar)
                # também não deve travar a publicação inteira; registramos
                # como um finding de baixa confiança e seguimos.
                findings.append(
                    AnalyzerFinding(
                        analyzer_name=getattr(analyzer, "name", "unknown"),
                        risk_level=RiskLevel.LOW,
                        confidence=0.0,
                        reasons=[f"Analisador falhou durante a execução: {exc}"],
                    )
                )

        result = self._decide(submission, findings)
        record = self._store.save(result, publication_title=submission.title)
        return result, record

    def _decide(
        self, submission: PublicationSubmission, findings: list[AnalyzerFinding]
    ) -> ModerationResult:
        if not findings:
            # Nenhum analisador disponível/rodou — não aprova automaticamente
            # às cegas; manda para revisão humana por segurança.
            return ModerationResult(
                submission_user_id=submission.user_id,
                status=ModerationStatus.PENDING_REVIEW,
                risk_level=RiskLevel.MEDIUM,
                confidence=0.0,
                internal_justification=(
                    "Nenhum analisador retornou resultado; enviado para "
                    "revisão manual por precaução."
                ),
                findings=[],
            )

        worst = max(findings, key=lambda f: _RISK_ORDER.index(f.risk_level))
        # Confiança do resultado combinado = maior confiança entre os
        # analisadores que apontaram o risco mais alto encontrado.
        relevant = [f for f in findings if f.risk_level == worst.risk_level]
        confidence = max(f.confidence for f in relevant)

        status = self._status_from_risk(worst.risk_level, confidence)

        justification = " | ".join(
            f"[{f.analyzer_name}] {'; '.join(f.reasons)}" for f in findings
        )

        return ModerationResult(
            submission_user_id=submission.user_id,
            status=status,
            risk_level=worst.risk_level,
            confidence=confidence,
            internal_justification=justification,
            findings=findings,
        )

    def _status_from_risk(self, risk: RiskLevel, confidence: float) -> ModerationStatus:
        if risk == RiskLevel.HIGH and confidence >= self._config.auto_reject_threshold:
            return ModerationStatus.REJECTED
        if risk in (RiskLevel.MEDIUM, RiskLevel.HIGH):
            return ModerationStatus.PENDING_REVIEW
        if risk == RiskLevel.LOW and confidence < self._config.auto_pending_threshold:
            # Baixíssima confiança mesmo em risco baixo -> por segurança,
            # revisão humana em vez de aprovação automática.
            return ModerationStatus.PENDING_REVIEW
        return ModerationStatus.APPROVED
