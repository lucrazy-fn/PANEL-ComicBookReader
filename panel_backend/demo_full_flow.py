
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

        try:
            auth = accounts.register_user(db, username="maria_autora", password="senha-forte-123")
            print(f"Conta criada: {auth.user.username} (id={auth.user.id})")
        except accounts.UsernameTakenError:
            auth = accounts.authenticate(db, username="maria_autora", password="senha-forte-123")
            print(f"Login realizado: {auth.user.username}")


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
