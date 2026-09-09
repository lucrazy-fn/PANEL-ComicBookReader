
from __future__ import annotations

import hashlib
import io
import os
import tempfile
import uuid
import zipfile
from pathlib import Path, PurePosixPath

from fastapi import UploadFile
from PIL import Image

ALLOWED_EXTENSIONS = {".cbz", ".zip", ".cbr", ".rar", ".pdf"}
MAX_UPLOAD_BYTES = int(os.environ.get("PANEL_MAX_UPLOAD_MB", "250")) * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = int(os.environ.get("PANEL_MAX_UNCOMPRESSED_MB", "1500")) * 1024 * 1024


class UnsafeAssetError(ValueError):
    pass


def storage_dir() -> Path:
    path = Path(os.environ.get("PANEL_STORAGE_DIR", "./panel_storage")).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


async def save_upload(upload: UploadFile) -> tuple[str, str, int, str]:
    original = Path(upload.filename or "quadrinho").name
    extension = Path(original).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise UnsafeAssetError("Formato não permitido. Use CBZ, CBR, ZIP, RAR ou PDF.")

    fd, temporary = tempfile.mkstemp(prefix="upload-", suffix=extension, dir=storage_dir())
    digest = hashlib.sha256()
    size = 0
    try:
        with os.fdopen(fd, "wb") as target:
            while chunk := await upload.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise UnsafeAssetError("Arquivo excede o limite de upload.")
                digest.update(chunk)
                target.write(chunk)
        _validate_file(Path(temporary), extension)
        stored_name = f"{uuid.uuid4().hex}{extension}"
        final_path = storage_dir() / stored_name
        os.replace(temporary, final_path)
        return stored_name, original, size, digest.hexdigest()
    finally:
        await upload.close()
        if os.path.exists(temporary):
            os.remove(temporary)


def resolve_asset(stored_name: str) -> Path:
    base = storage_dir()
    candidate = (base / Path(stored_name).name).resolve()
    if candidate.parent != base or not candidate.is_file():
        raise FileNotFoundError(stored_name)
    return candidate


def _validate_file(path: Path, extension: str) -> None:
    with path.open("rb") as source:
        header = source.read(8)


    if zipfile.is_zipfile(path):
        total = 0
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                member = PurePosixPath(info.filename.replace("\\", "/"))
                if member.is_absolute() or ".." in member.parts:
                    raise UnsafeAssetError("O arquivo contém caminhos inseguros.")
                total += info.file_size
                if total > MAX_UNCOMPRESSED_BYTES:
                    raise UnsafeAssetError("Conteúdo descompactado excede o limite seguro.")
                if info.compress_size and info.file_size / info.compress_size > 200:
                    raise UnsafeAssetError("Taxa de compressão suspeita (possível ZIP bomb).")
    elif header.startswith(b"Rar!"):
        return
    elif extension == ".pdf" and header.startswith(b"%PDF-"):
        return
    else:
        raise UnsafeAssetError("O conteúdo não corresponde a um quadrinho suportado.")


def cover_jpeg(path: Path, max_size: tuple[int, int] = (360, 520)) -> bytes:
    extension = path.suffix.lower()
    image_data: bytes
    image_exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif")
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            names = sorted(
                (name for name in archive.namelist() if Path(name).suffix.lower() in image_exts),
                key=str.casefold,
            )
            if not names:
                raise UnsafeAssetError("O quadrinho não contém imagens.")
            image_data = archive.read(names[0])
    elif extension in {".cbr", ".rar"}:
        import rarfile
        with rarfile.RarFile(path) as archive:
            names = sorted(
                (name for name in archive.namelist() if Path(name).suffix.lower() in image_exts),
                key=str.casefold,
            )
            if not names:
                raise UnsafeAssetError("O quadrinho não contém imagens.")
            image_data = archive.read(names[0])
    elif extension == ".pdf":
        import pymupdf
        document = pymupdf.open(path)
        try:
            if document.page_count == 0:
                raise UnsafeAssetError("PDF sem páginas.")
            pixmap = document[0].get_pixmap(matrix=pymupdf.Matrix(1.2, 1.2), alpha=False)
            image_data = pixmap.tobytes("png")
        finally:
            document.close()
    else:
        raise UnsafeAssetError("Formato sem suporte para capa.")

    with Image.open(io.BytesIO(image_data)) as image:
        image = image.convert("RGB")
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(output, "JPEG", quality=85, optimize=True)
        return output.getvalue()
