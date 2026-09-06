"""
Demonstração do fluxo completo: cadastro -> login -> envio de quadrinho
-> moderação -> publicação. Rode com:

    python -m panel_backend.demo_full_flow

Usa SQLite local (panel.db, criado na primeira execução) e o JSON de
moderação (_demo_moderation_records.json). Apague os dois se quiser
recomeçar do zero.
"""

from __future__ import annotations

from panel_backend.accounts import service as accounts
from panel_backend.catalog import service as catalog
from panel_backend.catalog.models import Comic, Publication  # noqa: F401 (garante registro no metadata)
from panel_backend.db import get_session, init_db
from panel_backend.moderation.service import ModerationService
from panel_backend.moderation.storage import JsonModerationStore


def main():
    init_db()
    moderation_service = ModerationService(store=JsonModerationStore("./_demo_moderation_records.json"))

    with get_session() as db:
        # 1. Cadastro (ou login, se já existir de uma execução anterior)
        try:
            auth = accounts.register_user(db, username="maria_autora", password="senha-forte-123")
            print(f"Conta criada: {auth.user.username} (id={auth.user.id})")
        except accounts.UsernameTakenError:
            auth = accounts.authenticate(db, username="maria_autora", password="senha-forte-123")
            print(f"Login realizado: {auth.user.username}")

        # 2. Envio de um quadrinho autoral, com declaração e licença
        outcome = catalog.submit_publication(
            db,
            moderation_service=moderation_service,
            user_id=auth.user.id,
            data=catalog.SubmissionInput(
                title="As Aventuras de Zeca Lagarta",
                author="Maria Autora",
                description="HQ autoral sobre um lagarta filósofo.",
                tags=["autoral", "comédia"],
                file_reference="/uploads/zeca-lagarta-cap1.cbz",
                authorship_declared=True,
                license="CC-BY-4.0",
            ),
        )
        print(f"\nComic criado: {outcome.comic.title} (id={outcome.comic.id})")
        print(f"Publication status: {outcome.publication.status}")
        print(f"Visível na comunidade? {outcome.publication.is_visible_to_community()}")
        print(f"Mensagem pública: {outcome.public_message}")

        # 3. Tentativa suspeita, pelo mesmo usuário
        outcome2 = catalog.submit_publication(
            db,
            moderation_service=moderation_service,
            user_id=auth.user.id,
            data=catalog.SubmissionInput(
                title="Naruto",
                author="?",
                description="upload rápido",
                tags=[],
                file_reference="/uploads/naruto-cap1.cbz",
                authorship_declared=False,
            ),
        )
        print(f"\nComic criado: {outcome2.comic.title} (id={outcome2.comic.id})")
        print(f"Publication status: {outcome2.publication.status}")
        print(f"Visível na comunidade? {outcome2.publication.is_visible_to_community()}")
        print(f"Mensagem pública: {outcome2.public_message}")


if __name__ == "__main__":
    main()
