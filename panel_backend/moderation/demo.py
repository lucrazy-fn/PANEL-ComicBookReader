"""
Demonstração manual do fluxo de moderação. Rode com:
    python -m panel_backend.moderation.demo

Não é um teste automatizado formal (isso viria depois, com pytest) —
serve só para você ver o sistema funcionando de ponta a ponta e revisar
se as decisões fazem sentido antes de integrar ao resto do backend.
"""

from __future__ import annotations

from panel_backend.moderation.models import PublicationSubmission
from panel_backend.moderation.service import ModerationService
from panel_backend.moderation.storage import JsonModerationStore


def _print_result(label: str, result, record):
    print(f"\n--- {label} ---")
    print(f"status: {result.status.value}")
    print(f"risk_level: {result.risk_level.value}  |  confidence: {result.confidence}")
    print(f"mensagem pública: {result.public_message()}")
    print(f"justificativa interna: {result.internal_justification}")
    print(f"record_id salvo: {record.record_id}")


def main():
    store = JsonModerationStore("./_demo_moderation_records.json")
    service = ModerationService(store=store)

    # Cenário 1: obra autoral original, tudo declarado -> deve aprovar
    original = PublicationSubmission(
        user_id="user-1",
        title="As Aventuras de Zeca Lagarta",
        author="Maria Autora",
        description="Uma HQ autoral sobre um lagarta filósofo.",
        tags=["autoral", "comédia"],
        authorship_declared=True,
        license="CC-BY-4.0",
    )
    _print_result("Obra original, com declaração", *service.review(original))

    # Cenário 2: título muito parecido com obra conhecida -> deve rejeitar/pending
    suspeito = PublicationSubmission(
        user_id="user-2",
        title="Batman",
        author="Desconhecido",
        description="Upload sem mais detalhes.",
        authorship_declared=False,
    )
    _print_result("Título batendo com obra conhecida", *service.review(suspeito))

    # Cenário 3: sem declaração de autoria, mas título neutro -> pending_review
    duvidoso = PublicationSubmission(
        user_id="user-3",
        title="Crônicas da Cidade Cinza",
        author="?",
        description="Achei esse arquivo e quero compartilhar.",
        authorship_declared=False,
    )
    _print_result("Sem declaração de autoria, título neutro", *service.review(duvidoso))


if __name__ == "__main__":
    main()
