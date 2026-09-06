"""
Guarda a sessão (token + dados básicos do usuário) localmente, no mesmo
padrão de pasta que o resto do ComicReader.py já usa
(%APPDATA%/Panel/*.json). Assim o usuário não precisa logar de novo toda
vez que abre o app — igual funciona hoje com prefs.json.

Ausência de sessão salva = modo convidado. Nunca é tratado como erro.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from typing import Optional

_APPDATA = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Panel")
os.makedirs(_APPDATA, exist_ok=True)
SESSION_FILE = os.path.join(_APPDATA, "auth_session.json")


@dataclass
class LocalSession:
    token: str
    user_id: str
    username: str
    display_name: str
    is_moderator: bool = False
    role: str = "user"


def load_session() -> Optional[LocalSession]:
    if not os.path.isfile(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return LocalSession(**data)
    except Exception:
        # Arquivo corrompido/formato antigo -> trata como "sem sessão",
        # nunca trava o app por causa disso.
        return None


def save_session(session: LocalSession) -> None:
    fd, temp_path = tempfile.mkstemp(prefix="session-", suffix=".tmp", dir=_APPDATA)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(asdict(session), f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, SESSION_FILE)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def clear_session() -> None:
    if os.path.isfile(SESSION_FILE):
        os.remove(SESSION_FILE)
