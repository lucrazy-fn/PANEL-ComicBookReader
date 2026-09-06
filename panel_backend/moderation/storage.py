"""
Guarda o histórico de decisões de moderação — necessário desde já para
viabilizar (no futuro) revisão manual, denúncias e apelações (ponto 7 do
pedido original), mesmo que essas features ainda não existam.

A API usa SqlAlchemyModerationStore para manter a decisão na mesma transação
da publicação. JsonModerationStore continua disponível para demos e para
ler dados legados criados pelas primeiras versões.
"""

from __future__ import annotations

import json
import os
import uuid
import tempfile
import threading
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from panel_backend.moderation.db_models import ModerationRecordRow
from panel_backend.moderation.models import ModerationResult, ModerationStatus, RiskLevel


@dataclass
class ModerationRecord:
    """Uma decisão de moderação, associada a uma publicação, com histórico."""
    record_id: str
    publication_title: str
    user_id: str
    status: ModerationStatus
    risk_level: RiskLevel
    confidence: float
    internal_justification: str
    created_at: str
    # Preparado para o futuro: revisão manual sobrescreve o status automático
    manual_override_status: Optional[ModerationStatus] = None
    manual_override_reason: Optional[str] = None
    manual_reviewer_id: Optional[str] = None

    def effective_status(self) -> ModerationStatus:
        """Status que deve valer de fato — revisão manual tem prioridade."""
        return self.manual_override_status or self.status

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        d["risk_level"] = self.risk_level.value
        if self.manual_override_status:
            d["manual_override_status"] = self.manual_override_status.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "ModerationRecord":
        d = dict(d)
        d["status"] = ModerationStatus(d["status"])
        d["risk_level"] = RiskLevel(d["risk_level"])
        if d.get("manual_override_status"):
            d["manual_override_status"] = ModerationStatus(d["manual_override_status"])
        return cls(**d)


class ModerationStore:
    """
    Interface mínima de persistência. `JsonModerationStore` é a
    implementação v1; troque por uma baseada em banco depois sem alterar
    quem consome (`ModerationService`).
    """

    def save(self, result: ModerationResult, publication_title: str) -> ModerationRecord:
        raise NotImplementedError

    def get(self, record_id: str) -> Optional[ModerationRecord]:
        raise NotImplementedError

    def list_by_user(self, user_id: str) -> list[ModerationRecord]:
        raise NotImplementedError


class SqlAlchemyModerationStore(ModerationStore):
    """Persistência transacional usada pela API."""

    def __init__(self, db: Session):
        self._db = db

    @staticmethod
    def _to_record(row: ModerationRecordRow) -> ModerationRecord:
        return ModerationRecord(
            record_id=row.id,
            publication_title=row.publication_title,
            user_id=row.user_id,
            status=ModerationStatus(row.status),
            risk_level=RiskLevel(row.risk_level),
            confidence=row.confidence,
            internal_justification=row.internal_justification,
            created_at=row.created_at.isoformat(),
            manual_override_status=(
                ModerationStatus(row.manual_override_status)
                if row.manual_override_status else None
            ),
            manual_override_reason=row.manual_override_reason,
            manual_reviewer_id=row.manual_reviewer_id,
        )

    def save(self, result: ModerationResult, publication_title: str) -> ModerationRecord:
        row = ModerationRecordRow(
            publication_title=publication_title,
            user_id=result.submission_user_id,
            status=result.status.value,
            risk_level=result.risk_level.value,
            confidence=result.confidence,
            internal_justification=result.internal_justification,
            created_at=result.evaluated_at.replace(tzinfo=None),
        )
        self._db.add(row)
        self._db.flush()
        return self._to_record(row)

    def get(self, record_id: str) -> Optional[ModerationRecord]:
        row = self._db.get(ModerationRecordRow, record_id)
        return self._to_record(row) if row else None

    def list_by_user(self, user_id: str) -> list[ModerationRecord]:
        rows = self._db.scalars(
            select(ModerationRecordRow)
            .where(ModerationRecordRow.user_id == user_id)
            .order_by(ModerationRecordRow.created_at.desc())
        ).all()
        return [self._to_record(row) for row in rows]


class JsonModerationStore(ModerationStore):
    def __init__(self, file_path: str):
        self._file_path = file_path
        self._lock = threading.RLock()
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
        if not os.path.isfile(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load_all(self) -> list[dict]:
        with self._lock:
            with open(self._file_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _save_all(self, records: list[dict]) -> None:
        # Gravação atômica: uma interrupção não deixa o JSON pela metade.
        directory = os.path.dirname(os.path.abspath(self._file_path))
        with self._lock:
            fd, temp_path = tempfile.mkstemp(prefix="moderation-", suffix=".tmp", dir=directory)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(temp_path, self._file_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    def save(self, result: ModerationResult, publication_title: str) -> ModerationRecord:
        record = ModerationRecord(
            record_id=str(uuid.uuid4()),
            publication_title=publication_title,
            user_id=result.submission_user_id,
            status=result.status,
            risk_level=result.risk_level,
            confidence=result.confidence,
            internal_justification=result.internal_justification,
            created_at=result.evaluated_at.isoformat(),
        )
        # O lock cobre leitura + alteração + escrita para evitar perda de
        # registros quando duas requisições chegam ao mesmo tempo.
        with self._lock:
            records = self._load_all()
            records.append(record.to_dict())
            self._save_all(records)
        return record

    def get(self, record_id: str) -> Optional[ModerationRecord]:
        for raw in self._load_all():
            if raw["record_id"] == record_id:
                return ModerationRecord.from_dict(raw)
        return None

    def list_by_user(self, user_id: str) -> list[ModerationRecord]:
        return [
            ModerationRecord.from_dict(raw)
            for raw in self._load_all()
            if raw["user_id"] == user_id
        ]
