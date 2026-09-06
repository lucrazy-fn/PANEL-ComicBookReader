"""
╔══════════════════════════════════════╗
║         PANEL — CBZ/CBR Reader       ║
║   Zoom · Drag · Page Nav · Themes    ║
╚══════════════════════════════════════╝
Requires: pip install pillow rarfile
Opcional (PDF): pip install pymupdf
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import zipfile
import os, sys, io, json, time, threading, hashlib, re, shutil, logging
from pathlib import Path
from collections import deque

from panel_app.storage import (
    APPDATA_DIR as _APPDATA, BOOKMARKS_FILE, COVER_CACHE_DIR, FAVORITES_FILE,
    LIBRARY_CONFIG_FILE, MANUAL_STATUS_FILE, PREFS_FILE, PROGRESS_FILE,
    collection_progress, collection_read_count, export_backup, get_bookmarks,
    get_manual_status, get_progress_page, import_backup, is_favorite,
    json_load as _json_load, json_save as _json_save, load_bookmarks,
    load_favorites, load_manual_status, load_prefs, load_progress, save_prefs,
    save_progress, set_manual_status, toggle_bookmark, toggle_favorite,
    register_change_listener,
)
from panel_app.account_views import render_notifications, render_profile
from panel_app.sync import build_sync_payload, content_id
from panel_app.reader import load_state as load_reader_state, save_state as save_reader_state
from panel_app.downloads import manager as download_manager, render_downloads
from panel_app.community import load_catalog, save_catalog
from panel_app.moderation import can_moderate

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("panel")
log.setLevel(logging.DEBUG)

try:
    import rarfile
    HAS_RAR = True
except ImportError:
    HAS_RAR = False

try:
    try:
        import pymupdf as fitz
    except ImportError:  # compatibilidade com versões antigas do PyMuPDF
        import fitz
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance
except ImportError:
    print("Pillow não encontrado. Instale com: pip install pillow")
    sys.exit(1)

def resource_path(relative_path):
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

def _setup_unrar():
    if not HAS_RAR:
        return
    candidates = [
        r"C:\Program Files\WinRAR\UnRAR.exe",
        r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
        shutil.which("unrar"),
        shutil.which("UnRAR"),
        shutil.which("bsdtar"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            rarfile.UNRAR_TOOL = c
            return

_setup_unrar()


def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r'(\d+)', str(s))]


LANG = "pt"
TEXTS = {
    "en": {
        "library": "Library", "collections": "Collections", "theme": "Theme",
        "fit": "⊞ Fit", "fullscreen": "⛶ Fullscreen",
        "language": "Choose Language", "choose_library_folder": "Choose Library Folder",
        "error": "Error", "back": "← Back",
        "no_comics": "No comics found", "add_folder": "Choose a folder",
        "light": "Light Mode", "dark": "Dark Mode", "folder": "Folder",
        "manga_off": "🇯🇵 Manga OFF", "manga_on": "🇯🇵 Manga ON",
        "no_collections": "No collections found", "issues": "issue", "back_collections": "← Collections",
        "all": "All", "subfolders": "Folders", "series": "Series",
        "sort_name": "Name", "sort_date": "Date", "sort_progress": "Progress",
        "read": "read", "continue_reading": "▶ Continue", "sort_by": "Sort:",
        "unread": "Unread", "search": "Search…", "no_results": "No results for",
        "loading": "Loading…", "continue_section": "Continue Reading",
        "next_issue": "Next issue", "next_chapter_q": "Next issue of the series?",
        "yes": "Yes", "no": "No", "bookmark": "Bookmark", "immersive": "Immersive",
        "rotate": "Rotate", "brightness": "Brightness", "double_page": "Double Page",
        "filter_status": "Status", "f_all": "All", "f_unread": "Unread",
        "f_reading": "Reading", "f_done": "Done",
    },
    "pt": {
        "library": "Biblioteca", "collections": "Coleções", "theme": "Tema",
        "fit": "⊞ Encaixar", "fullscreen": "⛶ Tela Cheia",
        "language": "Escolha o Idioma", "choose_library_folder": "Escolher Pasta",
        "error": "Erro", "back": "← Voltar",
        "no_comics": "Nenhuma história encontrada", "add_folder": "Escolher pasta",
        "light": "Modo Claro", "dark": "Modo Escuro", "folder": "Pasta",
        "manga_off": "🇯🇵 Mangá OFF", "manga_on": "🇯🇵 Mangá ON",
        "no_collections": "Nenhuma coleção encontrada", "issues": "edição", "back_collections": "← Coleções",
        "all": "Todas", "subfolders": "Pastas", "series": "Séries",
        "sort_name": "Nome", "sort_date": "Data", "sort_progress": "Progresso",
        "read": "lidas", "continue_reading": "▶ Continuar", "sort_by": "Ordenar:",
        "unread": "Não lido", "search": "Buscar…", "no_results": "Nenhum resultado para",
        "loading": "Carregando…", "continue_section": "Continuar Lendo",
        "next_issue": "Próxima edição", "next_chapter_q": "Próxima edição da série?",
        "yes": "Sim", "no": "Não", "bookmark": "Marcador", "immersive": "Imersivo",
        "rotate": "Girar", "brightness": "Brilho", "double_page": "Página Dupla",
        "filter_status": "Status", "f_all": "Todos", "f_unread": "Não lidos",
        "f_reading": "Lendo", "f_done": "Concluídos",
    },
}

DARK = {
    "bg": "#0d0d12", "surface": "#161620", "surface_alt": "#1e1e2c",
    "surface_hover": "#252536", "border": "#2a2a40", "border_glow": "#c44a2a",
    "accent": "#cc2222", "accent2": "#ff6644",
    "text": "#ede8e0", "text_dim": "#6b6680", "text_muted": "#3a3850",
    "canvas_bg": "#07070e", "btn_hover": "#2a2a3e",
    "progress_bg": "#1e1e2c", "shadow": "#000000", "shadow_light": "#1a1a2e",
    "read_badge": "#2a5c3a", "read_badge_text": "#5dde8a",
    "search_bg": "#1a1a28",
}
LIGHT = {
    "bg": "#f0ede8", "surface": "#ffffff", "surface_alt": "#f7f5f2",
    "surface_hover": "#ede9e4", "border": "#d4cfc8", "border_glow": "#d4603e",
    "accent": "#cc2222", "accent2": "#ff6644",
    "text": "#1a1812", "text_dim": "#8a8070", "text_muted": "#ccc8c0",
    "canvas_bg": "#e8e4de", "btn_hover": "#e5e0d8",
    "progress_bg": "#e0dbd4", "shadow": "#aaaaaa", "shadow_light": "#d4cfc8",
    "read_badge": "#d4f0dc", "read_badge_text": "#1a7a3a",
    "search_bg": "#f0ede8",
}

# Fonte canônica extraída; os aliases locais preservam a compatibilidade
# durante a migração das telas restantes.
from panel_app.themes import DARK as DARK, LIGHT as LIGHT, TEXTS as TEXTS

IS_DARK = True
THEME = DARK.copy()

def toggle_theme():
    global IS_DARK, THEME
    IS_DARK = not IS_DARK
    new = DARK if IS_DARK else LIGHT
    THEME.clear()
    THEME.update(new)

def current_theme_label():
    return TEXTS[LANG]["light"] if IS_DARK else TEXTS[LANG]["dark"]

LIBRARY_FOLDER      = ""

ICON_PATH = Path(resource_path("Icons"))
ICONS = {}

def load_icons(size=(18, 18)):
    global ICONS
    icon_files = {
        "library": "library.png", "collections": "collections.png",
        "next": "next.png", "open": "open.png", "prev": "prev.png",
        "theme": "theme.png", "zoom_in": "zoom_in.png", "zoom_out": "zoom_out.png",
        "backup": "backup.png", "restore": "restore.png", "favorited": "favorited.png",
    }
    for name, filename in icon_files.items():
        path = ICON_PATH / filename
        if path.exists():
            try:
                img = Image.open(path).convert("RGBA").resize(size, Image.BILINEAR)
                ICONS[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Erro ao carregar ícone {filename}: {e}")
                ICONS[name] = None
        else:
            ICONS[name] = None


import platform
_OS = platform.system()
_SANS = "Segoe UI" if _OS == "Windows" else ("SF Pro Text" if _OS == "Darwin" else "DejaVu Sans")
_MONO = "Consolas" if _OS == "Windows" else ("Menlo" if _OS == "Darwin" else "DejaVu Sans Mono")

FLOGO  = ("Georgia", 18, "bold")
FTITLE = ("Georgia", 20, "bold")
FBTN   = (_SANS, 10, "bold")
FLABEL = (_SANS, 10)
FSMALL = (_SANS, 9)
FTINY  = (_SANS, 8)
FPAGE  = (_MONO, 11, "bold")

CAPA_W, CAPA_H = 160, 220
CARD_R  = 12
GPAD    = 14

FADE_SPEED   = 0.18
EASING_POWER = 4

_PLACEHOLDER_PIL = None

def get_placeholder_pil() -> Image.Image:
    global _PLACEHOLDER_PIL
    if _PLACEHOLDER_PIL is None:
        bg_hex = THEME["surface_alt"].lstrip("#")
        bg_rgb = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
        img = Image.new("RGB", (CAPA_W, CAPA_H), bg_rgb)
        d = ImageDraw.Draw(img)
        cx, cy = CAPA_W // 2, CAPA_H // 2
        d.rectangle([cx-28, cy-36, cx+28, cy+36], outline=(100, 100, 120), width=2)
        d.line([cx, cy-36, cx, cy+36], fill=(80, 80, 100), width=1)
        _PLACEHOLDER_PIL = img
    return _PLACEHOLDER_PIL


IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}

class ArchiveBackend:
    """
    Abstrai o acesso ao arquivo (zip/rar/pdf).
    NÃO guarda bytes de páginas — só os nomes das entradas.
    Extrai bytes sob demanda via read_page(idx).
    """
    def __init__(self, path: str):
        self.path = path
        self.kind = None
        self.names = []
        self._pdf_doc = None
        try:
            self._detect()
        except Exception:
            self.close()
            raise

    def _detect(self):
        suffix = Path(self.path).suffix.lower()
        if zipfile.is_zipfile(self.path):
            self.kind = "zip"
            with zipfile.ZipFile(self.path, "r") as z:
                self.names = sorted(
                    [n for n in z.namelist()
                     if Path(n).suffix.lower() in IMG_EXTS
                     and not Path(n).name.startswith(".")],
                    key=natural_key)
        elif HAS_RAR and rarfile.is_rarfile(self.path):
            self.kind = "rar"
            with rarfile.RarFile(self.path, "r") as r:
                self.names = sorted(
                    [n for n in r.namelist()
                     if Path(n).suffix.lower() in IMG_EXTS
                     and not Path(n).name.startswith(".")],
                    key=natural_key)
        elif HAS_PDF and suffix == ".pdf":
            self.kind = "pdf"
            self._pdf_doc = fitz.open(self.path)
            self.names = [f"page_{i}" for i in range(self._pdf_doc.page_count)]
        else:
            raise ValueError(f"Formato não suportado: {suffix}")

    @property
    def count(self) -> int:
        return len(self.names)

    def read_page(self, idx: int) -> bytes:
        """Retorna os bytes da página idx (decodificável pelo PIL)."""
        if not (0 <= idx < self.count):
            raise IndexError(idx)
        if self.kind == "zip":
            with zipfile.ZipFile(self.path, "r") as z:
                return z.read(self.names[idx])
        elif self.kind == "rar":
            with rarfile.RarFile(self.path, "r") as r:
                return r.read(self.names[idx])
        elif self.kind == "pdf":
            page = self._pdf_doc.load_page(idx)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            return pix.tobytes("png")
        raise ValueError("backend inválido")

    def close(self):
        if self._pdf_doc:
            try: self._pdf_doc.close()
            except Exception as _e: log.debug("silenced: %s", _e)
            self._pdf_doc = None


def extract_cover_only(path: str) -> bytes:
    """Lê só a primeira página (capa) — usado em listagens."""
    suffix = Path(path).suffix.lower()
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path, "r") as z:
            names = sorted([n for n in z.namelist()
                            if Path(n).suffix.lower() in IMG_EXTS
                            and not Path(n).name.startswith(".")], key=natural_key)
            if names:
                return z.read(names[0])
    if HAS_RAR and rarfile.is_rarfile(path):
        with rarfile.RarFile(path, "r") as r:
            names = sorted([n for n in r.namelist()
                            if Path(n).suffix.lower() in IMG_EXTS
                            and not Path(n).name.startswith(".")], key=natural_key)
            if names:
                return r.read(names[0])
    if HAS_PDF and suffix == ".pdf":
        doc = fitz.open(path)
        try:
            if doc.page_count:
                pix = doc.load_page(0).get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                return pix.tobytes("png")
        finally:
            doc.close()
    raise ValueError(f"Formato não suportado: {suffix}")


def pil_from_bytes(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGBA")


def rounded_image(img: Image.Image, r: int) -> Image.Image:
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(img.convert("RGBA"), mask=mask)
    return out


def ease_out(t):  return 1 - pow(1 - t, EASING_POWER)
def ease_in_out(t):
    if t < 0.5: return 2 * t * t
    return 1 - pow(-2 * t + 2, 2) / 2
def lerp(a, b, t): return a + (b - a) * t


class SmartPageLoader:
    """
    Carrega páginas sob demanda mantendo só uma janela em RAM.
    Decodifica em thread; entrega PIL.Image (não PhotoImage, pra ser thread-safe).
    """
    WINDOW = 4

    def __init__(self, path: str):
        self.backend = ArchiveBackend(path)
        self._cache = {}
        self._lock = threading.Lock()
        self._prefetching = set()

    @property
    def count(self):
        return self.backend.count

    @property
    def names(self):
        return self.backend.names

    @property
    def entries(self):
        return self.backend.names

    def get_pil(self, idx: int) -> Image.Image:
        with self._lock:
            if idx in self._cache:
                return self._cache[idx]
        img = pil_from_bytes(self.backend.read_page(idx))
        with self._lock:
            self._cache[idx] = img
            self._trim(idx)
        return img

    def _trim(self, center: int):
        keep = set(range(center - self.WINDOW, center + self.WINDOW + 1))
        for k in list(self._cache.keys()):
            if k not in keep:
                del self._cache[k]

    def prefetch(self, idx: int):
        """Pré-carrega página em background (não bloqueia)."""
        if not (0 <= idx < self.count):
            return
        with self._lock:
            if idx in self._cache or idx in self._prefetching:
                return
            self._prefetching.add(idx)

        def work():
            try:
                img = pil_from_bytes(self.backend.read_page(idx))
                with self._lock:
                    self._cache[idx] = img
            except Exception as e:
                print("prefetch err:", e)
            finally:
                with self._lock:
                    self._prefetching.discard(idx)

        threading.Thread(target=work, daemon=True).start()

    def get_thumbnail_pil(self, idx, tw, th):
        cache_file = _cover_cache_path(self.backend.path)
        if idx == 0 and os.path.exists(cache_file):
            try:
                img = Image.open(cache_file).convert("RGB")
                img.thumbnail((tw, th), Image.BILINEAR)
                return img
            except Exception:
                pass
        img = pil_from_bytes(self.backend.read_page(idx)).convert("RGB")
        img.thumbnail((tw, th), Image.BILINEAR)
        return img

    def close(self):
        self.backend.close()
        with self._lock:
            self._cache.clear()

# Implementações canônicas extraídas do monólito. As definições antigas acima
# serão removidas quando os consumidores restantes estiverem migrados.
from panel_app.archive import (
    ArchiveBackend as ArchiveBackend,
    SmartPageLoader as SmartPageLoader,
    extract_cover_only as extract_cover_only,
    pil_from_bytes as pil_from_bytes,
    rounded_image as rounded_image,
)


def load_library_config():
    global LIBRARY_FOLDER, LANG, IS_DARK, THEME
    cfg = _json_load(LIBRARY_CONFIG_FILE, {})
    if "library_folder" in cfg and os.path.isdir(cfg["library_folder"]):
        LIBRARY_FOLDER = cfg["library_folder"]
    prefs = load_prefs()
    if prefs.get("lang") in ("pt", "en"):
        LANG = prefs["lang"]
    if "dark" in prefs:
        IS_DARK = prefs["dark"]
        THEME.clear()
        THEME.update(DARK if IS_DARK else LIGHT)

def save_library_config(path):
    global LIBRARY_FOLDER
    LIBRARY_FOLDER = path
    _json_save(LIBRARY_CONFIG_FILE, {"library_folder": path})


def _cover_cache_path(comic_path: str) -> str:
    try:
        mtime = os.path.getmtime(comic_path)
    except OSError:
        mtime = 0
    theme_id = "dark" if IS_DARK else "light"
    key = f"{comic_path}|{mtime}|{CAPA_W}x{CAPA_H}|{theme_id}"
    h = hashlib.md5(key.encode("utf-8")).hexdigest()
    return os.path.join(COVER_CACHE_DIR, f"{h}.webp")


def make_pill(parent, text, cmd, *, icon=None, variant="ghost",
              font=FSMALL, pad_x=14, pad_y=8, min_w=0, active=False):
    c = THEME
    host_bg = parent.cget("bg")
    if variant == "accent":
        base_fill, hover_fill = c["accent"], c["accent2"]
        base_fg, hover_fg = "#ffffff", "#ffffff"
        base_outline = ""
    elif variant == "soft":
        base_fill, hover_fill = c["surface_alt"], c["surface_hover"]
        base_fg, hover_fg = c["text"], c["text"]
        base_outline = c["border"]
    else:
        base_fill, hover_fill = host_bg, c["surface_hover"]
        base_fg, hover_fg = c["text_dim"], c["text"]
        base_outline = c["border"]

    tmp = tk.Label(parent, text=text, font=font)
    tmp_w = tmp.winfo_reqwidth(); tmp_h = tmp.winfo_reqheight()
    tmp.destroy()
    icon_w = (icon.width() + 8) if icon else 0
    w = max(min_w, tmp_w + icon_w + pad_x * 2)
    h = tmp_h + pad_y * 2
    r = h // 2

    cv = tk.Canvas(parent, width=w, height=h, bg=host_bg,
                   highlightthickness=0, cursor="hand2", takefocus=0)
    cv._pill_text = text
    cv._pill_active = bool(active)

    def render(fill, fg, outline):
        cv.delete("all")
        _rrect(cv, 1, 1, w - 1, h - 1, r, fill=fill)
        if outline:
            _rrect(cv, 1, 1, w - 2, h - 2, r, outline=outline, width=1)
        if icon:
            ix = pad_x + icon.width() // 2
            cv.create_image(ix, h // 2, image=icon)
            cv.create_text(ix + icon.width() // 2 + 6, h // 2,
                           text=cv._pill_text, font=font, fill=fg, anchor="w")
        else:
            cv.create_text(w // 2, h // 2, text=cv._pill_text, font=font, fill=fg)

    def _normal():
        if cv._pill_active and variant != "accent":
            render(c["accent"], "#ffffff", c["accent"])
        else:
            render(base_fill, base_fg, base_outline)

    def set_text(t):
        cv._pill_text = t
        _normal()

    def set_active(flag):
        cv._pill_active = bool(flag)
        _normal()

    cv.pill_set_text = set_text
    cv.pill_set_active = set_active
    _normal()
    cv.bind("<Enter>", lambda e: (None if cv._pill_active and variant != "accent"
                                  else render(hover_fill, hover_fg,
                                              hover_fill if variant != "ghost" else c["border_glow"])))
    cv.bind("<Leave>", lambda e: _normal())
    cv.bind("<Button-1>", lambda e: cmd())
    return cv


class CoverLoader:
    def __init__(self, root: tk.Tk, cache: dict):
        self._root = root
        self._cache = cache
        self._queue = deque()
        self._lock = threading.Lock()
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def request(self, path, callback):
        if path in self._cache:
            self._root.after(0, lambda: callback(path, self._cache[path]))
            return
        with self._lock:
            if not any(p == path for p, _ in self._queue):
                self._queue.append((path, callback))

    def clear_queue(self):
        with self._lock:
            self._queue.clear()

    def stop(self):
        self._running = False

    def _worker(self):
        while self._running:
            item = None
            with self._lock:
                if self._queue:
                    item = self._queue.popleft()
            if item:
                path, callback = item
                pil = self._load(path)
                self._cache[path] = pil
                if self._root.winfo_exists():
                    self._root.after(0, lambda p=path, i=pil, cb=callback: cb(p, i))
            else:
                time.sleep(0.02)

    def _load(self, path):
        cache_file = _cover_cache_path(path)
        if os.path.exists(cache_file):
            try:
                return Image.open(cache_file).convert("RGB")
            except Exception:
                pass
        try:
            data = extract_cover_only(path)
            img = Image.open(io.BytesIO(data)).convert("RGB")
            img.thumbnail((CAPA_W, CAPA_H), Image.BILINEAR)
            bg_hex = THEME["surface_alt"].lstrip("#")
            bg_rgb = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
            bg = Image.new("RGB", (CAPA_W, CAPA_H), bg_rgb)
            px = (CAPA_W - img.width) // 2
            py = (CAPA_H - img.height) // 2
            bg.paste(img, (px, py))
            mask_img = Image.new("L", (CAPA_W, CAPA_H), 0)
            ImageDraw.Draw(mask_img).rounded_rectangle(
                [0, 0, CAPA_W-1, CAPA_H-1], radius=CARD_R, fill=255)
            result = Image.new("RGB", (CAPA_W, CAPA_H), bg_rgb)
            result.paste(bg, mask=mask_img)
            try:
                result.save(cache_file, "WEBP", quality=85)
            except Exception:
                pass
            return result
        except Exception as e:
            print("Erro lazy capa:", e)
            return None


try:
    from panel_client import api_client, session_store
    _ACCOUNTS_AVAILABLE = True
except ImportError:
    # panel_client não instalado (ex: dependência 'requests' ausente) ->
    # o app continua 100% funcional no modo convidado, sem tela de conta.
    _ACCOUNTS_AVAILABLE = False


def _draw_field_icon(cv, kind, cx, cy, s, color):
    """Ícone vetorial simples (sem depender de arquivo de imagem), no
    mesmo espírito monocromático dos ícones da barra lateral."""
    if kind == "user":
        cv.create_oval(cx - s*0.26, cy - s*0.5, cx + s*0.26, cy - s*0.04,
                        outline=color, width=1.6)
        cv.create_arc(cx - s*0.5, cy - s*0.05, cx + s*0.5, cy + s*0.75,
                       start=0, extent=180, style="arc", outline=color, width=1.6)
    elif kind == "mail":
        cv.create_rectangle(cx - s*0.5, cy - s*0.32, cx + s*0.5, cy + s*0.32,
                             outline=color, width=1.6)
        cv.create_line(cx - s*0.5, cy - s*0.3, cx, cy + s*0.08, cx + s*0.5, cy - s*0.3,
                        fill=color, width=1.6)
    elif kind == "lock":
        cv.create_rectangle(cx - s*0.38, cy - s*0.02, cx + s*0.38, cy + s*0.48,
                             outline=color, width=1.6)
        cv.create_arc(cx - s*0.26, cy - s*0.5, cx + s*0.26, cy + s*0.02,
                       start=0, extent=180, style="arc", outline=color, width=1.6)


class AuthWindow(tk.Toplevel):
    """
    Tela inicial: entrar, criar conta, ou continuar como convidado.
    Um cartão único com abas (Entrar/Cadastrar) trocando o conteúdo do
    formulário; "continuar como convidado" fica fora do cartão, sempre
    visível. Ao terminar, chama self.cb(user) e se destrói — user=None
    significa convidado, igual antes.
    """
    W, H = 400, 660
    CARD_W = 320

    def __init__(self, master, cb):
        super().__init__(master)
        try: self.iconbitmap(resource_path("panel.ico"))
        except Exception as _e: log.debug("silenced: %s", _e)
        self.cb = cb
        self.title("PANEL")
        self.configure(bg=THEME["bg"])
        self.resizable(True, True)
        self.minsize(self.W, self.H)
        self.grab_set()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{self.W}x{self.H}+{(sw-self.W)//2}+{(sh-self.H)//2}")

        self._mode = "login"          # "login" | "register"
        self._status_text = ""
        self._status_error = False
        self._entries = {}            # nome -> (entry, placeholder)
        self._fullscreen = False
        self._auth_in_progress = False
        self._last_size = None
        self._resize_job = None

        self.bind("<F11>", self._toggle_fullscreen)
        self.bind("<Escape>", self._exit_fullscreen)
        self.bind("<Configure>", self._on_configure)

        self._build()

    # ---------- janela ----------

    def _current_size(self):
        w, h = self.winfo_width(), self.winfo_height()
        if w <= 1 or h <= 1:
            return self.W, self.H
        return w, h

    def _on_configure(self, event):
        if event.widget is not self:
            return
        size = (event.width, event.height)
        if size == self._last_size:
            return
        self._last_size = size
        if self._resize_job:
            self.after_cancel(self._resize_job)
        # debounce: só reconstrói quando o redimensionamento se estabiliza,
        # pra não recalcular a cada pixel arrastado
        self._resize_job = self.after(120, self._build)

    def _toggle_fullscreen(self, event=None):
        self._fullscreen = not self._fullscreen
        self.attributes("-fullscreen", self._fullscreen)

    def _exit_fullscreen(self, event=None):
        if self._fullscreen:
            self._fullscreen = False
            self.attributes("-fullscreen", False)

    # ---------- construção ----------

    def _scale_factor(self, W, H):
        """
        Fator de escala do cartão em relação ao tamanho base (400x660).
        Usa o menor dos dois eixos pra o cartão nunca estourar a janela
        em nenhuma direção (mesmo com proporção bem larga ou bem alta),
        e nunca fica menor que 1x nem passa de 1.6x (senão fica gigante
        e vazio numa tela ultrawide).
        """
        factor = min(W / self.W, H / self.H)
        return max(1.0, min(factor, 1.6))

    @staticmethod
    def _sf(font, scale):
        family, size, *rest = font
        return (family, max(1, round(size * scale)), *rest)

    def _build(self):
        self._resize_job = None
        saved_values = self._capture_values()
        for w in self.winfo_children():
            w.destroy()
        c = THEME
        W, H = self._current_size()
        scale = self._scale_factor(W, H)

        f_logo  = self._sf(FLOGO, scale)
        f_btn   = self._sf(FBTN, scale)
        f_label = self._sf(FLABEL, scale)
        f_tiny  = self._sf(FTINY, scale)
        f_entry = self._sf(FSMALL, scale)

        card_w = round(self.CARD_W * scale)
        card_x = (W - card_w) // 2
        card_y = round(92 * scale)

        # ---- fase 1: calcular posições (sem desenhar), tudo em função de scale ----
        tab_pad = round(16 * scale)
        tab_h = round(38 * scale)
        tab_y0, tab_y1 = card_y + round(16 * scale), card_y + round(54 * scale)
        ax, ay, ar = W // 2, tab_y1 + round(44 * scale), round(30 * scale)
        field_y = ay + ar + round(24 * scale)
        field_h = round(42 * scale)
        field_spacing = round(12 * scale)
        # Cadastro e login possuem três campos. O login ganhou o código
        # 2FA opcional; manter "2" aqui fazia o botão ser desenhado por
        # cima do terceiro campo.
        n_fields = 3
        field_y_end = field_y + n_fields * field_h + (n_fields - 1) * field_spacing
        status_y = field_y_end + round(20 * scale)
        btn_y = status_y + round(32 * scale)
        switch_y = btn_y + round(30 * scale)
        card_h = (switch_y + round(20 * scale)) - card_y
        guest_y = card_y + card_h + round(34 * scale)

        cv = tk.Canvas(self, width=W, height=H, bg=c["bg"], highlightthickness=0)
        cv.pack(fill="both", expand=True)
        self._cv = cv

        # ---- fase 2: desenhar ----
        cv.create_text(W//2, round(40*scale), text="◈ PANEL", font=f_logo, fill=c["text"])
        cv.create_text(W//2, round(64*scale), text="Sua biblioteca de quadrinhos", font=f_tiny, fill=c["text_dim"])
        cv.create_text(W - 14, H - 14, text="F11 tela cheia", font=FTINY, fill=c["text_dim"], anchor="se")

        card_radius = round(22 * scale)
        _rrect(cv, card_x+4, card_y+6, card_x+card_w+4, card_y+card_h+6, card_radius, fill=c["shadow_light"])
        _rrect(cv, card_x, card_y, card_x+card_w, card_y+card_h, card_radius, fill=c["surface"])

        # ---- abas segmentadas (Entrar / Cadastrar) ----
        tab_x0, tab_x1 = card_x + tab_pad, card_x + card_w - tab_pad
        _rrect(cv, tab_x0, tab_y0, tab_x1, tab_y1, (tab_y1-tab_y0)//2, fill=c["surface_alt"])
        half_w = (tab_x1 - tab_x0) / 2
        active_x0 = tab_x0 if self._mode == "login" else tab_x0 + half_w
        _rrect(cv, active_x0 + 2, tab_y0 + 2, active_x0 + half_w - 2, tab_y1 - 2,
               (tab_y1-tab_y0)//2 - 2, fill=c["accent"])

        login_tag = cv.create_rectangle(tab_x0, tab_y0, tab_x0+half_w, tab_y1, outline="", fill="")
        register_tag = cv.create_rectangle(tab_x0+half_w, tab_y0, tab_x1, tab_y1, outline="", fill="")
        cv.create_text(tab_x0 + half_w/2, (tab_y0+tab_y1)/2, text="Entrar", font=f_btn,
                        fill="#ffffff" if self._mode == "login" else c["text_dim"])
        cv.create_text(tab_x0 + half_w*1.5, (tab_y0+tab_y1)/2, text="Cadastrar", font=f_btn,
                        fill="#ffffff" if self._mode == "register" else c["text_dim"])
        cv.tag_bind(login_tag, "<Button-1>", lambda e: self._switch_mode("login"))
        cv.tag_bind(register_tag, "<Button-1>", lambda e: self._switch_mode("register"))

        # ---- avatar ----
        cv.create_oval(ax-ar, ay-ar, ax+ar, ay+ar, fill=c["surface_alt"], outline=c["border"])
        _draw_field_icon(cv, "user", ax, ay+3, ar*1.3, c["text_dim"])

        # ---- campos ----
        field_pad = round(24 * scale)
        field_x0 = card_x + field_pad
        field_w = card_w - field_pad * 2
        y = field_y
        self._entries.clear()
        if self._mode == "register":
            y = self._add_field(cv, "username", "user", "Usuário", field_x0, y, field_w, field_h, scale=scale, font=f_entry) + field_spacing
            y = self._add_field(cv, "email", "mail", "E-mail (opcional)", field_x0, y, field_w, field_h, scale=scale, font=f_entry) + field_spacing
            y = self._add_field(cv, "password", "lock", "Senha (mín. 8 caracteres)", field_x0, y, field_w, field_h, secret=True, scale=scale, font=f_entry)
        else:
            y = self._add_field(cv, "username", "user", "Usuário", field_x0, y, field_w, field_h, scale=scale, font=f_entry) + field_spacing
            y = self._add_field(cv, "password", "lock", "Senha", field_x0, y, field_w, field_h, secret=True, scale=scale, font=f_entry) + field_spacing
            y = self._add_field(cv, "totp", "lock", "Código 2FA (se ativado)", field_x0, y, field_w, field_h, scale=scale, font=f_entry)
        self._restore_values(saved_values)

        # ---- status (erro/info) ----
        self._status_item = cv.create_text(
            W//2, status_y, text=self._status_text, font=f_tiny,
            fill=(c["accent2"] if self._status_error else c["text_dim"]),
            width=card_w - round(40*scale), justify="center",
        )

        # ---- botão principal ----
        btn_label = "Entrar" if self._mode == "login" else "Criar conta"
        btn = make_pill(cv, btn_label,
                         self._do_login if self._mode == "login" else self._do_register,
                         variant="accent", font=f_btn,
                         pad_x=round(20*scale), pad_y=round(9*scale), min_w=field_w)
        cv.create_window(W//2, btn_y, window=btn)

        # ---- link de troca de modo ----
        if self._mode == "login":
            cv.create_text(W//2, switch_y, text="Não tem conta?  Cadastre-se",
                            font=f_tiny, fill=c["text_dim"])
        else:
            cv.create_text(W//2, switch_y, text="Já tem conta?  Entrar",
                            font=f_tiny, fill=c["text_dim"])
        link_tag = cv.create_rectangle(card_x, switch_y-10, card_x+card_w, switch_y+10, outline="", fill="")
        cv.tag_bind(link_tag, "<Button-1>",
                    lambda e: self._switch_mode("register" if self._mode == "login" else "login"))

        # ---- convidado, fora do cartão ----
        guest = cv.create_text(W//2, guest_y, text="Continuar como convidado",
                                font=f_label, fill=c["text_dim"])
        cv.tag_bind(guest, "<Button-1>", lambda e: self._continue_guest())
        cv.tag_bind(guest, "<Enter>", lambda e: cv.itemconfig(guest, fill=c["text"]))
        cv.tag_bind(guest, "<Leave>", lambda e: cv.itemconfig(guest, fill=c["text_dim"]))
        for tag in (guest, login_tag, register_tag, link_tag):
            cv.tag_bind(tag, "<Enter>", lambda e, t=tag: cv.config(cursor="hand2"))
            cv.tag_bind(tag, "<Leave>", lambda e: cv.config(cursor=""))

        if not _ACCOUNTS_AVAILABLE:
            self._set_status("Contas indisponíveis no momento — use o modo convidado.", error=True)

    def _capture_values(self):
        """Preserva o que o usuário já digitou ao reconstruir a tela
        (redimensionar janela, maximizar, entrar/sair de tela cheia)."""
        saved = {}
        for name, (entry, ph) in getattr(self, "_entries", {}).items():
            try:
                val = entry.get()
            except tk.TclError:
                continue
            if val != ph:
                saved[name] = val
        return saved

    def _restore_values(self, saved):
        for name, val in saved.items():
            if name not in self._entries or not val:
                continue
            entry, _ph = self._entries[name]
            entry.delete(0, "end")
            entry.insert(0, val)
            entry.config(fg=THEME["text"])
            if name == "password":
                entry.config(show="•")

    def _add_field(self, cv, name, icon_kind, placeholder, x, y, w, h, secret=False, scale=1.0, font=None):
        c = THEME
        font = font or FSMALL
        icon_off = round(22 * scale)
        icon_size = round(18 * scale)
        entry_x = round(40 * scale)
        radius = round(12 * scale)

        _rrect(cv, x, y, x+w, y+h, radius, fill=c["surface_alt"])
        _draw_field_icon(cv, icon_kind, x + icon_off, y + h/2, icon_size, c["text_dim"])

        entry = tk.Entry(cv, font=font, bd=0, highlightthickness=0,
                          bg=c["surface_alt"], fg=c["text_dim"],
                          insertbackground=c["text"])
        entry.insert(0, placeholder)
        entry_w = w - entry_x - round(6 * scale)
        cv.create_window(x + entry_x, y + h/2, window=entry, anchor="w",
                          width=entry_w, height=max(1, h - round(14 * scale)))

        def on_focus_in(_e, ent=entry, ph=placeholder, sec=secret):
            if ent.get() == ph:
                ent.delete(0, "end")
                ent.config(fg=c["text"])
                if sec:
                    ent.config(show="•")

        def on_focus_out(_e, ent=entry, ph=placeholder):
            if not ent.get():
                ent.config(fg=c["text_dim"], show="")
                ent.insert(0, ph)

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        self._entries[name] = (entry, placeholder)
        return y + h

    def _field_value(self, name):
        entry, placeholder = self._entries[name]
        v = entry.get()
        return "" if v == placeholder else v.strip() if name != "password" else v

    def _set_status(self, text, error=False):
        self._status_text, self._status_error = text, error
        if hasattr(self, "_cv") and self._status_item:
            self._cv.itemconfig(self._status_item, text=text,
                                 fill=(THEME["accent2"] if error else THEME["text_dim"]))

    # ---------- interação ----------

    def _switch_mode(self, mode):
        if mode == self._mode:
            return
        self._mode = mode
        self._status_text = ""
        self._build()

    def _do_login(self):
        if not _ACCOUNTS_AVAILABLE:
            self._set_status("Contas indisponíveis no momento.", error=True)
            return
        self._authenticate(api_client.login)

    def _do_register(self):
        if not _ACCOUNTS_AVAILABLE:
            self._set_status("Contas indisponíveis no momento.", error=True)
            return
        self._authenticate(api_client.register, with_email=True)

    def _authenticate(self, api_fn, with_email=False):
        if self._auth_in_progress:
            return
        username = self._field_value("username")
        password = self._field_value("password")
        if not username or not password:
            self._set_status("Preencha usuário e senha.", error=True)
            return
        email = (self._field_value("email") or None) if with_email else None
        self._auth_in_progress = True
        self._set_status("Conectando…")

        def worker():
            try:
                auth = api_fn(username, password, email) if with_email else api_fn(username, password,self._field_value("totp") or None)
                result = (auth, None)
            except api_client.ApiAuthError as exc:
                result = (None, str(exc))
            except api_client.ApiUnavailableError:
                result = (None, "Sem conexão com o servidor. Tente o modo convidado.")
            except api_client.ApiServerError as exc:
                result = (None, str(exc))
            except Exception:
                log.exception("Falha inesperada durante autenticação")
                result = (None, "Não foi possível entrar agora.")
            try:
                self.after(0, lambda: self._finish_auth(*result))
            except tk.TclError:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _finish_auth(self, auth, error):
        self._auth_in_progress = False
        if error:
            self._set_status(error, error=True)
            return
        session_store.save_session(session_store.LocalSession(
            token=auth.token, user_id=auth.user_id,
            username=auth.username, display_name=auth.display_name,
            is_moderator=getattr(auth, "is_moderator", False),
            role=getattr(auth, "role", "user"),
        ))
        self.destroy()
        self.cb(auth)

    def _continue_guest(self):
        self.destroy()
        self.cb(None)


class PublishDialog(tk.Toplevel):
    """
    Formulário pra enviar um quadrinho da biblioteca local pra moderação
    e, se aprovado, pra comunidade. Só os METADADOS são enviados agora —
    o arquivo em si continua no computador do usuário (upload de arquivo
    de verdade é um passo futuro separado, de armazenamento).
    """
    W, H = 440, 650

    def __init__(self, master, path, user):
        super().__init__(master)
        try: self.iconbitmap(resource_path("panel.ico"))
        except Exception as _e: log.debug("silenced: %s", _e)
        self._path = path
        self._user = user
        self._submit_in_progress = False
        self.title("Publicar na comunidade")
        self.configure(bg=THEME["bg"])
        self.resizable(False, False)
        self.grab_set()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{self.W}x{self.H}+{(sw-self.W)//2}+{(sh-self.H)//2}")

        c = THEME
        pad = dict(padx=28)

        tk.Label(self, text="Publicar na comunidade", font=FTITLE,
                 bg=c["bg"], fg=c["text"]).pack(pady=(22, 2), **pad)
        tk.Label(self, text=os.path.basename(path), font=FTINY,
                 bg=c["bg"], fg=c["text_dim"]).pack(pady=(0, 14), **pad)

        def field(label_text):
            tk.Label(self, text=label_text, font=FTINY, bg=c["bg"], fg=c["text_dim"],
                      anchor="w").pack(fill="x", pady=(8, 2), **pad)
            e = tk.Entry(self, font=FSMALL, bg=c["surface_alt"], fg=c["text"],
                         bd=0, highlightthickness=1, highlightbackground=c["border"],
                         highlightcolor=c["accent"], insertbackground=c["text"])
            e.pack(fill="x", ipady=6, **pad)
            return e

        self._title_e = field("Título")
        self._title_e.insert(0, Path(path).stem)
        self._author_e = field("Autor")
        self._series_e = field("Série (opcional)")
        self._chapter_e = field("Número do capítulo (opcional)")
        self._tags_e = field("Tags (separadas por vírgula)")
        self._license_e = field("Licença (opcional — ex: CC-BY-4.0, Domínio Público)")

        tk.Label(self, text="Descrição", font=FTINY, bg=c["bg"], fg=c["text_dim"],
                  anchor="w").pack(fill="x", pady=(8, 2), **pad)
        self._desc_txt = tk.Text(self, font=FSMALL, bg=c["surface_alt"], fg=c["text"],
                                   bd=0, highlightthickness=1, highlightbackground=c["border"],
                                   highlightcolor=c["accent"], insertbackground=c["text"],
                                   height=3, wrap="word")
        self._desc_txt.pack(fill="x", **pad)

        self._authorship_var = tk.BooleanVar(value=False)
        self._authorization_var = tk.BooleanVar(value=False)
        chk_kwargs = dict(bg=c["bg"], fg=c["text"], selectcolor=c["surface_alt"],
                           activebackground=c["bg"], activeforeground=c["text"],
                           font=FTINY, anchor="w", relief="flat", bd=0,
                           highlightthickness=0)
        tk.Checkbutton(self, text="Sou o autor original desta obra",
                        variable=self._authorship_var, **chk_kwargs).pack(fill="x", pady=(12, 0), **pad)
        tk.Checkbutton(self, text="Tenho autorização do autor para publicar",
                        variable=self._authorization_var, **chk_kwargs).pack(fill="x", **pad)

        self._status = tk.Label(self, text="", font=FTINY, bg=c["bg"], fg=c["text_dim"],
                                  wraplength=self.W-56, justify="center")
        self._status.pack(pady=(10, 0), **pad)

        btn_row = tk.Frame(self, bg=c["bg"])
        btn_row.pack(pady=16, **pad, fill="x")
        make_pill(btn_row, "Cancelar", self.destroy,
                  variant="ghost", font=FBTN, pad_x=18, pad_y=9).pack(side="left")
        make_pill(btn_row, "Enviar para moderação", self._submit,
                  variant="accent", font=FBTN, pad_x=18, pad_y=9).pack(side="right")

    def _submit(self):
        if self._submit_in_progress:
            return
        title = self._title_e.get().strip()
        author = self._author_e.get().strip()
        if not title or not author:
            self._status.config(text="Preencha ao menos título e autor.", fg=THEME["accent2"])
            return
        if not self._authorship_var.get() and not self._authorization_var.get():
            self._status.config(
                text="Marque que você é o autor ou tem autorização — publicações "
                     "sem isso têm risco maior de ficar em revisão.",
                fg=THEME["accent2"])
            return

        tags = [t.strip() for t in self._tags_e.get().split(",") if t.strip()]
        description = self._desc_txt.get("1.0", "end").strip()
        license_ = self._license_e.get().strip() or None
        series_title = self._series_e.get().strip() or None
        try: chapter_number = int(self._chapter_e.get()) if self._chapter_e.get().strip() else None
        except ValueError:
            self._status.config(text="O número do capítulo precisa ser inteiro.",fg=THEME["accent2"]); return
        authorship_declared = self._authorship_var.get()
        authorization_declared = self._authorization_var.get()

        self._submit_in_progress = True
        self._status.config(text="Enviando para moderação…", fg=THEME["text_dim"])

        def worker():
            try:
                response = api_client.submit_publication(
                    self._user.token, title=title, author=author, description=description,
                    tags=tags, file_reference=self._path,
                    authorship_declared=authorship_declared,
                    authorization_declared=authorization_declared, license=license_,
                    series_title=series_title, chapter_number=chapter_number,
                )
                api_client.upload_publication_file(
                    self._user.token, response.publication_id, self._path
                )
                outcome = (response, None)
            except api_client.ApiAuthError as exc:
                outcome = (None, str(exc))
            except api_client.ApiUnavailableError:
                outcome = (None, "Sem conexão com o servidor. Tente novamente mais tarde.")
            except api_client.ApiServerError as exc:
                outcome = (None, str(exc))
            except Exception:
                log.exception("Falha inesperada durante publicação")
                outcome = (None, "Não foi possível enviar a publicação agora.")
            try:
                self.after(0, lambda: self._finish_submit(*outcome))
            except tk.TclError:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _finish_submit(self, result, error):
        self._submit_in_progress = False
        if error:
            self._status.config(text=error, fg=THEME["accent2"])
            return
        messagebox.showinfo("Publicação enviada", result.public_message)
        self.destroy()


class CommunityWindow(tk.Toplevel):
    """Catálogo público ou histórico de envios da conta."""

    STATUS_LABELS = {
        "approved": "Aprovada",
        "pending_review": "Em análise",
        "rejected": "Rejeitada",
    }

    def __init__(self, master, user=None, mine=False):
        super().__init__(master)
        self._user = user
        self._mine = mine
        self._items = []
        self._cover_tk = None
        title = "Meus envios" if mine else "Descobrir"
        self.title(f"PANEL — {title}")
        self.geometry("860x540")
        self.minsize(700, 440)
        self.configure(bg=THEME["bg"])
        try: self.iconbitmap(resource_path("panel.ico"))
        except Exception as _e: log.debug("silenced: %s", _e)

        header = tk.Frame(self, bg=THEME["bg"])
        header.pack(fill="x", padx=20, pady=(18, 10))
        tk.Label(header, text=title, font=FTITLE, bg=THEME["bg"],
                 fg=THEME["text"]).pack(side="left")
        make_pill(header, "Atualizar", self._refresh, variant="ghost",
                  font=FBTN, pad_x=14, pad_y=7).pack(side="right")

        body = tk.Frame(self, bg=THEME["bg"])
        body.pack(fill="both", expand=True, padx=20)
        self._list = tk.Listbox(
            body, width=38, bg=THEME["surface"], fg=THEME["text"],
            selectbackground=THEME["accent"], selectforeground="#ffffff",
            bd=0, highlightthickness=1, highlightbackground=THEME["border"],
            font=FSMALL,
        )
        self._list.pack(side="left", fill="both")
        self._list.bind("<<ListboxSelect>>", self._show_selected)
        right = tk.Frame(body, bg=THEME["surface"])
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))
        self._cover = tk.Label(
            right, text="Selecione uma obra", bg=THEME["surface_alt"],
            fg=THEME["text_dim"], font=FTINY, width=22, height=12,
        )
        self._cover.pack(side="left", padx=14, pady=14)
        detail_side = tk.Frame(right, bg=THEME["surface"])
        detail_side.pack(side="left", fill="both", expand=True)
        self._detail = tk.Text(
            detail_side, bg=THEME["surface"], fg=THEME["text"], font=FSMALL,
            wrap="word", bd=0, padx=18, pady=15, state="disabled",
        )
        self._detail.pack(fill="both", expand=True)
        actions = tk.Frame(detail_side, bg=THEME["surface"])
        actions.pack(fill="x", padx=12, pady=12)
        make_pill(actions, "Ler", self._read_selected, variant="accent",
                  font=FBTN, pad_x=16, pad_y=8).pack(side="left")
        make_pill(actions, "Baixar", self._download_selected, variant="ghost",
                  font=FBTN, pad_x=16, pad_y=8).pack(side="left", padx=8)
        if self._user is not None and not self._mine:
            make_pill(actions, "Denunciar", self._report_selected, variant="ghost",
                      font=FBTN, pad_x=16, pad_y=8).pack(side="left")
        self._status = tk.Label(self, text="", font=FTINY, bg=THEME["bg"],
                                fg=THEME["text_dim"])
        self._status.pack(fill="x", padx=20, pady=14)
        self._refresh()

    def _refresh(self):
        self._status.config(text="Carregando…", fg=THEME["text_dim"])

        def worker():
            try:
                items = (api_client.my_publications(self._user.token)
                         if self._mine else api_client.discovery())
                outcome = (items, None)
            except (api_client.ApiAuthError, api_client.ApiServerError) as exc:
                outcome = (None, str(exc))
            except api_client.ApiUnavailableError:
                cached, saved_at = load_catalog()
                outcome = (cached, None) if cached and not self._mine else (None, "Servidor indisponível.")
            except Exception:
                log.exception("Falha ao carregar comunidade")
                outcome = (None, "Não foi possível carregar os dados.")
            try: self.after(0, lambda: self._loaded(*outcome))
            except tk.TclError: pass

        threading.Thread(target=worker, daemon=True).start()

    def _loaded(self, items, error):
        if error:
            self._status.config(text=error, fg=THEME["accent2"])
            return
        self._items = items
        if not self._mine:
            save_catalog(items)
        self._list.delete(0, "end")
        for item in items:
            suffix = (f" — {self.STATUS_LABELS.get(item['status'], item['status'])}"
                      if self._mine else f" — {item['author']}")
            self._list.insert("end", item["title"] + suffix)
        noun = "envio(s)" if self._mine else "obra(s)"
        self._status.config(text=f"{len(items)} {noun}", fg=THEME["text_dim"])
        if items:
            self._list.selection_set(0)
            self._show_selected()
        else:
            self._set_detail("Nenhum item encontrado.")

    def _show_selected(self, _event=None):
        selected = self._list.curselection()
        if not selected:
            return
        item = self._items[selected[0]]
        lines = [
            f"Título: {item['title']}",
            f"Autor: {item['author']}",
            f"Tags: {', '.join(item.get('tags', [])) or 'Nenhuma'}",
        ]
        if item.get("series_title"):
            lines.insert(1,f"Série: {item['series_title']} · Capítulo {item.get('chapter_number') or '?'}")
        if self._mine:
            lines.extend([
                f"Status: {self.STATUS_LABELS.get(item['status'], item['status'])}",
                f"Risco da triagem: {item['risk_level']}",
            ])
            if item.get("decision_reason"):
                lines.append(f"Motivo da decisão: {item['decision_reason']}")
        lines.extend(["", item.get("description") or "Sem descrição."])
        if not item.get("has_file"):
            lines.extend(["", "O arquivo desta publicação ainda não foi enviado."])
        self._set_detail("\n".join(lines))
        self._load_cover(item)

    def _selected_item(self):
        selected = self._list.curselection()
        return self._items[selected[0]] if selected else None

    def _token(self):
        return self._user.token if self._user else None

    def _report_selected(self):
        item=self._selected_item()
        if not item:return
        reason=simpledialog.askstring("Denunciar obra","Motivo (copyright, illegal, harassment, spam ou other):",parent=self)
        if not reason:return
        reason=reason.strip().lower()
        if reason not in {"copyright","illegal","harassment","spam","other"}:
            messagebox.showerror("Denúncia","Motivo inválido.",parent=self);return
        description=simpledialog.askstring("Denunciar obra","Descreva o problema:",parent=self) or ""
        def worker():
            try: api_client.create_report(self._user.token,"publication",item["publication_id"],reason,description); error=None
            except Exception as exc:error=str(exc)
            self.after(0,lambda:messagebox.showerror("Denúncia",error,parent=self) if error else messagebox.showinfo("Denúncia","Denúncia enviada para a moderação.",parent=self))
        threading.Thread(target=worker,daemon=True).start()

    def _load_cover(self, item):
        self._cover.config(image="", text="Carregando capa…")
        self._cover_tk = None
        if not item.get("has_file"):
            self._cover.config(text="Sem arquivo")
            return
        publication_id = item["publication_id"]
        token = self._token()

        def worker():
            try:
                data = api_client.publication_cover(publication_id, token)
                image = Image.open(io.BytesIO(data)).convert("RGB")
                image.thumbnail((220, 320), Image.LANCZOS)
                outcome = (image, None)
            except Exception as exc:
                outcome = (None, str(exc))
            try: self.after(0, lambda: self._cover_loaded(*outcome))
            except tk.TclError: pass
        threading.Thread(target=worker, daemon=True).start()

    def _cover_loaded(self, image, error):
        if error:
            self._cover.config(text="Capa indisponível")
            return
        self._cover_tk = ImageTk.PhotoImage(image)
        self._cover.config(image=self._cover_tk, text="", width=image.width, height=image.height)

    def _read_selected(self):
        item = self._selected_item()
        if not item or not item.get("has_file"):
            messagebox.showinfo("Comunidade", "Esta publicação ainda não possui arquivo.", parent=self)
            return
        folder = os.path.join(_APPDATA, "community_cache")
        os.makedirs(folder, exist_ok=True)
        extension = Path(item.get("original_filename") or ".cbz").suffix or ".cbz"
        destination = os.path.join(folder, item["publication_id"] + extension)
        self._download_item(item, destination, open_after=True)

    def _download_selected(self):
        item = self._selected_item()
        if not item or not item.get("has_file"):
            messagebox.showinfo("Comunidade", "Esta publicação ainda não possui arquivo.", parent=self)
            return
        destination = filedialog.asksaveasfilename(
            parent=self, initialfile=item.get("original_filename") or "quadrinho.cbz"
        )
        if destination:
            self._download_item(item, destination, open_after=False)

    def _download_item(self, item, destination, open_after):
        self._status.config(text="Baixando arquivo…", fg=THEME["text_dim"])
        token = self._token()
        url = f"{api_client.BASE_URL}/publications/{item['publication_id']}/content"
        def done(task):
            error = task.error or ("Download cancelado." if task.status == "cancelled" else None)
            try: self.after(0, lambda: self._download_finished(destination, open_after, error))
            except tk.TclError: pass
        download_manager.add(item.get("title") or "Quadrinho", url, destination, token, done)

    def _download_finished(self, destination, open_after, error):
        if error:
            self._status.config(text=error, fg=THEME["accent2"])
            return
        self._status.config(text="Download concluído.", fg=THEME["text_dim"])
        if open_after:
            try:
                loader = SmartPageLoader(destination)
                ReaderWindow(self, destination, loader)
            except Exception as exc:
                messagebox.showerror("Leitura", f"Não foi possível abrir: {exc}", parent=self)

    def _set_detail(self, text):
        self._detail.config(state="normal")
        self._detail.delete("1.0", "end")
        self._detail.insert("1.0", text)
        self._detail.config(state="disabled")


class ModerationWindow(tk.Toplevel):
    """Fila administrativa de publicações que aguardam revisão humana."""

    def __init__(self, master, user):
        super().__init__(master)
        self._user = user
        self._items = []
        self.title("PANEL — Moderação")
        self.geometry("900x560")
        self.minsize(720, 460)
        self.configure(bg=THEME["bg"])
        try: self.iconbitmap(resource_path("panel.ico"))
        except Exception as _e: log.debug("silenced: %s", _e)

        header = tk.Frame(self, bg=THEME["bg"])
        header.pack(fill="x", padx=20, pady=(18, 10))
        tk.Label(header, text="Pedidos de publicação", font=FTITLE,
                 bg=THEME["bg"], fg=THEME["text"]).pack(side="left")
        make_pill(header, "Atualizar", self._refresh, variant="ghost",
                  font=FBTN, pad_x=14, pad_y=7).pack(side="right")

        body = tk.Frame(self, bg=THEME["bg"])
        body.pack(fill="both", expand=True, padx=20)
        self._list = tk.Listbox(
            body, width=38, bg=THEME["surface"], fg=THEME["text"],
            selectbackground=THEME["accent"], selectforeground="#ffffff",
            bd=0, highlightthickness=1, highlightbackground=THEME["border"],
            font=FSMALL,
        )
        self._list.pack(side="left", fill="both", expand=False)
        self._list.bind("<<ListboxSelect>>", self._show_selected)

        right = tk.Frame(body, bg=THEME["surface"])
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))
        self._detail = tk.Text(
            right, bg=THEME["surface"], fg=THEME["text"], font=FSMALL,
            wrap="word", bd=0, padx=16, pady=14, state="disabled",
        )
        self._detail.pack(fill="both", expand=True)

        actions = tk.Frame(self, bg=THEME["bg"])
        actions.pack(fill="x", padx=20, pady=14)
        self._status = tk.Label(actions, text="", font=FTINY,
                                bg=THEME["bg"], fg=THEME["text_dim"])
        self._status.pack(side="left")
        make_pill(actions, "Rejeitar", lambda: self._decide("rejected"),
                  variant="ghost", font=FBTN, pad_x=16, pad_y=8).pack(side="right")
        make_pill(actions, "Aprovar", lambda: self._decide("approved"),
                  variant="accent", font=FBTN, pad_x=16, pad_y=8).pack(side="right", padx=8)
        self._refresh()

    def _run(self, operation, callback):
        self._status.config(text="Carregando…", fg=THEME["text_dim"])

        def worker():
            try:
                outcome = (operation(), None)
            except (api_client.ApiAuthError, api_client.ApiServerError) as exc:
                outcome = (None, str(exc))
            except api_client.ApiUnavailableError:
                outcome = (None, "Servidor indisponível.")
            except Exception:
                log.exception("Falha na tela de moderação")
                outcome = (None, "Não foi possível concluir a operação.")
            try: self.after(0, lambda: callback(*outcome))
            except tk.TclError: pass

        threading.Thread(target=worker, daemon=True).start()

    def _refresh(self):
        self._run(lambda: api_client.moderation_queue(self._user.token), self._loaded)

    def _loaded(self, items, error):
        if error:
            self._status.config(text=error, fg=THEME["accent2"])
            return
        self._items = items
        self._list.delete(0, "end")
        for item in items:
            self._list.insert("end", f"{item['title']} — @{item['uploader_username']}")
        self._status.config(text=f"{len(items)} pedido(s) pendente(s)", fg=THEME["text_dim"])
        if items:
            self._list.selection_set(0)
            self._show_selected()
        else:
            self._set_detail("Nenhum pedido aguardando revisão.")

    def _selected(self):
        selection = self._list.curselection()
        return self._items[selection[0]] if selection else None

    def _show_selected(self, _event=None):
        item = self._selected()
        if not item:
            return
        self._set_detail(
            f"Título: {item['title']}\n"
            f"Autor: {item['author']}\n"
            f"Enviado por: @{item['uploader_username']}\n"
            f"Risco: {item['risk_level']}\n"
            f"Confiança automática: {item['confidence']:.0%}\n\n"
            f"Análise interna:\n{item['justification']}"
        )

    def _set_detail(self, text):
        self._detail.config(state="normal")
        self._detail.delete("1.0", "end")
        self._detail.insert("1.0", text)
        self._detail.config(state="disabled")

    def _decide(self, decision):
        item = self._selected()
        if not item:
            messagebox.showinfo("Moderação", "Selecione um pedido primeiro.", parent=self)
            return
        verb = "aprovar" if decision == "approved" else "rejeitar"
        reason = simpledialog.askstring(
            "Motivo da decisão", f"Explique por que deseja {verb} esta publicação:",
            parent=self,
        )
        if not reason or len(reason.strip()) < 3:
            return
        self._run(
            lambda: api_client.moderate(
                self._user.token, item["record_id"], decision, reason.strip()
            ),
            lambda _result, error: self._decision_finished(error),
        )

    def _decision_finished(self, error):
        if error:
            self._status.config(text=error, fg=THEME["accent2"])
            return
        self._refresh()


class LangWindow(tk.Toplevel):
    def __init__(self, master, cb):
        super().__init__(master)
        try: self.iconbitmap(resource_path("panel.ico"))
        except Exception as _e: log.debug("silenced: %s", _e)
        self.cb = cb
        self.title("Idioma / Language")
        self.configure(bg=THEME["bg"])
        self.resizable(False, False)
        self.grab_set()
        W, H = 340, 232
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        tk.Canvas(self, width=W, height=3, bg=THEME["accent"], highlightthickness=0).place(x=0, y=0)
        tk.Label(self, text="◈ PANEL", font=FLOGO, bg=THEME["bg"], fg=THEME["text"]).pack(pady=(24, 2))
        tk.Label(self, text="Idioma / Language", font=FSMALL, bg=THEME["bg"], fg=THEME["text_dim"]).pack(pady=(0, 16))
        for flag, txt, lang in [("🇧🇷", "Português", "pt"), ("🇺🇸", "English", "en")]:
            make_pill(self, f"{flag}   {txt}", lambda l=lang: self._pick(l),
                      variant="soft", font=FBTN, pad_x=20, pad_y=10, min_w=W-100).pack(pady=5)

    def _pick(self, lang):
        global LANG
        LANG = lang
        save_prefs(lang=lang)
        self.destroy()
        self.cb()

class ThumbnailStrip(tk.Frame):
    def __init__(self, parent, bg_color="#1e1e1e", on_click=None, **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        self._on_click = on_click
        self._bg = bg_color
        self.canvas = tk.Canvas(self, height=110, highlightthickness=0, bg=bg_color)
        self.canvas.pack(side="top", fill="x", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg_color)
        self.win_id = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._wheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
        self._buttons = {}

    def _wheel(self, e):
        self.canvas.xview_scroll(int(-1 * (e.delta / 120)), "units")

    def add_thumbnail(self, tk_img, page_index):
        btn = tk.Button(self.inner, image=tk_img,
                        command=lambda: self._on_click and self._on_click(page_index),
                        bg="#2d2d2d", activebackground="#5a5a5a",
                        relief="flat", borderwidth=0, cursor="hand2",
                        highlightthickness=0)
        btn.image = tk_img
        btn.pack(side="left", padx=4, pady=8)
        self._buttons[page_index] = btn

    def highlight(self, idx):
        for i, b in self._buttons.items():
            if b.winfo_exists():
                b.config(highlightthickness=2 if i == idx else 0,
                         highlightbackground=THEME["accent"],
                         highlightcolor=THEME["accent"])

    def scroll_to(self, idx, total):
        if total <= 0:
            return
        self.canvas.update_idletasks()
        try:
            self.canvas.xview_moveto(max(0.0, (idx / total) - 0.1))
        except Exception:
            pass


class WebtoonViewer(tk.Toplevel):
    def __init__(self, parent, loader: SmartPageLoader, width=800, height=900):
        super().__init__(parent)
        self.title("PANEL - Modo Webtoon")
        self.geometry(f"{width}x{height}")
        bg = THEME["canvas_bg"]
        self.configure(bg=bg)
        self._loader = loader
        self._tw = width - 40
        self._labels = {}
        self._loaded = set()
        self._placeholders = {}

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=bg)
        self.canvas.create_window((width // 2, 0), window=self.inner, anchor="n")
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<MouseWheel>", self._wheel)
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._wheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        self._build_placeholders(bg)
        self.after(60, self._check_visible)

    def _build_placeholders(self, bg=None):
        if bg is None:
            bg = THEME["canvas_bg"]
        ph_text = THEME["text_muted"]
        est_h = int(self._tw * 1.4)
        for idx in range(self._loader.count):
            lbl = tk.Label(self.inner, bg=bg, text=f"··· {idx+1} ···",
                           fg=ph_text, height=int(est_h / 18))
            lbl.pack(side="top", fill="x", pady=0)
            self._labels[idx] = lbl

    def _wheel(self, e):
        self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        self.after(40, self._check_visible)

    def _check_visible(self):
        """Carrega só páginas visíveis + margem."""
        if not self.winfo_exists():
            return
        top = self.canvas.canvasy(0)
        bot = top + self.canvas.winfo_height()
        margin = self.canvas.winfo_height()
        for idx, lbl in self._labels.items():
            if idx in self._loaded or not lbl.winfo_exists():
                continue
            ly = lbl.winfo_y()
            lh = lbl.winfo_height()
            if (ly + lh) >= (top - margin) and ly <= (bot + margin):
                self._load_page(idx)

    def _load_page(self, idx):
        self._loaded.add(idx)
        def work():
            try:
                pil = self._loader.get_pil(idx).convert("RGB")
                pil.thumbnail((self._tw, 99999), Image.LANCZOS)
                def apply():
                    if not self.winfo_exists():
                        return
                    tk_img = ImageTk.PhotoImage(pil)
                    lbl = self._labels.get(idx)
                    if lbl and lbl.winfo_exists():
                        lbl.config(image=tk_img, text="", height=0)
                        lbl.image = tk_img
                self.after(0, apply)
            except Exception as e:
                print("webtoon load err:", e)
        threading.Thread(target=work, daemon=True).start()


class ReaderWindow(tk.Toplevel):
    ZSTEP = 0.15
    ZMIN  = 0.1
    ZMAX  = 5.0
    Z0    = 0.45

    def __init__(self, master, path, loader: SmartPageLoader, on_finish=None):
        super().__init__(master)
        try: self.iconbitmap(resource_path("panel.ico"))
        except Exception as _e: log.debug("silenced: %s", _e)
        self.title(f"PANEL — {Path(path).stem}")
        self.configure(bg=THEME["bg"])

        self._path      = path
        self._loader    = loader
        self._on_finish = on_finish
        self._idx       = 0
        self._zoom      = self.Z0
        self._offset    = [0, 0]
        self._drag      = None
        self._tk_img    = None
        self._rotation  = 0
        self._brightness = 1.0
        self._double    = False
        self._immersive = False
        self._fading    = False
        self._slider    = None
        try: self._content_key = content_id(path)
        except OSError: self._content_key = os.path.normcase(os.path.abspath(path))

        prefs = load_prefs()
        self._manga = prefs.get("manga", False)
        reader_state = load_reader_state(self._content_key)
        self._zoom = float(reader_state.get("zoom", self.Z0))
        self._offset = list(reader_state.get("offset", [0, 0]))
        self._double = bool(reader_state.get("double", False))
        self._manga = bool(reader_state.get("manga", self._manga))

        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(1280, sw-60), min(860, sh-60)
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.minsize(800, 600)
        self.protocol("WM_DELETE_WINDOW", self._close)

        p = get_progress_page(path)
        if p is not None and 0 <= p < loader.count:
            self._idx = p

        self._thumb_strip = None
        self._thumb_visible = False

        self._build()
        self.after(80, self._show)
        self._prefetch_neighbors()

    @property
    def _count(self):
        return self._loader.count

    def _build(self):
        for w in self.winfo_children():
            w.destroy()
        c = THEME

        self._top = tk.Frame(self, bg=c["surface"], height=58)
        self._top.pack(fill="x")
        self._top.pack_propagate(False)
        inner = tk.Frame(self._top, bg=c["surface"])
        inner.pack(fill="both", expand=True, padx=16, pady=9)

        left = tk.Frame(inner, bg=c["surface"])
        left.pack(side="left", fill="y")
        self._mkbtn(left, f"◀  {TEXTS[LANG]['back']}", self._close, accent=True).pack(side="left", padx=(0, 14))

        title_box = tk.Frame(left, bg=c["surface"])
        title_box.pack(side="left", fill="y")
        fname = Path(self._path).stem
        if len(fname) > 48: fname = fname[:45] + "…"
        tk.Label(title_box, text=fname, font=("Segoe UI", 11, "bold"),
                 bg=c["surface"], fg=c["text"], anchor="w").pack(anchor="w")

        right = tk.Frame(inner, bg=c["surface"])
        right.pack(side="right", fill="y")
        self._mkbtn(right, "⛶", self._immersive_toggle).pack(side="right", padx=3)
        self._mkbtn(right, TEXTS[LANG]["fullscreen"], self._fullscreen).pack(side="right", padx=3)
        self._mkbtn(right, "📜  Webtoon", self._open_webtoon).pack(side="right", padx=3)
        self._mkbtn(right, TEXTS[LANG]["fit"], self._fit).pack(side="right", padx=3)
        self._mkbtn(right, current_theme_label(), self._toggle_theme, icon=ICONS.get("theme")).pack(side="right", padx=3)

        self._bm_btn = self._pill(right, self._bm_label(), self._toggle_bookmark, variant="soft")
        self._bm_btn.pack(side="right", padx=3)

        txt = TEXTS[LANG]["manga_on"] if self._manga else TEXTS[LANG]["manga_off"]
        self._manga_btn = self._pill(right, txt, self._toggle_manga, variant="soft")
        self._manga_btn.pill_set_active(self._manga)
        self._manga_btn.pack(side="right", padx=(3, 10))

        tk.Frame(self, bg=c["accent"], height=2).pack(fill="x")

        self._cv = tk.Canvas(self, bg=c["canvas_bg"], highlightthickness=0, cursor="crosshair")
        self._cv.pack(fill="both", expand=True)

        self._bot = tk.Frame(self, bg=c["surface"], height=66)
        self._bot.pack(fill="x")
        self._bot.pack_propagate(False)
        self._prog_cv = tk.Canvas(self._bot, height=6, bg=c["progress_bg"], highlightthickness=0)
        self._prog_cv.pack(fill="x")
        self._prog_cv.bind("<Button-1>", self._seek_click)
        ib = tk.Frame(self._bot, bg=c["surface"])
        ib.pack(fill="both", expand=True, padx=16, pady=8)

        nf = tk.Frame(ib, bg=c["surface"]); nf.pack(side="left")
        self._nav_btn(nf, "‹" if not ICONS.get("prev") else "", self._prev,
                      icon=ICONS.get("prev")).pack(side="left", padx=(0, 8))
        self._page_lbl = tk.Label(nf, text="", font=("Consolas", 12, "bold"),
                                  bg=c["surface_alt"], fg=c["text"], width=11, padx=10, pady=6)
        self._page_lbl.pack(side="left", padx=2)
        self._nav_btn(nf, "›" if not ICONS.get("next") else "", self._next,
                      icon=ICONS.get("next")).pack(side="left", padx=(8, 0))

        zf = tk.Frame(ib, bg=c["surface"]); zf.pack(side="left", padx=18)
        self._nav_btn(zf, "−" if not ICONS.get("zoom_out") else "", self._zoom_out,
                      icon=ICONS.get("zoom_out")).pack(side="left", padx=3)
        self._zoom_lbl = tk.Label(zf, text="45%", font=("Segoe UI", 9, "bold"),
                                  bg=c["surface"], fg=c["text_dim"], width=5)
        self._zoom_lbl.pack(side="left", padx=4)
        self._nav_btn(zf, "+" if not ICONS.get("zoom_in") else "", self._zoom_in,
                      icon=ICONS.get("zoom_in")).pack(side="left", padx=3)

        self._zvar = tk.DoubleVar(value=self._zoom)
        sl = tk.Scale(ib, from_=self.ZMIN, to=self.ZMAX, resolution=0.05,
                      orient="horizontal", variable=self._zvar, command=self._slider_zoom,
                      bg=c["surface"], fg=c["text_dim"], troughcolor=c["progress_bg"],
                      activebackground=c["accent2"], highlightthickness=0,
                      sliderrelief="flat", length=130, showvalue=False, bd=0)
        sl.pack(side="left", padx=(8, 0))
        self._slider = sl

        self._thumb_btn = self._pill(ib, "⊟  Miniaturas", self._toggle_thumbnails, variant="soft")
        self._thumb_btn.pack(side="right", padx=6)
        self._double_btn = self._pill(ib, "▭▭ Dupla", self._toggle_double, variant="soft")
        self._double_btn.pack(side="right", padx=3)
        self._nav_btn(ib, "↻", self._rotate).pack(side="right", padx=3)
        self._nav_btn(ib, "?", self._show_shortcuts).pack(side="right", padx=3)

        bf = tk.Frame(ib, bg=c["surface"]); bf.pack(side="right", padx=(0, 8))
        tk.Label(bf, text="☀", font=(_SANS, 9), bg=c["surface"], fg=c["text_dim"]).pack(side="left", padx=(0, 2))
        self._bright_var = tk.DoubleVar(value=self._brightness)
        bright_sl = tk.Scale(bf, from_=0.3, to=2.0, resolution=0.05,
                             orient="horizontal", variable=self._bright_var,
                             command=self._slider_brightness,
                             bg=c["surface"], fg=c["text_dim"], troughcolor=c["progress_bg"],
                             activebackground=c["accent2"], highlightthickness=0,
                             sliderrelief="flat", length=90, showvalue=False, bd=0)
        bright_sl.pack(side="left")

        self._thumb_frame = tk.Frame(self, bg=c["surface"], height=120)
        self._thumb_frame.pack_propagate(False)

        self._cv.bind("<ButtonPress-1>",  self._drag_start)
        self._cv.bind("<B1-Motion>",      self._drag_move)
        self._cv.bind("<ButtonRelease-1>",self._drag_end)
        self._cv.bind("<MouseWheel>",     self._wheel)
        self._cv.bind("<Configure>",      lambda e: self.after(80, lambda: self._show(reset=False)))
        self.bind("<Left>",   lambda e: self._prev())
        self.bind("<Right>",  lambda e: self._next())
        self.bind("<Prior>",  lambda e: self._prev())
        self.bind("<Next>",   lambda e: self._next())
        self.bind("<equal>",  lambda e: self._zoom_in())
        self.bind("<minus>",  lambda e: self._zoom_out())
        self.bind("<f>",      lambda e: self._fullscreen())
        self.bind("<F11>",    lambda e: self._fullscreen())
        self.bind("<i>",      lambda e: self._immersive_toggle())
        self.bind("<Escape>", lambda e: self._escape())
        self.bind("<t>",      lambda e: self._toggle_theme())
        self.bind("<g>",      lambda e: self._toggle_thumbnails())
        self.bind("<b>",      lambda e: self._toggle_bookmark())
        self.bind("<r>",      lambda e: self._rotate())
        self.bind("<question>", lambda e: self._show_shortcuts())
        self.bind("<bracketleft>",  lambda e: self._set_brightness(self._brightness - 0.1))
        self.bind("<bracketright>", lambda e: self._set_brightness(self._brightness + 0.1))

    def _pill(self, parent, text, cmd, *, icon=None, variant="ghost",
              font=FSMALL, pad_x=14, pad_y=8, min_w=0):
        return make_pill(parent, text, cmd, icon=icon, variant=variant,
                         font=font, pad_x=pad_x, pad_y=pad_y, min_w=min_w)

    def _mkbtn(self, parent, text, cmd, accent=False, icon=None):
        return self._pill(parent, text, cmd, icon=icon,
                          variant="accent" if accent else "ghost")

    def _nav_btn(self, parent, text, cmd, icon=None):
        c = THEME
        host_bg = parent.cget("bg")
        size, r = 40, 12
        cv = tk.Canvas(parent, width=size, height=size, bg=host_bg,
                       highlightthickness=0, cursor="hand2", takefocus=0)
        def render(fill, fg, outline):
            cv.delete("all")
            _rrect(cv, 1, 1, size - 1, size - 1, r, fill=fill)
            if outline: _rrect(cv, 1, 1, size - 2, size - 2, r, outline=outline, width=1)
            if icon: cv.create_image(size // 2, size // 2, image=icon)
            if text: cv.create_text(size // 2, size // 2, text=text,
                                    font=("Segoe UI", 13, "bold"), fill=fg)
        render(c["surface_alt"], c["text"], c["border"])
        cv.bind("<Enter>", lambda e: render(c["accent"], "#fff", c["accent"]))
        cv.bind("<Leave>", lambda e: render(c["surface_alt"], c["text"], c["border"]))
        cv.bind("<Button-1>", lambda e: cmd())
        return cv

    def _processed_pil(self, idx):
        """Aplica rotação + brilho."""
        img = self._loader.get_pil(idx)
        if self._rotation:
            img = img.rotate(-self._rotation, expand=True, resample=Image.BICUBIC)
        if abs(self._brightness - 1.0) > 0.01:
            img = ImageEnhance.Brightness(img.convert("RGB")).enhance(self._brightness).convert("RGBA")
        return img

    def _compose_pages(self):
        """Retorna a imagem a desenhar (1 ou 2 páginas)."""
        base = self._processed_pil(self._idx)
        if not self._double:
            return base
        if self._idx == 0:
            return base
        nxt_idx = self._idx + 1
        if nxt_idx >= self._count:
            return base
        nxt = self._processed_pil(nxt_idx)
        h = max(base.height, nxt.height)
        left, rightimg = (nxt, base) if self._manga else (base, nxt)
        combo = Image.new("RGBA", (left.width + rightimg.width, h), (0, 0, 0, 0))
        combo.paste(left, (0, (h - left.height) // 2))
        combo.paste(rightimg, (left.width, (h - rightimg.height) // 2))
        return combo

    def _show(self, reset=True, alpha=1.0):
        cw = self._cv.winfo_width() or 800
        ch = self._cv.winfo_height() or 600
        img = self._compose_pages()
        iw, ih = img.size

        if reset:
            self._zoom = self.Z0
            self._offset = [0, 0]
            if self._slider: self._zvar.set(self._zoom)

        nw = max(1, int(iw * self._zoom))
        nh = max(1, int(ih * self._zoom))
        resized = img.resize((nw, nh), Image.BILINEAR)

        bg_rgb = (7, 7, 14) if IS_DARK else (232, 228, 222)
        full = Image.new("RGB", (cw, ch), bg_rgb)
        px = cw // 2 + int(self._offset[0]) - nw // 2
        py = ch // 2 + int(self._offset[1]) - nh // 2
        full.paste(resized.convert("RGB"), (px, py))

        if alpha < 1.0:
            full = Image.blend(Image.new("RGB", (cw, ch), bg_rgb), full, alpha)

        self._tk_img = ImageTk.PhotoImage(full)
        self._cv.delete("all")
        self._cv.create_image(0, 0, anchor="nw", image=self._tk_img)
        self._hud()

    def _fade_to(self, new_idx):
        if self._fading: return
        new_idx = max(0, min(new_idx, self._count - 1))
        if new_idx == self._idx: return
        self._fading = True
        start = time.perf_counter()
        self._loader.get_pil(new_idx)

        def animate():
            elapsed = time.perf_counter() - start
            prog = min(elapsed / FADE_SPEED, 1.0)
            if prog < 0.5:
                self._show(reset=False, alpha=1.0 - ease_out(prog))
            elif prog < 1.0:
                if not hasattr(animate, "swapped"):
                    self._idx = new_idx
                    save_progress(self._path, self._idx)
                    animate.swapped = True
                    self._prefetch_neighbors()
                self._show(reset=True, alpha=ease_out((prog - 0.5) * 2))
            else:
                self._show(reset=False)
                self._fading = False
                return
            self.after(16, animate)
        animate()

    def _prefetch_neighbors(self):
        self._loader.prefetch(self._idx + 1)
        self._loader.prefetch(self._idx + 2)
        self._loader.prefetch(self._idx - 1)

    def _update_progress_bar(self):
        if not hasattr(self, "_prog_cv") or not self._prog_cv.winfo_exists():
            return
        n = self._count
        if n == 0: return
        pw = self._prog_cv.winfo_width() or 400
        h = 6
        filled = int(pw * (self._idx + 1) / n)
        self._prog_cv.delete("all")
        self._prog_cv.create_rectangle(0, 0, pw, h, fill=THEME["progress_bg"], outline="")
        if filled > 0:
            self._prog_cv.create_rectangle(0, 0, filled, h, fill=THEME["accent"], outline="")
            self._prog_cv.create_rectangle(0, 0, filled, 2, fill=THEME["accent2"], outline="")
            self._prog_cv.create_oval(filled-4, -1, filled+4, h+1,
                                      fill=THEME["accent2"], outline="")
        for bm in get_bookmarks(self._path):
            bx = int(pw * (bm + 0.5) / n)
            self._prog_cv.create_rectangle(bx-1, 0, bx+1, h, fill="#ffd24a", outline="")

    def _hud(self):
        n = self._count
        suffix = f" +1" if (self._double and self._idx + 1 < n) else ""
        self._page_lbl.config(text=f"{self._idx+1}{suffix} / {n}")
        self._zoom_lbl.config(text=f"{self._zoom*100:.0f}%")
        if self._slider: self._zvar.set(self._zoom)
        if hasattr(self, "_bm_btn") and self._bm_btn.winfo_exists():
            self._bm_btn.pill_set_text(self._bm_label())
            self._bm_btn.pill_set_active(self._idx in get_bookmarks(self._path))
        self.update_idletasks()
        self._update_progress_bar()
        if self._thumb_visible and self._thumb_strip:
            self._thumb_strip.highlight(self._idx)
        self._update_done_btn()

    def _bm_label(self):
        return "★" if self._idx in get_bookmarks(self._path) else "☆"

    def _update_done_btn(self):
        """Mostra/esconde o botão 'Concluído' na última página."""
        c = THEME
        on_last = (self._idx >= self._count - 1)
        is_done = get_manual_status(self._path) == "done"
        if on_last:
            if not hasattr(self, "_done_overlay") or not self._done_overlay.winfo_exists():
                self._done_overlay = tk.Frame(self._cv, bg="", highlightthickness=0)
                lbl_txt = "✓  Concluído!" if is_done else "✓  Marcar como Concluído"
                fill = c["read_badge"] if is_done else c["accent"]
                fg   = c["read_badge_text"] if is_done else "#ffffff"
                self._done_pill = make_pill(self._done_overlay, lbl_txt,
                                           self._toggle_done_from_reader,
                                           variant="accent", font=FBTN, pad_x=22, pad_y=11)
                self._done_pill.pack()
                self._done_overlay.place(relx=0.5, rely=0.92, anchor="center")
            else:
                is_done = get_manual_status(self._path) == "done"
                lbl_txt = "✓  Concluído!" if is_done else "✓  Marcar como Concluído"
                if hasattr(self._done_pill, "pill_set_text"):
                    self._done_pill.pill_set_text(lbl_txt)
        else:
            if hasattr(self, "_done_overlay"):
                try: self._done_overlay.place_forget()
                except Exception as _e: log.debug("silenced: %s", _e)

    def _toggle_done_from_reader(self):
        cur = get_manual_status(self._path)
        set_manual_status(self._path, None if cur == "done" else "done")
        self._update_done_btn()

    def _step(self):
        return 2 if self._double else 1

    def _next(self):
        nxt = self._idx - self._step() if self._manga else self._idx + self._step()
        if nxt >= self._count or nxt < 0:
            if (not self._manga and self._idx + self._step() >= self._count) or \
               (self._manga and self._idx - self._step() < 0):
                self._maybe_next_chapter()
            return
        self._fade_to(nxt)

    def _prev(self):
        prv = self._idx + self._step() if self._manga else self._idx - self._step()
        self._fade_to(prv)

    def _maybe_next_chapter(self):
        if not self._on_finish:
            return
        if messagebox.askyesno(TEXTS[LANG]["next_issue"],
                               TEXTS[LANG]["next_chapter_q"]):
            self._on_finish(self._path)
            self.destroy()

    def _seek_click(self, e):
        pw = self._prog_cv.winfo_width() or 1
        frac = max(0.0, min(1.0, e.x / pw))
        self._fade_to(int(frac * (self._count - 1)))

    def _set_zoom(self, z):
        self._zoom = max(self.ZMIN, min(self.ZMAX, z))
        self._show(reset=False)
    def _zoom_in(self):  self._set_zoom(self._zoom + self.ZSTEP)
    def _zoom_out(self): self._set_zoom(self._zoom - self.ZSTEP)
    def _slider_zoom(self, v): self._set_zoom(float(v))

    def _fit(self):
        cw = self._cv.winfo_width() or 800
        ch = self._cv.winfo_height() or 600
        img = self._compose_pages()
        self._zoom = min(cw / img.width, ch / img.height) * 0.95
        self._offset = [0, 0]
        self._show(reset=False)

    def _drag_start(self, e):
        self._drag = (e.x, e.y); self._cv.config(cursor="fleur")
    def _drag_move(self, e):
        if self._drag:
            dx = e.x - self._drag[0]
            dy = e.y - self._drag[1]
            self._offset[0] += dx
            self._offset[1] += dy
            self._drag = (e.x, e.y)
            self._cv.move("all", dx, dy)
    def _drag_end(self, e):
        self._drag = None; self._cv.config(cursor="crosshair")
        self._show(reset=False)

    def _wheel(self, e):
        d = e.delta / 120 if e.delta else 0
        if e.state & 0x4:
            old_zoom = self._zoom
            new_zoom = max(self.ZMIN, min(self.ZMAX, self._zoom + d * self.ZSTEP))
            if new_zoom != old_zoom:
                cw = self._cv.winfo_width() or 800
                ch = self._cv.winfo_height() or 600
                mx = e.x - cw // 2
                my = e.y - ch // 2
                ratio = new_zoom / old_zoom
                self._offset[0] = mx - (mx - self._offset[0]) * ratio
                self._offset[1] = my - (my - self._offset[1]) * ratio
                self._zoom = new_zoom
                self._show(reset=False)
        else:
            (self._prev if d > 0 else self._next)()

    def _rotate(self):
        self._rotation = (self._rotation + 90) % 360
        self._show(reset=True)

    def _set_brightness(self, val):
        self._brightness = max(0.1, min(3.0, round(val, 2)))
        if hasattr(self, "_bright_var"):
            self._bright_var.set(self._brightness)
        self._show(reset=False)

    def _slider_brightness(self, v):
        self._brightness = float(v)
        self._show(reset=False)

    def _show_shortcuts(self):
        c = THEME
        win = tk.Toplevel(self)
        win.title("Atalhos de teclado")
        win.configure(bg=c["surface"])
        win.resizable(False, False)
        win.grab_set()
        W, H = 360, 380
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        tk.Canvas(win, width=W, height=3, bg=c["accent"], highlightthickness=0).place(x=0, y=0)
        tk.Label(win, text="Atalhos de Teclado", font=FBTN, bg=c["surface"],
                 fg=c["text"], pady=14).pack()
        tk.Frame(win, bg=c["border"], height=1).pack(fill="x", padx=16, pady=(0, 8))
        shortcuts = [
            ("← / →", "Página anterior / próxima"),
            ("+ / -", "Zoom in / out"),
            ("Ctrl + scroll", "Zoom no cursor"),
            ("F / F11", "Tela cheia"),
            ("I", "Modo imersivo"),
            ("R", "Girar página"),
            ("B", "Marcar bookmark"),
            ("G", "Mostrar miniaturas"),
            ("T", "Alternar tema"),
            ("[ / ]", "Reduzir / aumentar brilho"),
            ("?", "Esta janela"),
            ("Esc", "Sair da tela cheia"),
        ]
        frame = tk.Frame(win, bg=c["surface"]); frame.pack(padx=24, pady=4, fill="x")
        for key, desc in shortcuts:
            row = tk.Frame(frame, bg=c["surface"]); row.pack(fill="x", pady=3)
            tk.Label(row, text=key, font=(_MONO, 9, "bold"), bg=c["surface_alt"],
                     fg=c["accent"], padx=8, pady=3, relief="flat").pack(side="left")
            tk.Label(row, text=desc, font=FSMALL, bg=c["surface"],
                     fg=c["text_dim"], anchor="w").pack(side="left", padx=10)
        make_pill(win, "Fechar", win.destroy, variant="soft", font=FBTN,
                  pad_x=24, pad_y=10).pack(pady=14)

    def _toggle_double(self):
        self._double = not self._double
        if hasattr(self._double_btn, "pill_set_active"):
            self._double_btn.pill_set_active(self._double)
        self._show(reset=True)

    def _fullscreen(self):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def _immersive_toggle(self):
        self._immersive = not self._immersive
        if self._immersive:
            self._top.pack_forget()
            self._bot.pack_forget()
            self.attributes("-fullscreen", True)
        else:
            self.attributes("-fullscreen", False)
            self._top.pack(fill="x", before=self._cv)
            self._bot.pack(fill="x")
        self.after(60, lambda: self._show(reset=False))

    def _escape(self):
        if self.attributes("-fullscreen"):
            if self._immersive: self._immersive_toggle()
            else: self.attributes("-fullscreen", False)

    def _toggle_bookmark(self):
        toggle_bookmark(self._path, self._idx)
        self._hud()

    def _toggle_manga(self, e=None):
        self._manga = not self._manga
        save_prefs(manga=self._manga)
        txt = TEXTS[LANG]["manga_on"] if self._manga else TEXTS[LANG]["manga_off"]
        if hasattr(self, "_manga_btn") and self._manga_btn.winfo_exists():
            self._manga_btn.pill_set_text(txt)
            self._manga_btn.pill_set_active(self._manga)

    def _toggle_theme(self):
        toggle_theme()
        save_prefs(dark=IS_DARK)
        idx, zoom, offset = self._idx, self._zoom, self._offset[:]
        brightness = self._brightness
        tv = self._thumb_visible
        self._build()
        self._idx, self._zoom, self._offset = idx, zoom, offset
        self._brightness = brightness
        if hasattr(self, "_bright_var"): self._bright_var.set(brightness)
        if self._slider: self._zvar.set(zoom)
        if tv: self.after(120, self._open_thumbnails)
        self.after(80, lambda: self._show(reset=False))

    def _open_webtoon(self):
        WebtoonViewer(self, self._loader,
                      width=self.winfo_width(), height=self.winfo_height())

    def _toggle_thumbnails(self):
        if self._thumb_visible:
            self._thumb_visible = False
            self._thumb_btn.pill_set_text("⊟  Miniaturas")
            self._thumb_btn.pill_set_active(False)
            self._thumb_frame.pack_forget()
            for w in self._thumb_frame.winfo_children():
                try: w.destroy()
                except Exception as _e: log.debug("silenced: %s", _e)
            self._thumb_strip = None
        else:
            self._open_thumbnails()

    def _open_thumbnails(self):
        self._thumb_visible = True
        self._thumb_btn.pill_set_text("⊠  Miniaturas")
        self._thumb_btn.pill_set_active(True)
        for w in self._thumb_frame.winfo_children():
            try: w.destroy()
            except Exception as _e: log.debug("silenced: %s", _e)
        self._thumb_strip = ThumbnailStrip(self._thumb_frame, bg_color=THEME["surface"],
                                           on_click=self._fade_to)
        self._thumb_strip.pack(fill="both", expand=True)
        if not self._thumb_frame.winfo_ismapped():
            self._thumb_frame.pack(fill="x", before=self._bot)
        threading.Thread(target=self._load_thumbs_bg, daemon=True).start()

    def _load_thumbs_bg(self):
        TW, TH = 60, 84
        for i in range(self._count):
            try:
                pil = self._loader.get_thumbnail_pil(i, TW, TH)
                def add(idx=i, p=pil):
                    if self._thumb_strip and self._thumb_strip.winfo_exists():
                        tk_img = ImageTk.PhotoImage(p)
                        self._thumb_strip.add_thumbnail(tk_img, idx)
                        self._thumb_strip.highlight(self._idx)
                self.after(0, add)
            except Exception:
                pass

    def _close(self):
        save_progress(self._path, self._idx)
        save_reader_state(self._content_key, page=self._idx, zoom=self._zoom,
                          offset=self._offset, double=self._double, manga=self._manga)
        try: self._loader.close()
        except Exception as _e: log.debug("silenced: %s", _e)
        self.destroy()

class ComicCard:
    HOVER_STEPS = 10
    HOVER_MS    = 14
    SCALE_MAX   = 1.12

    def __init__(self, parent, path, img_pil, open_cb, root, label_override=None):
        self._path    = path
        self._open_cb = open_cb
        self._root    = root
        self._alpha   = 0.0
        self._anim_id = None
        self._img_pil = img_pil
        self._tk_img  = None

        c    = THEME
        nome = label_override if label_override else Path(path).stem
        if len(nome) > 22: nome = nome[:20] + "…"
        self._nome = nome

        self._cw = CAPA_W + 40
        self._ch = CAPA_H + 40

        self.frame = tk.Frame(parent, bg=c["bg"])
        self.cv = tk.Canvas(self.frame, width=self._cw, height=self._ch,
                            bg=c["bg"], highlightthickness=0)
        self.cv.pack()
        self.lbl = tk.Label(self.frame, text=nome, font=FSMALL,
                            bg=c["bg"], fg=c["text_dim"], wraplength=self._cw)
        self.lbl.pack(pady=(0, 3))

        self._draw(0.0)
        for w in (self.cv, self.lbl):
            w.bind("<Enter>",           self._on_enter)
            w.bind("<Leave>",           self._on_leave)
            w.bind("<Double-Button-1>", lambda e: self._open_cb(self._path))
            w.bind("<Button-1>",        lambda e: self._open_cb(self._path))
            w.bind("<Button-3>",        self._show_context_menu)

    def set_image(self, pil_image):
        self._img_pil = pil_image
        self._draw(self._alpha)

    def _draw(self, alpha: float):
        c  = THEME
        cw, ch = self._cw, self._ch
        cv = self.cv
        cv.delete("all")
        scale  = 1.0 + (self.SCALE_MAX - 1.0) * ease_out(alpha)
        iw, ih = int(CAPA_W * scale), int(CAPA_H * scale)
        px, py = (cw - iw) // 2, (ch - ih) // 2

        s_off = int(4 + alpha * 4)
        s_color = "#1a3a6a" if alpha > 0.4 else c["shadow"]
        _rrect(cv, px + s_off, py + s_off, px + iw + s_off - 1, py + ih + s_off - 1, 20, fill=s_color)

        img_to_draw = self._img_pil if self._img_pil is not None else get_placeholder_pil()
        if img_to_draw:
            resized = img_to_draw.resize((iw, ih), Image.BILINEAR)
            if alpha > 0.01:
                overlay = Image.new("RGBA", (iw, ih), (0, 0, 0, int(120 * alpha)))
                resized = Image.alpha_composite(resized.convert("RGBA"), overlay).convert("RGB")
            mask = Image.new("L", (iw, ih), 0)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, iw - 1, ih - 1], radius=CARD_R, fill=255)
            result = Image.new("RGB", (iw, ih),
                               tuple(int(c["surface_alt"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4)))
            result.paste(resized, mask=mask)
            self._tk_img = ImageTk.PhotoImage(result)
            cv.create_image(px, py, anchor="nw", image=self._tk_img)
            if self._img_pil is None:
                cv.create_rectangle(px, py, px+iw, py+ih, fill="", outline=c["border"], width=1)
                cv.create_text(cw//2, ch//2, text="…", font=FSMALL, fill=c["text_muted"])
            if alpha > 0.3 and self._img_pil is not None:
                a_int = int(255 * min(1.0, (alpha - 0.3) / 0.7))
                mx, my = cw // 2, ch // 2 - 10
                cv.create_text(mx, my - 4, text="▶",
                               font=("Segoe UI Symbol", int(22 * scale)),
                               fill=f"#{a_int:02x}{a_int:02x}{a_int:02x}")
                cv.create_text(mx, my + 26, text=self._nome,
                               font=("Segoe UI", 8, "bold"),
                               fill=f"#{a_int:02x}{a_int:02x}{a_int:02x}", width=iw - 16)
        border_col = "#60b4ff" if alpha > 0.4 else c["border"]
        bw = 2 if alpha > 0.4 else 1
        _rrect(cv, px, py, px + iw - 1, py + ih - 1, CARD_R, outline=border_col, width=bw)

        status = get_manual_status(self._path)
        if status == "done":
            cv.create_oval(px+4, py+4, px+18, py+18, fill="#2a5c3a", outline="")
            cv.create_text(px+11, py+11, text="✓", font=(_SANS, 7, "bold"), fill="#5dde8a", anchor="center")
        elif status == "reading":
            cv.create_oval(px+4, py+4, px+18, py+18, fill="#1e3a5c", outline="")
            cv.create_text(px+11, py+11, text="▶", font=(_SANS, 6, "bold"), fill="#5aabff", anchor="center")
        if is_favorite(self._path):
            fav_icon = ICONS.get("favorited")
            if fav_icon:
                cv.create_image(px + iw - 14, py + 12, image=fav_icon, anchor="center")
            else:
                cv.create_text(px + iw - 12, py + 12, text="★", font=(_SANS, 11, "bold"),
                               fill="#f5c842", anchor="center")

    def _show_context_menu(self, event):
        path = self._path
        c = THEME
        menu = tk.Menu(self._root, tearoff=0,
                       bg=c["surface"], fg=c["text"],
                       activebackground=c["accent"], activeforeground="#ffffff",
                       relief="flat", borderwidth=1,
                       font=FSMALL)

        fav_label = "★  Desfavoritar" if is_favorite(path) else "☆  Favoritar"
        def toggle_fav():
            toggle_favorite(path)
            self._draw(self._alpha)
        menu.add_command(label=fav_label, command=toggle_fav)
        menu.add_separator()

        cur = get_manual_status(path)

        def set_reading():
            if cur == "reading":
                set_manual_status(path, None)
            else:
                set_manual_status(path, "reading")
            self._draw(self._alpha)
        reading_label = "▶  Lendo  ✓" if cur == "reading" else "▶  Marcar como Lendo"
        menu.add_command(label=reading_label, command=set_reading)

        def set_done():
            if cur == "done":
                set_manual_status(path, None)
            else:
                set_manual_status(path, "done")
            self._draw(self._alpha)
        done_label = "✓  Concluído  ✓" if cur == "done" else "✓  Marcar como Concluído"
        menu.add_command(label=done_label, command=set_done)

        menu.add_separator()
        menu.add_command(label="▶  Abrir", command=lambda: self._open_cb(path))

        menu.add_separator()
        menu.add_command(label="📤  Publicar na comunidade", command=lambda: self._publish())

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _publish(self):
        user = getattr(self._root, "current_user", None)
        if not _ACCOUNTS_AVAILABLE or user is None:
            messagebox.showinfo(
                "Conta necessária",
                "Crie uma conta ou entre com uma existente para publicar na comunidade.\n\n"
                "Use \"Sair\" na barra lateral se quiser trocar de conta, ou reabra o app "
                "e escolha \"Entrar\"/\"Cadastrar\" em vez de convidado.",
            )
            return
        PublishDialog(self._root, self._path, user)

    def _animate(self, target: float):
        if self._anim_id:
            self._root.after_cancel(self._anim_id); self._anim_id = None
        step = (1.0 / self.HOVER_STEPS) * (1 if target > self._alpha else -1)
        def tick():
            self._alpha += step
            if (step > 0 and self._alpha >= target) or (step < 0 and self._alpha <= target):
                self._alpha = target
                self._draw(self._alpha)
                self.lbl.config(fg=THEME["text"] if target > 0.5 else THEME["text_dim"],
                                font=("Segoe UI", 9, "bold") if target > 0.5 else FSMALL)
                return
            self._draw(self._alpha)
            self._anim_id = self._root.after(self.HOVER_MS, tick)
        tick()

    def _on_enter(self, e): self._animate(1.0)
    def _on_leave(self, e): self._animate(0.0)
    def grid(self, **kwargs): self.frame.grid(**kwargs)


class CollectionCard:
    HOVER_STEPS = 10
    HOVER_MS    = 14
    SCALE_MAX   = 1.08

    def __init__(self, parent, collection: dict, open_cb, detail_cb, root):
        self._collection = collection
        self._open_cb = open_cb
        self._detail_cb = detail_cb
        self._root = root
        self._alpha = 0.0
        self._anim_id = None
        self._tk_imgs = []

        c = THEME
        files = collection["files"]
        name = collection["name"]
        if len(name) > 22: name = name[:20] + "…"
        self._name = name
        self._files = files

        lidas, total, ultima = collection_read_count(files)
        self._lidas, self._total, self._ultima = lidas, total, ultima

        self._capas_pil = []
        for fpath in files[:3]:
            try:
                cf = _cover_cache_path(fpath)
                if os.path.exists(cf):
                    self._capas_pil.append(Image.open(cf).convert("RGB"))
                else:
                    data = extract_cover_only(fpath)
                    img = Image.open(io.BytesIO(data)).convert("RGB")
                    img.thumbnail((CAPA_W, CAPA_H), Image.BILINEAR)
                    self._capas_pil.append(img)
            except:
                self._capas_pil.append(None)

        self._cw = CAPA_W + 60
        self._ch = CAPA_H + 60

        self.frame = tk.Frame(parent, bg=c["bg"])
        self.cv = tk.Canvas(self.frame, width=self._cw, height=self._ch,
                            bg=c["bg"], highlightthickness=0)
        self.cv.pack()
        self.lbl = tk.Label(self.frame, text=self._name, font=FSMALL,
                            bg=c["bg"], fg=c["text_dim"], wraplength=self._cw)
        self.lbl.pack(pady=(0, 1))
        self._prog_frame = tk.Frame(self.frame, bg=c["bg"])
        self._prog_frame.pack(pady=(0, 3))
        self._draw_progress_bar()
        self._draw(0.0)
        for w in (self.cv, self.lbl):
            w.bind("<Enter>",           self._on_enter)
            w.bind("<Leave>",           self._on_leave)
            w.bind("<Double-Button-1>", lambda e: self._detail_cb(self._collection))
            w.bind("<Button-1>",        lambda e: self._detail_cb(self._collection))

    def _draw_progress_bar(self):
        for w in self._prog_frame.winfo_children():
            w.destroy()
        c = THEME
        if self._total == 0: return
        pct = self._lidas / self._total
        bar_w, bar_h = CAPA_W, 4
        cv = tk.Canvas(self._prog_frame, width=bar_w, height=bar_h, bg=c["bg"], highlightthickness=0)
        cv.pack(side="left", padx=(10, 4))
        cv.create_rectangle(0, 0, bar_w, bar_h, fill=c["progress_bg"], outline="")
        filled = int(bar_w * pct)
        if filled > 0:
            cv.create_rectangle(0, 0, filled, bar_h, fill=c["accent"], outline="")
        tk.Label(self._prog_frame, text=f"{self._lidas}/{self._total} {TEXTS[LANG]['read']}",
                 font=FTINY, bg=c["bg"], fg=c["text_dim"]).pack(side="left")

    def _make_stack_image(self, alpha):
        c = THEME
        cw, ch = self._cw, self._ch
        scale = 1.0 + (self.SCALE_MAX - 1.0) * ease_out(alpha)
        iw, ih = int(CAPA_W * scale), int(CAPA_H * scale)
        bg_hex = c["bg"].lstrip("#")
        bg_rgb = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
        canvas_img = Image.new("RGBA", (cw, ch), (*bg_rgb, 255))
        rotations  = [6, -4, 0]
        offsets_x  = [-8, 6, 0]
        offsets_y  = [4, -4, 0]
        shadow_cols = [(0,0,0,80),(0,0,0,60),(0,0,0,120)]
        cx, cy = cw // 2, ch // 2 - 4
        n_capas = len(self._capas_pil)
        layers = min(3, n_capas) if n_capas > 0 else 1
        for i in range(layers - 1, -1, -1):
            pil = self._capas_pil[i] if i < len(self._capas_pil) else None
            rot = rotations[i] * (1 + alpha * 0.3)
            ox, oy = offsets_x[i], offsets_y[i]
            layer = Image.new("RGBA", (iw, ih), (50, 50, 60, 255))
            if pil:
                resized = pil.resize((iw, ih), Image.BILINEAR)
                if i < layers - 1:
                    overlay = Image.new("RGBA", (iw, ih), (0, 0, 0, int(80 * (layers - 1 - i) / layers)))
                    resized = Image.alpha_composite(resized.convert("RGBA"), overlay)
                else:
                    resized = resized.convert("RGBA")
                    if alpha > 0.01:
                        ov = Image.new("RGBA", (iw, ih), (0, 0, 0, int(100 * alpha)))
                        resized = Image.alpha_composite(resized, ov)
                layer = resized
            mask = Image.new("L", (iw, ih), 0)
            ImageDraw.Draw(mask).rounded_rectangle([0,0,iw-1,ih-1], radius=CARD_R, fill=255)
            layer.putalpha(mask)
            if abs(rot) > 0.1:
                layer = layer.rotate(rot, expand=True, resample=Image.BICUBIC)
            lw, lh = layer.size
            px, py = cx - lw // 2 + ox, cy - lh // 2 + oy
            shadow = Image.new("RGBA", (lw+8, lh+8), (0,0,0,0))
            shadow.paste(Image.new("RGBA", (lw, lh), shadow_cols[i]), (4, 4))
            canvas_img.alpha_composite(shadow, (px-4, py-4))
            canvas_img.alpha_composite(layer, (px, py))
        return canvas_img.convert("RGB"), iw, ih, cx, cy

    def _draw(self, alpha):
        c = THEME
        cw, ch = self._cw, self._ch
        cv = self.cv
        cv.delete("all")
        self._tk_imgs.clear()
        stack_img, iw, ih, cx, cy = self._make_stack_image(alpha)
        tk_img = ImageTk.PhotoImage(stack_img)
        self._tk_imgs.append(tk_img)
        cv.create_image(0, 0, anchor="nw", image=tk_img)
        n = self._total
        bx, by = cw - 22, 18
        cv.create_oval(bx-12, by-10, bx+12, by+10, fill=c["accent"], outline="")
        cv.create_text(bx, by, text=f"{n}", font=("Segoe UI", 8, "bold"), fill="#fff", anchor="center")
        if self._lidas > 0:
            cv.create_rectangle(18, by-10, 18+52, by+10, fill=c["read_badge"], outline="")
            cv.create_text(18+26, by, text=f"✓ {self._lidas} {TEXTS[LANG]['read']}",
                           font=("Segoe UI", 7, "bold"), fill=c["read_badge_text"], anchor="center")
        if alpha > 0.3:
            a_int = int(255 * min(1.0, (alpha - 0.3) / 0.7))
            col_hex = f"#{a_int:02x}{a_int:02x}{a_int:02x}"
            scale = 1.0 + (self.SCALE_MAX - 1.0) * ease_out(alpha)
            cv.create_text(cx, cy-6, text="▶", font=("Segoe UI Symbol", int(22*scale)), fill=col_hex)
            cv.create_text(cx, cy+26, text=self._name, font=("Segoe UI", 8, "bold"),
                           fill=col_hex, width=iw-16)

    def _animate(self, target):
        if self._anim_id:
            self._root.after_cancel(self._anim_id); self._anim_id = None
        step = (1.0 / self.HOVER_STEPS) * (1 if target > self._alpha else -1)
        def tick():
            self._alpha += step
            if (step > 0 and self._alpha >= target) or (step < 0 and self._alpha <= target):
                self._alpha = target
                self._draw(self._alpha)
                self.lbl.config(fg=THEME["text"] if target > 0.5 else THEME["text_dim"],
                                font=("Segoe UI", 9, "bold") if target > 0.5 else FSMALL)
                return
            self._draw(self._alpha)
            self._anim_id = self._root.after(self.HOVER_MS, tick)
        tick()

    def _on_enter(self, e): self._animate(1.0)
    def _on_leave(self, e): self._animate(0.0)
    def grid(self, **kwargs): self.frame.grid(**kwargs)


def _serie_name(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r'\s*[\(\[]?\d{4}[\)\]]?\s*', ' ', stem)
    stem = re.sub(r'\s*[#nNvV°º]\.?\s*\d+.*$', '', stem)
    stem = re.sub(r'\s+\d+\s*$', '', stem)
    stem = re.sub(r'\s*[-–—]\s*.*$', '', stem)
    stem = stem.strip(" ._-")
    return stem if stem else Path(filename).stem


def scan_collections(folder: str) -> dict:
    exts = (".cbz", ".cbr", ".zip", ".rar", ".pdf")
    result = {"subfolders": [], "series": []}
    if not folder or not os.path.isdir(folder):
        return result

    def _scan_dir(base_path, depth=0):
        collected = []
        try:
            entries = sorted(os.scandir(base_path), key=lambda e: natural_key(e.name))
        except PermissionError:
            return collected
        for entry in entries:
            if not entry.name.startswith(".") and entry.is_dir() and depth < 3:
                sub = _scan_dir(entry.path, depth + 1)
                direct_files = sorted([
                    os.path.join(entry.path, f)
                    for f in os.listdir(entry.path)
                    if f.lower().endswith(exts) and os.path.isfile(os.path.join(entry.path, f))
                ], key=natural_key)
                if direct_files:
                    collected.append({"name": entry.name, "path": entry.path, "files": direct_files})
                collected.extend(sub)
        return collected

    result["subfolders"] = _scan_dir(folder)
    root_files = sorted([
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(exts) and os.path.isfile(os.path.join(folder, f))
    ], key=natural_key)
    series_map = {}
    for fpath in root_files:
        key = _serie_name(os.path.basename(fpath))
        series_map.setdefault(key, []).append(fpath)
    for name, files in sorted(series_map.items()):
        if len(files) >= 2:
            result["series"].append({"name": name, "files": sorted(files, key=natural_key)})
    return result


def _sort_collections(items, mode):
    if mode == "name":
        return sorted(items, key=lambda x: natural_key(x["name"]))
    elif mode == "date":
        def _mtime(item):
            try: return max(os.path.getmtime(f) for f in item["files"])
            except: return 0
        return sorted(items, key=_mtime, reverse=True)
    elif mode == "progress":
        def _pct(item):
            lidas, total, _ = collection_read_count(item["files"])
            return lidas / total if total > 0 else 0
        return sorted(items, key=_pct, reverse=True)
    return items


import xml.etree.ElementTree as ET

def read_comic_info(path: str) -> dict:
    info = {}
    try:
        if not zipfile.is_zipfile(path):
            return info
        with zipfile.ZipFile(path, "r") as z:
            ci_name = next((n for n in z.namelist()
                            if Path(n).name.lower() == "comicinfo.xml"), None)
            if ci_name is None: return info
            root = ET.fromstring(z.read(ci_name))
            tag_map = {"Title":"title","Series":"series","Number":"number","Year":"year",
                       "Writer":"writer","Penciller":"penciller","Inker":"inker",
                       "Colorist":"colorist","Publisher":"publisher","Summary":"summary",
                       "Genre":"genre","PageCount":"page_count","LanguageISO":"language","Web":"web"}
            for xml_tag, key in tag_map.items():
                el = root.find(xml_tag)
                if el is not None and el.text and el.text.strip():
                    info[key] = el.text.strip()
    except Exception:
        pass
    return info


_COMIC_INFO_CACHE = {}

def get_comic_info(path):
    if path not in _COMIC_INFO_CACHE:
        _COMIC_INFO_CACHE[path] = read_comic_info(path)
    return _COMIC_INFO_CACHE.get(path, {})

def comic_display_title(path):
    info = get_comic_info(path)
    if info.get("series") and info.get("number"):
        return f"{info['series']} #{info['number']}"
    if info.get("title"): return info["title"]
    if info.get("series"): return info["series"]
    return Path(path).stem


class MetaTooltip:
    def __init__(self, root):
        self._root = root
        self._win = None
        self._after = None

    def show(self, widget, path):
        info = get_comic_info(path)
        if not info: return
        self._cancel()
        self._after = self._root.after(600, lambda: self._create(widget, path, info))

    def hide(self):
        self._cancel()
        if self._win:
            try: self._win.destroy()
            except Exception as _e: log.debug("silenced: %s", _e)
            self._win = None

    def _cancel(self):
        if self._after:
            self._root.after_cancel(self._after); self._after = None

    def _create(self, widget, path, info):
        if self._win:
            try: self._win.destroy()
            except Exception as _e: log.debug("silenced: %s", _e)
        c = THEME
        self._win = tk.Toplevel(self._root)
        self._win.overrideredirect(True)
        self._win.configure(bg=c["surface"])
        tk.Canvas(self._win, height=2, bg=c["accent"], highlightthickness=0).pack(fill="x")
        frame = tk.Frame(self._win, bg=c["surface"], padx=12, pady=8); frame.pack()
        tk.Label(frame, text=comic_display_title(path), font=FBTN,
                 bg=c["surface"], fg=c["text"], wraplength=220).pack(anchor="w")
        tk.Frame(frame, bg=c["border"], height=1).pack(fill="x", pady=(4, 6))
        for key, label in [("series","Série"),("number","Nº"),("year","Ano"),
                           ("writer","Roteiro"),("penciller","Desenho"),
                           ("publisher","Editora"),("genre","Gênero")]:
            val = info.get(key, "")
            if val:
                row = tk.Frame(frame, bg=c["surface"]); row.pack(fill="x", pady=1)
                tk.Label(row, text=f"{label}:", font=FTINY, bg=c["surface"],
                         fg=c["text_dim"], width=8, anchor="e").pack(side="left")
                tk.Label(row, text=val, font=FTINY, bg=c["surface"], fg=c["text"],
                         anchor="w", wraplength=150).pack(side="left", padx=(4, 0))
        if info.get("summary"):
            tk.Frame(frame, bg=c["border"], height=1).pack(fill="x", pady=(6, 4))
            tk.Label(frame, text=info["summary"], font=FTINY, bg=c["surface"],
                     fg=c["text_dim"], wraplength=220, justify="left").pack(anchor="w")
        self._win.update_idletasks()
        wx = widget.winfo_rootx() + widget.winfo_width() + 6
        wy = widget.winfo_rooty()
        sw, sh = self._root.winfo_screenwidth(), self._root.winfo_screenheight()
        tw, th = self._win.winfo_width(), self._win.winfo_height()
        if wx + tw > sw - 10: wx = widget.winfo_rootx() - tw - 6
        if wy + th > sh - 10: wy = sh - th - 10
        self._win.geometry(f"+{wx}+{wy}")
        self._win.configure(highlightbackground=c["border"], highlightthickness=1)

class SearchBubble:
    BUBBLE_SIZE  = 46
    BUBBLE_ANIM  = 12
    BUBBLE_MS    = 12
    EXPAND_WIDTH = 220
    PAD_RIGHT    = 18
    PAD_BOTTOM   = 18

    def __init__(self, parent, on_change, on_clear, root):
        self._parent = parent
        self._on_change = on_change
        self._on_clear = on_clear
        self._root = root
        self._expanded = False
        self._anim_id = None
        self._anim_t = 0.0
        self._search_job = None

        c = THEME
        BS = self.BUBBLE_SIZE
        self._frame = tk.Frame(parent, bg=c["bg"])
        self._cv = tk.Canvas(self._frame, height=BS, bg=c["bg"], highlightthickness=0)
        self._cv.pack(fill="x")
        self._var = tk.StringVar()
        self._entry = tk.Entry(self._frame, textvariable=self._var, font=FLABEL,
                               bg=c["accent"], fg="#ffffff", insertbackground="#ffffff",
                               relief="flat", highlightthickness=0, bd=0)
        self._clear_btn = tk.Label(self._frame, text="✕", font=("Segoe UI", 9),
                                   bg=c["accent"], fg="#ffffff", cursor="hand2", padx=4)
        self._cv.bind("<Enter>", lambda e: self._open())
        self._cv.bind("<Button-1>", lambda e: self._open())
        self._frame.bind("<Leave>", self._on_frame_leave)
        self._cv.bind("<Leave>", self._on_frame_leave)
        self._clear_btn.bind("<Button-1>", lambda e: self._do_clear())
        self._var.trace_add("write", self._on_text_change)
        self._entry.bind("<Escape>", lambda e: self._close())
        self._entry.bind("<Return>", lambda e: self._close())
        parent.bind("<Configure>", lambda e: self._reposition())
        self._draw_bubble(0.0)
        self.reposition_after = parent.after(100, self._reposition)

    def _reposition(self):
        pw, ph = self._parent.winfo_width(), self._parent.winfo_height()
        if pw < 10 or ph < 10: return
        target_w = self._target_width()
        x = pw - target_w - self.PAD_RIGHT
        y = ph - self.BUBBLE_SIZE - self.PAD_BOTTOM
        self._frame.place(in_=self._parent, x=x, y=y, width=target_w, height=self.BUBBLE_SIZE)

    def _target_width(self):
        t = ease_out(self._anim_t)
        return int(self.BUBBLE_SIZE + (self.EXPAND_WIDTH - self.BUBBLE_SIZE) * t)

    def _draw_bubble(self, t):
        BS = self.BUBBLE_SIZE
        w = self._target_width()
        r = BS // 2
        self._cv.config(width=w, height=BS)
        self._cv.delete("all")
        acc = THEME["accent"]
        border_glow = THEME["border_glow"]
        self._cv.create_oval(3, 3, BS+1, BS+1, fill=THEME["shadow"], outline="")
        self._cv.create_oval(0, 0, BS, BS, fill=acc, outline="")
        if t > 0.01:
            self._cv.create_rectangle(r, 0, w - r, BS, fill=acc, outline="")
            self._cv.create_oval(w - BS, 0, w, BS, fill=acc, outline="")
            outline_w = 2
            self._cv.create_arc(0, 0, BS, BS, start=90, extent=180,
                                style="arc", outline=border_glow, width=outline_w)
            self._cv.create_line(r, 0, w - r, 0, fill=border_glow, width=outline_w)
            self._cv.create_line(r, BS, w - r, BS, fill=border_glow, width=outline_w)
            self._cv.create_arc(w - BS, 0, w, BS, start=270, extent=180,
                                style="arc", outline=border_glow, width=outline_w)
        else:
            self._cv.create_oval(1, 1, BS - 1, BS - 1, fill=acc, outline=border_glow, width=2)
        self._cv.create_text(w - r, r, text="⌕", font=(_SANS, 15),
                             fill="#ffffff", anchor="center")
        if t > 0.15:
            entry_w = max(0, w - BS - 24)
            self._entry.place(in_=self._cv, x=10, y=8, width=entry_w, height=BS - 16)
            if t > 0.6 and self._var.get():
                self._clear_btn.place(in_=self._cv, x=w - BS - 20, y=12, width=18, height=BS - 24)
            else:
                self._clear_btn.place_forget()
        else:
            self._entry.place_forget()
            self._clear_btn.place_forget()

    def _animate_to(self, target):
        if self._anim_id:
            self._root.after_cancel(self._anim_id)
        step = (1.0 / self.BUBBLE_ANIM) * (1 if target > self._anim_t else -1)
        def tick():
            self._anim_t += step
            done = False
            if step > 0 and self._anim_t >= target: self._anim_t = target; done = True
            elif step < 0 and self._anim_t <= target: self._anim_t = target; done = True
            self._draw_bubble(self._anim_t); self._reposition()
            if not done:
                self._anim_id = self._root.after(self.BUBBLE_MS, tick)
            else:
                self._anim_id = None
                if target > 0.5: self._entry.focus_set()
        tick()

    def _open(self):
        if self._anim_t < 0.9:
            self._expanded = True
            self._animate_to(1.0)

    def _close(self):
        self._expanded = False
        self._entry.place_forget()
        self._animate_to(0.0)
        self._root.focus_set()

    def _on_frame_leave(self, e):
        if not self._var.get() and self._expanded:
            wx, wy = self._frame.winfo_rootx(), self._frame.winfo_rooty()
            ww, wh = self._frame.winfo_width(), self._frame.winfo_height()
            mx, my = self._frame.winfo_pointerx(), self._frame.winfo_pointery()
            if not (wx <= mx <= wx + ww and wy <= my <= wy + wh):
                self._close()

    def _on_text_change(self, *args):
        val = self._var.get()
        if self._search_job: self._root.after_cancel(self._search_job)
        self._search_job = self._root.after(280, lambda: self._on_change(val))
        self._draw_bubble(self._anim_t)

    def _do_clear(self):
        self._var.set(""); self._on_clear(); self._entry.focus_set()

    def update_theme(self):
        c = THEME
        self._entry.config(bg=c["accent"], fg="#ffffff", insertbackground="#ffffff")
        self._clear_btn.config(bg=c["accent"])
        self._frame.config(bg=c["bg"]); self._cv.config(bg=c["bg"])
        self._draw_bubble(self._anim_t)

    def set_text(self, text): self._var.set(text)
    def get_text(self): return self._var.get()
    def destroy(self):
        try: self._frame.destroy()
        except Exception as _e: log.debug("silenced: %s", _e)


class LibraryWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        try: self.iconbitmap(resource_path("panel.ico"))
        except Exception as _e: log.debug("silenced: %s", _e)
        self.withdraw()
        self.title("PANEL — Biblioteca")
        self.configure(bg=THEME["bg"])

        self._capa_cache   = {}
        self._resize_job   = None
        self._last_ncols   = 0
        self._col_filter   = "all"
        self._col_sort     = "name"
        self._status_filter= "all"
        self._search_query = ""
        self._card_map     = {}
        self._cover_loader = None
        self._search_bubble= None
        self._meta_tooltip = None
        self._sync_job = None
        register_change_listener(self._schedule_sync)
        self._notification_count = 0

        self.current_user = None  # None = convidado; preenchido após login/cadastro

        load_icons()
        load_library_config()
        prefs = load_prefs()
        if prefs.get("lang"):
            self.after(10, self._show_auth)
        else:
            LangWindow(self, self._show_auth)

    def _show_auth(self):
        # Restaura uma sessão somente depois de validá-la sem bloquear a UI.
        existing = session_store.load_session() if _ACCOUNTS_AVAILABLE else None
        if existing:
            def validate():
                try:
                    user = api_client.get_current_user(existing.token)
                    outcome = (user, True)
                except api_client.ApiUnavailableError:
                    # A biblioteca local continua utilizável offline.
                    outcome = (existing, True)
                except Exception:
                    session_store.clear_session()
                    outcome = (None, False)
                self.after(0, lambda: self._finish_saved_session(*outcome))

            threading.Thread(target=validate, daemon=True).start()
        else:
            AuthWindow(self, self._on_auth_done)

    def _finish_saved_session(self, user, usable):
        if usable:
            self.current_user = user
            if user is not None:
                self._sync_library_state(user)
            self._start()
        else:
            AuthWindow(self, self._on_auth_done)

    def _on_auth_done(self, auth):
        # auth é None no modo convidado, ou um AuthResponse/LocalSession
        # com token+usuário. Em nenhum dos dois casos isso bloqueia o
        # restante do app — biblioteca, leitor e coleções continuam
        # funcionando exatamente como hoje.
        self.current_user = auth
        if auth is not None:
            self._sync_library_state(auth)
        self._start()

    def _sync_library_state(self, auth):
        def worker():
            try:
                progress, favorites = load_progress(), set(load_favorites())
                payload, paths_by_id = build_sync_payload(progress, favorites)
                merged = api_client.sync_library_state(auth.token, payload)
                changed = False
                for item in merged:
                    path = paths_by_id.get(item["item_key"])
                    if not path: continue
                    local = progress.get(path, {})
                    local_stamp = local.get("ts", 0) if isinstance(local, dict) else 0
                    remote_stamp = float(item.get("client_updated_at") or 0)
                    if item.get("page") is not None and remote_stamp > local_stamp:
                        progress[path] = {"page": item["page"], "ts": remote_stamp}; changed = True
                    if remote_stamp >= local_stamp:
                        if item.get("favorite"): favorites.add(path)
                        else: favorites.discard(path)
                        changed = True
                if changed:
                    _json_save(PROGRESS_FILE, progress); _json_save(FAVORITES_FILE, sorted(favorites))
            except Exception:
                log.debug("Sincronização da biblioteca indisponível", exc_info=True)
        threading.Thread(target=worker, daemon=True).start()

    def _schedule_sync(self, _kind=None, _path=None):
        if self.current_user is None:return
        if self._sync_job is not None:
            try:self.after_cancel(self._sync_job)
            except Exception:pass
        self._sync_job=self.after(1500,lambda:self._sync_library_state(self.current_user))

    def _open_profile(self):
        self._active_tab = "profile"
        self._build_shell()
        render_profile(
            self._main, self, self.current_user, api_client, THEME,
            (FTITLE, FLABEL, FSMALL), self._profile_updated,
        )

    def _profile_updated(self, data):
        self.current_user.display_name = data.get("display_name") or self.current_user.display_name
        if hasattr(self.current_user, "email"):
            self.current_user.email = data.get("email")

    def _open_notifications(self):
        self._active_tab = "notifications"
        self._build_shell()
        render_notifications(
            self._main, self, self.current_user, api_client, THEME,
            (FTITLE, FLABEL, FSMALL), self._set_notification_count,
        )

    def _set_notification_count(self, count):
        self._notification_count = max(0, int(count or 0))

    def _refresh_notification_count(self):
        if self.current_user is None:
            return
        def worker():
            try:
                items = api_client.notifications(self.current_user.token)
                count = sum(not item.get("read_at") for item in items)
            except Exception:
                return
            self.after(0, lambda: self._set_notification_count(count))
        threading.Thread(target=worker, daemon=True).start()

    def _open_downloads(self):
        self._active_tab = "downloads"
        self._build_shell()
        render_downloads(self._main, THEME, (FTITLE, FLABEL, FSMALL))

    def _logout(self):
        if _ACCOUNTS_AVAILABLE and self.current_user is not None:
            token = getattr(self.current_user, "token", None)
            if token:
                try:
                    api_client.logout(token)
                except Exception as _e:
                    log.debug("silenced: %s", _e)  # best-effort; segue com a limpeza local
            session_store.clear_session()
        self.current_user = None
        # Reabre a tela de login por cima da biblioteca (mesmo padrão do
        # início do app); ao escolher de novo, _on_auth_done reconstrói
        # o shell — biblioteca local, progresso e favoritos não mudam.
        AuthWindow(self, self._on_auth_done)

    def _open_moderation(self):
        if self.current_user is None:
            messagebox.showinfo("Moderação", "Entre em uma conta para continuar.")
            return
        role = getattr(self.current_user, "role", "user")
        if can_moderate(self.current_user):
            self._active_tab = "moderation"
            self._build_shell()
            self._render_moderation_tab()
            return

        messagebox.showerror("Moderação", "Sua conta não possui acesso à moderação.", parent=self)
        return

    def _claim_admin_token(self):
        if getattr(self.current_user, "role", "user") != "moderator":
            return
        setup_token = simpledialog.askstring(
            "Ativar administrador",
            "Digite o token de administrador:", parent=self, show="•",
        )
        if not setup_token:
            return

        def worker():
            try:
                promoted = api_client.claim_admin(
                    self.current_user.token, setup_token.strip()
                )
                outcome = (promoted, None)
            except (api_client.ApiAuthError, api_client.ApiServerError) as exc:
                outcome = (None, str(exc))
            except api_client.ApiUnavailableError:
                outcome = (None, "Servidor indisponível.")
            except Exception:
                log.exception("Falha ao ativar administrador")
                outcome = (None, "Não foi possível ativar o cargo de administrador.")
            self.after(0, lambda: self._finish_moderator_claim(*outcome))

        threading.Thread(target=worker, daemon=True).start()

    def _open_discovery(self):
        CommunityWindow(self, user=self.current_user, mine=False)

    def _open_my_publications(self):
        if self.current_user is not None:
            CommunityWindow(self, user=self.current_user, mine=True)

    def _finish_moderator_claim(self, promoted, error):
        if error:
            messagebox.showerror("Administrador", error, parent=self)
            return
        self.current_user = promoted
        session_store.save_session(session_store.LocalSession(
            token=promoted.token, user_id=promoted.user_id,
            username=promoted.username, display_name=promoted.display_name,
            is_moderator=True,
            role=getattr(promoted, "role", "admin"),
        ))
        self._build_shell()
        self._active_tab = "moderation"
        self._build_shell()
        self._render_moderation_tab()

    def _render_moderation_tab(self):
        for child in self._main.winfo_children():
            child.destroy()
        self._moderation_images = []
        header = tk.Frame(self._main, bg=THEME["bg"])
        header.pack(fill="x", padx=28, pady=(24, 12))
        tk.Label(header, text="Moderação", font=FTITLE, bg=THEME["bg"],
                 fg=THEME["text"]).pack(side="left")
        make_pill(header, "Atualizar", self._render_moderation_tab,
                  variant="ghost", font=FBTN, pad_x=14, pad_y=7).pack(side="right")
        make_pill(header, "Denúncias", self._render_reports_tab,
                  variant="ghost", font=FBTN, pad_x=14, pad_y=7).pack(side="right", padx=8)
        if getattr(self.current_user, "role", "user") == "moderator":
            make_pill(header, "Usar token de administrador", self._claim_admin_token,
                      variant="accent", font=FSMALL, pad_x=12, pad_y=7).pack(side="right", padx=8)
        self._moderation_status = tk.Label(
            self._main, text="Carregando pedidos…", font=FSMALL,
            bg=THEME["bg"], fg=THEME["text_dim"],
        )
        self._moderation_status.pack(anchor="w", padx=28)

        canvas = tk.Canvas(self._main, bg=THEME["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self._main, orient="vertical", command=canvas.yview)
        self._moderation_grid = tk.Frame(canvas, bg=THEME["bg"])
        self._moderation_grid.bind(
            "<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self._moderation_grid, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True, padx=(20, 0), pady=12)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 if e.delta > 0 else 1, "units"))

        def worker():
            try:
                outcome = (api_client.moderation_queue(
                    self.current_user.token, include_decided=True
                ), None)
            except Exception as exc:
                outcome = (None, str(exc))
            self.after(0, lambda: self._moderation_loaded(*outcome))

        threading.Thread(target=worker, daemon=True).start()

    def _render_reports_tab(self):
        for child in self._main.winfo_children(): child.destroy()
        tk.Label(self._main,text="Denúncias",font=FTITLE,bg=THEME["bg"],fg=THEME["text"]).pack(anchor="w",padx=28,pady=(24,8))
        status=tk.Label(self._main,text="Carregando…",font=FSMALL,bg=THEME["bg"],fg=THEME["text_dim"]);status.pack(anchor="w",padx=28)
        area=tk.Frame(self._main,bg=THEME["bg"]);area.pack(fill="both",expand=True,padx=28,pady=12)
        def worker():
            try: result,error=api_client.admin_reports(self.current_user.token),None
            except Exception as exc: result,error=None,str(exc)
            def done(items,error):
                status.config(text=error or f"{len(items)} denúncia(s)",fg=THEME["accent2"] if error else THEME["text_dim"])
                if error:return
                for item in items:
                    card=tk.Frame(area,bg=THEME["surface"],padx=14,pady=10);card.pack(fill="x",pady=5)
                    tk.Label(card,text=f"{item['target_type']} · {item['reason']} · {item['status']}",font=FLABEL,bg=THEME["surface"],fg=THEME["text"]).pack(anchor="w")
                    tk.Label(card,text=item.get("description") or "Sem descrição",font=FSMALL,bg=THEME["surface"],fg=THEME["text_dim"],wraplength=850,justify="left").pack(anchor="w")
            self.after(0,lambda:done(result,error))
        threading.Thread(target=worker,daemon=True).start()

    def _moderation_loaded(self, items, error):
        if error:
            self._moderation_status.config(text=error, fg=THEME["accent2"])
            return
        pending = sum(item.get("status") == "pending_review" for item in items)
        self._moderation_status.config(
            text=f"{len(items)} pedido(s) no histórico · {pending} pendente(s)"
        )
        if not items:
            tk.Label(self._moderation_grid, text="Nenhum pedido pendente.", font=FTITLE,
                     bg=THEME["bg"], fg=THEME["text_dim"]).grid(row=0, column=0, padx=40, pady=70)
            return
        for index, item in enumerate(items):
            self._create_moderation_card(item, index // 4, index % 4)

    def _create_moderation_card(self, item, row, column):
        card = tk.Frame(self._moderation_grid, bg=THEME["surface"], width=220, height=390)
        card.grid(row=row, column=column, padx=9, pady=9, sticky="n")
        card.grid_propagate(False)
        cover_box = tk.Frame(card, width=190, height=220, bg=THEME["surface_alt"])
        cover_box.pack(padx=10, pady=(10, 7))
        cover_box.pack_propagate(False)
        cover = tk.Label(cover_box,
                         text="Carregando capa…" if item.get("has_file") else "Sem arquivo",
                         bg=THEME["surface_alt"], fg=THEME["text_dim"], font=FTINY)
        cover.pack(fill="both", expand=True)
        tk.Label(card, text=item["title"], font=FBTN, bg=THEME["surface"],
                 fg=THEME["text"], wraplength=195).pack(padx=10)
        status_labels = {"pending_review": "Pendente", "approved": "Aprovado", "rejected": "Rejeitado"}
        tk.Label(card, text=f"{item['author']} · {status_labels.get(item.get('status'), item.get('status'))}", font=FTINY,
                 bg=THEME["surface"], fg=THEME["text_dim"], wraplength=195).pack(padx=10, pady=3)
        buttons = tk.Frame(card, bg=THEME["surface"])
        buttons.pack(side="bottom", fill="x", padx=8, pady=8)
        if item.get("has_file"):
            make_pill(buttons, "Ler", lambda i=item: self._read_moderation_file(i),
                      variant="ghost", font=FTINY, pad_x=8, pad_y=5).pack(side="left")
            make_pill(buttons, "Baixar", lambda i=item: self._download_moderation_file(i),
                      variant="ghost", font=FTINY, pad_x=8, pad_y=5).pack(side="left", padx=3)
            self._load_moderation_cover(item, cover)
        if item.get("status") == "pending_review":
            make_pill(buttons, "✓", lambda i=item: self._moderate_from_tab(i, "approved"),
                      variant="accent", font=FTINY, pad_x=8, pad_y=5).pack(side="right")
            make_pill(buttons, "✕", lambda i=item: self._moderate_from_tab(i, "rejected"),
                      variant="ghost", font=FTINY, pad_x=8, pad_y=5).pack(side="right", padx=3)

    def _load_moderation_cover(self, item, label):
        def worker():
            try:
                data = api_client.moderation_cover(self.current_user.token, item["record_id"])
                image = Image.open(io.BytesIO(data)).convert("RGB")
                image.thumbnail((190, 220), Image.LANCZOS)
                self.after(0, lambda: self._set_moderation_cover(label, image))
            except Exception:
                self.after(0, lambda: label.config(text="Capa indisponível"))
        threading.Thread(target=worker, daemon=True).start()

    def _set_moderation_cover(self, label, image):
        tk_image = ImageTk.PhotoImage(image)
        self._moderation_images.append(tk_image)
        label.config(image=tk_image, text="")

    def _moderation_cache_path(self, item):
        folder = os.path.join(_APPDATA, "moderation_cache")
        os.makedirs(folder, exist_ok=True)
        extension = Path(item.get("original_filename") or ".cbz").suffix or ".cbz"
        return os.path.join(folder, item["record_id"] + extension)

    def _read_moderation_file(self, item):
        destination = self._moderation_cache_path(item)
        self._download_for_action(item, destination, open_after=True)

    def _download_moderation_file(self, item):
        destination = filedialog.asksaveasfilename(
            parent=self, initialfile=item.get("original_filename") or "quadrinho.cbz"
        )
        if destination:
            self._download_for_action(item, destination, open_after=False)

    def _download_for_action(self, item, destination, open_after):
        self._moderation_status.config(text="Baixando arquivo…")
        def worker():
            try:
                api_client.download_moderation_file(
                    self.current_user.token, item["record_id"], destination
                )
                outcome = None
            except Exception as exc:
                outcome = str(exc)
            self.after(0, lambda: self._download_finished(destination, open_after, outcome))
        threading.Thread(target=worker, daemon=True).start()

    def _download_finished(self, destination, open_after, error):
        if error:
            self._moderation_status.config(text=error, fg=THEME["accent2"])
            return
        self._moderation_status.config(text="Download concluído.", fg=THEME["text_dim"])
        if open_after:
            try:
                loader = SmartPageLoader(destination)
                ReaderWindow(self, destination, loader)
            except Exception as exc:
                messagebox.showerror("Leitura", f"Não foi possível abrir o arquivo: {exc}", parent=self)

    def _moderate_from_tab(self, item, decision):
        verb = "aprovar" if decision == "approved" else "rejeitar"
        reason = simpledialog.askstring(
            "Motivo da decisão", f"Explique por que deseja {verb} esta publicação:", parent=self
        )
        if not reason or len(reason.strip()) < 3:
            return
        def worker():
            try:
                api_client.moderate(
                    self.current_user.token, item["record_id"], decision, reason.strip()
                )
                error = None
            except Exception as exc:
                error = str(exc)
            self.after(0, lambda: self._moderation_decided(error))
        threading.Thread(target=worker, daemon=True).start()

    def _moderation_decided(self, error):
        if error:
            messagebox.showerror("Moderação", error, parent=self)
        else:
            self._render_moderation_tab()

    def _start(self):
        self.state("zoomed")
        self.deiconify()
        self._cover_loader = CoverLoader(self, self._capa_cache)
        self._meta_tooltip = MetaTooltip(self)
        self._build_shell()
        self.after(200, self._refresh_library)
        self.after(250, self._refresh_notification_count)

    def _build_shell(self):
        for w in self.winfo_children():
            w.destroy()
        c = THEME
        self._sb = tk.Frame(self, bg=c["surface"], width=190)
        self._sb.pack(side="left", fill="y")
        self._sb.pack_propagate(False)
        lc = tk.Canvas(self._sb, width=190, height=140, bg=c["surface"], highlightthickness=0)
        lc.pack(pady=(10, 4))
        try:
            logo_img = Image.open(resource_path("panellogo.png")).convert("RGBA")
            logo_img.thumbnail((195, 140), Image.LANCZOS)
            self.logo_tk = ImageTk.PhotoImage(logo_img)
            lc.create_image(95, 55, image=self.logo_tk)
        except Exception:
            lc.create_text(95, 35, text="PANEL", font=FLOGO, fill=c["text"])
        lc.create_line(16, 130, 174, 130, fill=c["accent"], width=2)

        def sb_sep():
            tk.Frame(self._sb, bg=c["border"], height=1).pack(fill="x", padx=12, pady=4)
        sb_sep()

        self._active_tab = getattr(self, "_active_tab", "library")
        for label, cmd, tab, icon in [
            (f"  {TEXTS[LANG]['library']}", self._refresh_library, "library", ICONS.get("library")),
            (f"  {TEXTS[LANG]['collections']}", self._show_collections, "collections", ICONS.get("collections")),
        ]:
            active = (self._active_tab == tab)
            self._sidebar_item(label, icon,
                lambda f=cmd, t=tab: (setattr(self, "_active_tab", t), self._build_shell(), f())[-1],
                active=active, font=FBTN, pady=11)
        self._sidebar_item("  Descobrir", ICONS.get("collections"),
                           self._open_discovery, active=False, font=FBTN, pady=11)
        self._sidebar_item("  Downloads", ICONS.get("open"),
                           self._open_downloads, active=(self._active_tab == "downloads"), font=FBTN, pady=11)
        tk.Frame(self._sb, bg=c["surface"]).pack(fill="both", expand=True)
        sb_sep()
        for txt, cmd, icon in [
            (current_theme_label(), self._toggle_theme, ICONS.get("theme")),
            (f"  {TEXTS[LANG]['folder']}", self._choose_folder, ICONS.get("open")),
            ("  Backup", self._do_backup, ICONS.get("backup")),
            ("  Restaurar", self._do_restore, ICONS.get("restore")),
        ]:
            self._sidebar_item(txt, icon, cmd, active=False, font=FLABEL, pady=9)

        if self.current_user is not None:
            sb_sep()
            self._sidebar_item("  Meu perfil", ICONS.get("collections"),
                                self._open_profile, active=(self._active_tab == "profile"), font=FLABEL, pady=9)
            notification_text = "  Notificações"
            if self._notification_count:
                notification_text += f" ({self._notification_count})"
            self._sidebar_item(notification_text, ICONS.get("collections"),
                                self._open_notifications, active=(self._active_tab == "notifications"), font=FLABEL, pady=9)
            self._sidebar_item("  Meus envios", ICONS.get("library"),
                                self._open_my_publications, active=False, font=FLABEL, pady=9)
            role = getattr(self.current_user, "role", "user")
            has_moderation_access = can_moderate(self.current_user)
            if has_moderation_access:
                self._sidebar_item("  Moderação", ICONS.get("collections"),
                                    self._open_moderation,
                                    active=(self._active_tab == "moderation"), font=FLABEL, pady=9)
            username = getattr(self.current_user, "username", "conta")
            self._sidebar_item(f"  Sair ({username})", ICONS.get("logout"),
                                self._logout, active=False, font=FLABEL, pady=9)

        tk.Frame(self._sb, bg=c["surface"], height=8).pack()

        self._main = tk.Frame(self, bg=c["bg"])
        self._main.pack(side="right", fill="both", expand=True)

    def _sidebar_item(self, text, icon, cmd, *, active=False, font=FBTN, pady=11):
        c = THEME
        W = 178
        tmp = tk.Label(self._sb, text=text, font=font)
        th = tmp.winfo_reqheight(); tmp.destroy()
        ih = icon.height() if icon else 0
        H = max(th, ih) + pady * 2
        r = 10
        cv = tk.Canvas(self._sb, width=W, height=H, bg=c["surface"],
                       highlightthickness=0, cursor="hand2", takefocus=0)
        cv.pack(padx=6, pady=2)
        def render(hover):
            cv.delete("all")
            if active:
                _rrect(cv, 1, 2, W - 1, H - 2, r, fill=c["surface_alt"])
                cv.create_rectangle(2, H // 2 - 9, 5, H // 2 + 9, fill=c["accent"], outline="")
                fg = c["text"]
            elif hover:
                _rrect(cv, 1, 2, W - 1, H - 2, r, fill=c["surface_hover"]); fg = c["text"]
            else:
                fg = c["text_dim"]
            x = 16
            if icon:
                cv.create_image(x, H // 2, image=icon, anchor="w"); x += icon.width() + 8
            cv.create_text(x, H // 2, text=text.strip(), font=font, fill=fg, anchor="w")
        render(False)
        cv.bind("<Enter>", lambda e: (None if active else render(True)))
        cv.bind("<Leave>", lambda e: render(False))
        cv.bind("<Button-1>", lambda e: cmd())
        return cv

    def _refresh_library(self):
        c = THEME
        self._card_map.clear()
        if self._cover_loader: self._cover_loader.clear_queue()
        if self._search_bubble:
            try: self._search_bubble.destroy()
            except Exception as _e: log.debug("silenced: %s", _e)
            self._search_bubble = None
        try: self._main.unbind("<Configure>")
        except Exception as _e: log.debug("silenced: %s", _e)
        for w in self._main.winfo_children():
            w.destroy()

        hdr = tk.Frame(self._main, bg=c["bg"])
        hdr.pack(fill="x", padx=20, pady=(16, 6))
        tk.Label(hdr, text=TEXTS[LANG]["library"], font=FTITLE, bg=c["bg"], fg=c["text"]).pack(side="left")
        if LIBRARY_FOLDER:
            short = LIBRARY_FOLDER
            if len(short) > 40: short = "…" + short[-37:]
            tk.Label(hdr, text=short, font=FTINY, bg=c["bg"], fg=c["text_muted"]).pack(side="left", padx=10, pady=(6,0))
        make_pill(hdr, "+  Pasta", self._choose_folder, variant="accent", font=FSMALL).pack(side="right")

        stf = tk.Frame(self._main, bg=c["bg"]); stf.pack(fill="x", padx=20, pady=(0, 4))
        tk.Label(stf, text=f"{TEXTS[LANG]['filter_status']}:", font=FTINY,
                 bg=c["bg"], fg=c["text_dim"]).pack(side="left", padx=(0, 6))
        self._status_btns = {}
        for key, lbl in [("all", TEXTS[LANG]["f_all"]), ("unread", TEXTS[LANG]["f_unread"]),
                         ("reading", TEXTS[LANG]["f_reading"]), ("done", TEXTS[LANG]["f_done"]),
                         ("favorites", "★ Favoritos")]:
            b = make_pill(stf, lbl, lambda k=key: self._set_status_filter(k),
                          variant="soft", font=FTINY, pad_x=12, pad_y=5,
                          active=(self._status_filter == key))
            b.pack(side="left", padx=(0, 4))
            self._status_btns[key] = b

        tk.Frame(self._main, bg=c["border"], height=1).pack(fill="x", padx=20, pady=(0, 4))

        sf = tk.Frame(self._main, bg=c["bg"]); sf.pack(fill="both", expand=True)
        self._lib_canvas = tk.Canvas(sf, bg=c["bg"], highlightthickness=0)
        self._lib_canvas.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(sf, orient="vertical", command=self._lib_canvas.yview)
        sb.pack(side="right", fill="y")
        self._lib_canvas.configure(yscrollcommand=sb.set)
        self._lib_content = tk.Frame(self._lib_canvas, bg=c["bg"])
        self._lib_win_id = self._lib_canvas.create_window((0, 0), window=self._lib_content, anchor="nw")

        def _update_scroll(e=None):
            self._lib_canvas.configure(scrollregion=(0, 0, self._lib_canvas.winfo_width(),
                max(self._lib_canvas.winfo_height(), self._lib_content.winfo_height())))
        self._lib_content.bind("<Configure>", _update_scroll)
        self._lib_canvas.bind("<Configure>", lambda e: (
            self._lib_canvas.itemconfig(self._lib_win_id, width=e.width), _update_scroll()))
        def _on_wheel(e): self._lib_canvas.yview_scroll(-int(e.delta/120), "units")
        self._lib_canvas.bind("<Enter>", lambda e: self._lib_canvas.bind_all("<MouseWheel>", _on_wheel))
        self._lib_canvas.bind("<Leave>", lambda e: self._lib_canvas.unbind_all("<MouseWheel>"))

        self._populate_library_grid()

        def _on_resize(e):
            if self._resize_job: self.after_cancel(self._resize_job)
            self._resize_job = self.after(350, self._check_ncols)
        self._main.bind("<Configure>", _on_resize)

        self._search_bubble = SearchBubble(self._main, self._bubble_search_changed,
                                           self._bubble_search_clear, self)
        if self._search_query:
            self._search_bubble.set_text(self._search_query)

    def _set_status_filter(self, key):
        self._status_filter = key
        self._populate_library_grid()
        for k, b in self._status_btns.items():
            b.pill_set_active(k == key)

    def _bubble_search_changed(self, val):
        self._search_query = val
        self._populate_library_grid()
    def _bubble_search_clear(self):
        self._search_query = ""
        self._populate_library_grid()

    def _status_of(self, path):
        ms = get_manual_status(path)
        if ms in ("reading", "done"):
            return ms
        page = get_progress_page(path)
        if page is None: return "unread"
        try:
            be = ArchiveBackend(path)
            total = be.count
            be.close()
        except Exception as _e:
            log.debug("silenced: %s", _e)
            total = 0
        if total and page >= total - 1: return "done"
        return "reading"

    def _populate_library_grid(self):
        c = THEME
        for w in self._lib_content.winfo_children():
            w.destroy()
        self._card_map.clear()

        arquivos = self._scan()

        prog = load_progress()
        continuar = []
        for p in arquivos:
            entry = prog.get(p)
            if entry is not None:
                ts = entry.get("ts", 0) if isinstance(entry, dict) else 0
                continuar.append((ts, p))
        continuar.sort(reverse=True)
        continuar = [p for _, p in continuar[:6]]

        q = self._search_query.strip().lower()
        if q:
            def _match(p):
                if q in Path(p).stem.lower(): return True
                info = get_comic_info(p)
                return any(q in info.get(f, "").lower()
                           for f in ("title", "series", "writer", "publisher", "genre"))
            arquivos = [p for p in arquivos if _match(p)]

        if self._status_filter == "favorites":
            arquivos = [p for p in arquivos if is_favorite(p)]
        elif self._status_filter != "all":
            arquivos = [p for p in arquivos if self._status_of(p) == self._status_filter]

        if not arquivos and not continuar:
            self._show_empty(self._lib_content, no_results=bool(q))
            return

        self.update_idletasks()
        avail = self._main.winfo_width() - 44
        if avail < 50:
            self.after(200, self._populate_library_grid); return
        card_w = CAPA_W + 24 + GPAD * 2
        ncols = max(2, avail // card_w)
        self._last_ncols = ncols

        if continuar and not q and self._status_filter == "all":
            tk.Label(self._lib_content, text=f"▶  {TEXTS[LANG]['continue_section']}",
                     font=FBTN, bg=c["bg"], fg=c["text_dim"], anchor="w").pack(
                fill="x", padx=GPAD+4, pady=(8, 2))
            cg = tk.Frame(self._lib_content, bg=c["bg"]); cg.pack(padx=GPAD, anchor="nw")
            for i, path in enumerate(continuar):
                card = ComicCard(cg, path, None, self._open, self,
                                 label_override=comic_display_title(path))
                card.grid(row=0, column=i, padx=GPAD//2, pady=GPAD//2)
                self._wire_card(card, path)
            tk.Frame(self._lib_content, bg=c["border"], height=1).pack(fill="x", padx=GPAD, pady=8)

        gf = tk.Frame(self._lib_content, bg=c["bg"])
        gf.pack(padx=GPAD, pady=GPAD, anchor="nw")
        for placed, path in enumerate(arquivos):
            row, col = placed // ncols, placed % ncols
            card = ComicCard(gf, path, None, self._open, self,
                             label_override=comic_display_title(path))
            card.grid(row=row, column=col, padx=GPAD//2, pady=GPAD//2)
            self._card_map[path] = card
            self._wire_card(card, path)

    def _wire_card(self, card, path):
        if self._meta_tooltip:
            tt = self._meta_tooltip
            card.cv.bind("<Enter>",  lambda e, p=path, w=card.cv: tt.show(w, p), add="+")
            card.cv.bind("<Leave>",  lambda e: tt.hide(), add="+")
            card.lbl.bind("<Enter>", lambda e, p=path, w=card.cv: tt.show(w, p), add="+")
            card.lbl.bind("<Leave>", lambda e: tt.hide(), add="+")
        def _on_loaded(p, pil, _card=card):
            try: _card.set_image(pil)
            except Exception: pass
        self._cover_loader.request(path, _on_loaded)

    def _check_ncols(self):
        self._resize_job = None
        avail = self._main.winfo_width() - 44
        if avail < 50: return
        card_w = CAPA_W + 24 + GPAD * 2
        nc = max(2, avail // card_w)
        if nc != self._last_ncols:
            self._populate_library_grid()

    def _show_empty(self, parent, no_results=False):
        c = THEME
        f = tk.Frame(parent, bg=c["bg"]); f.pack(pady=80)
        if no_results:
            tk.Label(f, text="🔍", font=("Segoe UI Emoji", 42), bg=c["bg"], fg=c["text_muted"]).pack(pady=(20, 6))
            tk.Label(f, text=f'{TEXTS[LANG]["no_results"]} "{self._search_query}"',
                     font=FLABEL, bg=c["bg"], fg=c["text_dim"]).pack()
            make_pill(f, "✕  Limpar busca", self._bubble_search_clear,
                      variant="soft", font=FBTN, pad_x=18, pad_y=9).pack(pady=12)
        else:
            tk.Label(f, text="📚", font=("Segoe UI Emoji", 42), bg=c["bg"], fg=c["text_muted"]).pack(pady=(20, 6))
            tk.Label(f, text=TEXTS[LANG]["no_comics"], font=FLABEL, bg=c["bg"], fg=c["text_dim"]).pack()
            make_pill(f, TEXTS[LANG]["add_folder"], self._choose_folder,
                      variant="accent", font=FBTN, pad_x=22, pad_y=11).pack(pady=16)

    def _scan(self):
        exts = (".cbz", ".cbr", ".zip", ".rar", ".pdf")
        if not LIBRARY_FOLDER or not os.path.isdir(LIBRARY_FOLDER):
            return []
        return sorted([os.path.join(LIBRARY_FOLDER, f)
                       for f in os.listdir(LIBRARY_FOLDER)
                       if f.lower().endswith(exts) and os.path.isfile(os.path.join(LIBRARY_FOLDER, f))],
                      key=natural_key)

    def _open(self, path, sibling_list=None):
        try:
            loader = SmartPageLoader(path)
        except Exception as e:
            messagebox.showerror(TEXTS[LANG]["error"], str(e)); return
        if loader.count == 0:
            messagebox.showerror(TEXTS[LANG]["error"], "Sem imagens."); return

        if sibling_list is None:
            sibling_list = self._siblings_of(path)

        def on_finish(cur_path):
            try:
                i = sibling_list.index(cur_path)
                if i + 1 < len(sibling_list):
                    self._open(sibling_list[i + 1], sibling_list)
            except (ValueError, IndexError):
                pass

        has_next = False
        try:
            i = sibling_list.index(path)
            has_next = (i + 1 < len(sibling_list))
        except ValueError:
            pass

        ReaderWindow(self, path, loader, on_finish=on_finish if has_next else None)

    def _siblings_of(self, path):
        """Acha as outras edições da mesma série/pasta, ordenadas."""
        folder = os.path.dirname(path)
        same_dir = self._scan() if folder == LIBRARY_FOLDER else sorted([
            os.path.join(folder, f) for f in os.listdir(folder)
            if f.lower().endswith((".cbz",".cbr",".zip",".rar",".pdf"))
            and os.path.isfile(os.path.join(folder, f))], key=natural_key)
        if folder == LIBRARY_FOLDER:
            key = _serie_name(os.path.basename(path))
            serie = sorted([p for p in same_dir
                            if _serie_name(os.path.basename(p)) == key], key=natural_key)
            if len(serie) >= 2:
                return serie
        return same_dir

    def _do_backup(self):
        path = filedialog.asksaveasfilename(
            title="Exportar backup", defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile="panel_backup.json")
        if path:
            try:
                export_backup(path)
                messagebox.showinfo("Backup", f"Backup salvo em:\n{path}")
            except Exception as e:
                messagebox.showerror(TEXTS[LANG]["error"], str(e))

    def _do_restore(self):
        path = filedialog.askopenfilename(
            title="Importar backup", filetypes=[("JSON", "*.json")])
        if path:
            try:
                import_backup(path)
                messagebox.showinfo("Restaurar", "Backup importado com sucesso!")
                self._refresh_library()
            except Exception as e:
                messagebox.showerror(TEXTS[LANG]["error"], str(e))

    def _choose_folder(self):
        p = filedialog.askdirectory(title=TEXTS[LANG]["choose_library_folder"],
                                    initialdir=LIBRARY_FOLDER if LIBRARY_FOLDER else None)
        if p:
            save_library_config(p)
            self._capa_cache.clear()
            _COMIC_INFO_CACHE.clear()
            self._search_query = ""
            self._refresh_library()

    def _show_collections(self):
        if self._search_bubble:
            try: self._search_bubble.destroy()
            except Exception as _e: log.debug("silenced: %s", _e)
            self._search_bubble = None
        c = THEME
        try: self._main.unbind("<Configure>")
        except Exception as _e: log.debug("silenced: %s", _e)
        for w in self._main.winfo_children():
            w.destroy()
        hdr = tk.Frame(self._main, bg=c["bg"]); hdr.pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(hdr, text=TEXTS[LANG]["collections"], font=FTITLE, bg=c["bg"], fg=c["text"]).pack(side="left")
        ctrl = tk.Frame(self._main, bg=c["bg"]); ctrl.pack(fill="x", padx=20, pady=(8, 0))
        tabs = tk.Frame(ctrl, bg=c["bg"]); tabs.pack(side="left")
        self._filter_btns = {}
        for key, label in [("all", TEXTS[LANG]["all"]), ("subfolders", TEXTS[LANG]["subfolders"]),
                           ("series", TEXTS[LANG]["series"])]:
            btn = make_pill(tabs, label, lambda k=key: self._set_col_filter(k),
                            variant="soft", font=FSMALL, pad_x=14, pad_y=6,
                            active=(self._col_filter == key))
            btn.pack(side="left", padx=(0, 5)); self._filter_btns[key] = btn
        srt = tk.Frame(ctrl, bg=c["bg"]); srt.pack(side="right")
        tk.Label(srt, text=TEXTS[LANG]["sort_by"], font=FTINY, bg=c["bg"], fg=c["text_dim"]).pack(side="left", padx=(0, 6))
        self._sort_btns = {}
        for key, label in [("name", TEXTS[LANG]["sort_name"]), ("date", TEXTS[LANG]["sort_date"]),
                           ("progress", TEXTS[LANG]["sort_progress"])]:
            btn = make_pill(srt, label, lambda k=key: self._set_col_sort(k),
                            variant="soft", font=FTINY, pad_x=10, pad_y=6,
                            active=(self._col_sort == key))
            btn.pack(side="left", padx=(0, 3)); self._sort_btns[key] = btn
        tk.Frame(self._main, bg=c["border"], height=1).pack(fill="x", padx=20, pady=(8, 4))
        self._col_scroll_area(self._main)

    def _col_scroll_area(self, parent):
        c = THEME
        if hasattr(self, "_col_sf") and self._col_sf.winfo_exists():
            self._col_sf.destroy()
        sf = tk.Frame(parent, bg=c["bg"]); sf.pack(fill="both", expand=True); self._col_sf = sf
        cv = tk.Canvas(sf, bg=c["bg"], highlightthickness=0); cv.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(sf, orient="vertical", command=cv.yview); sb.pack(side="right", fill="y")
        cv.configure(yscrollcommand=sb.set)
        content = tk.Frame(cv, bg=c["bg"])
        wid = cv.create_window((0, 0), window=content, anchor="nw")
        content.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>", lambda e: cv.itemconfig(wid, width=e.width))
        def _on_wheel(e): cv.yview_scroll(-int(e.delta / 120), "units")
        cv.bind("<Enter>", lambda e: cv.bind_all("<MouseWheel>", _on_wheel))
        cv.bind("<Leave>", lambda e: cv.unbind_all("<MouseWheel>"))

        cols = scan_collections(LIBRARY_FOLDER)
        subfolders = _sort_collections(cols["subfolders"], self._col_sort)
        series = _sort_collections(cols["series"], self._col_sort)
        show_sub = self._col_filter in ("all", "subfolders")
        show_ser = self._col_filter in ("all", "series")

        if not (subfolders and show_sub) and not (series and show_ser):
            f = tk.Frame(content, bg=c["bg"]); f.pack(pady=80)
            tk.Label(f, text="🗂️", font=("Segoe UI Emoji", 42), bg=c["bg"], fg=c["text_muted"]).pack(pady=(20, 6))
            tk.Label(f, text=TEXTS[LANG]["no_collections"], font=FLABEL, bg=c["bg"], fg=c["text_dim"]).pack()
            return

        self.update_idletasks()
        avail = self._main.winfo_width() - 44
        if avail < 50:
            self.after(200, lambda: self._col_scroll_area(parent)); return
        card_w = CAPA_W + 60 + GPAD * 2
        ncols = max(2, avail // card_w)

        def _section(par, title, items):
            tk.Label(par, text=title, font=FBTN, bg=c["bg"], fg=c["text_dim"],
                     anchor="w", padx=4).pack(fill="x", padx=GPAD, pady=(12, 4))
            tk.Frame(par, bg=c["border"], height=1).pack(fill="x", padx=GPAD, pady=(0, 6))
            gf = tk.Frame(par, bg=c["bg"]); gf.pack(padx=GPAD, pady=(0, GPAD), anchor="nw")
            for i, item in enumerate(items):
                row, col = i // ncols, i % ncols
                card = CollectionCard(gf, item, open_cb=self._open,
                                      detail_cb=self._show_collection_detail, root=self)
                card.grid(row=row, column=col, padx=GPAD//2, pady=GPAD//2)
        if show_sub and subfolders: _section(content, f"📁  {TEXTS[LANG]['subfolders']}", subfolders)
        if show_ser and series:     _section(content, f"📚  {TEXTS[LANG]['series']}", series)

    def _set_col_filter(self, key): self._col_filter = key; self._show_collections()
    def _set_col_sort(self, key):   self._col_sort = key; self._show_collections()

    def _show_collection_detail(self, collection):
        c = THEME
        try: self._main.unbind("<Configure>")
        except Exception as _e: log.debug("silenced: %s", _e)
        for w in self._main.winfo_children():
            w.destroy()
        files = sorted(collection["files"], key=natural_key)
        lidas, total, ultima = collection_read_count(files)

        hdr = tk.Frame(self._main, bg=c["bg"]); hdr.pack(fill="x", padx=20, pady=(16, 6))
        make_pill(hdr, f"◀  {TEXTS[LANG]['back_collections']}", self._show_collections,
                  variant="soft", font=FSMALL).pack(side="left", padx=(0, 14))
        cname = collection["name"]
        if files:
            info = get_comic_info(files[0])
            if info.get("series"): cname = info["series"]
        tk.Label(hdr, text=cname, font=FTITLE, bg=c["bg"], fg=c["text"]).pack(side="left")
        n = len(files)
        tk.Label(hdr, text=f"{n} {TEXTS[LANG]['issues']}{'s' if n != 1 else ''}",
                 font=FTINY, bg=c["bg"], fg=c["text_muted"]).pack(side="left", padx=10, pady=(6, 0))
        if ultima:
            make_pill(hdr, f"▶  {TEXTS[LANG]['continue_reading']}",
                      lambda: self._open(ultima, files), variant="accent", font=FSMALL).pack(side="right")

        prog_row = tk.Frame(self._main, bg=c["bg"]); prog_row.pack(fill="x", padx=20, pady=(0, 4))
        if total > 0:
            pct = lidas / total
            bar_w_full, bar_h = 300, 8
            pbar = tk.Canvas(prog_row, width=bar_w_full, height=bar_h, bg=c["bg"], highlightthickness=0)
            pbar.pack(side="left", pady=4)
            r = bar_h // 2
            _rrect(pbar, 0, 0, bar_w_full, bar_h, r, fill=c["progress_bg"])
            filled = int(bar_w_full * pct)
            if filled > r * 2: _rrect(pbar, 0, 0, filled, bar_h, r, fill=c["accent"])
            elif filled > 0: pbar.create_oval(0, 0, bar_h, bar_h, fill=c["accent"], outline="")
            tk.Label(prog_row, text=f"  {lidas}/{total} {TEXTS[LANG]['read']}  ({int(pct*100)}%)",
                     font=FTINY, bg=c["bg"], fg=c["text_dim"]).pack(side="left", padx=6)

        tk.Frame(self._main, bg=c["border"], height=1).pack(fill="x", padx=20, pady=(0, 4))
        sf = tk.Frame(self._main, bg=c["bg"]); sf.pack(fill="both", expand=True)
        cvd = tk.Canvas(sf, bg=c["bg"], highlightthickness=0); cvd.pack(side="left", fill="both", expand=True)
        sb2 = ttk.Scrollbar(sf, orient="vertical", command=cvd.yview); sb2.pack(side="right", fill="y")
        cvd.configure(yscrollcommand=sb2.set)
        content = tk.Frame(cvd, bg=c["bg"])
        wid = cvd.create_window((0, 0), window=content, anchor="nw")
        content.bind("<Configure>", lambda e: cvd.configure(scrollregion=cvd.bbox("all")))
        cvd.bind("<Configure>", lambda e: cvd.itemconfig(wid, width=e.width))
        def _on_wheel(e): cvd.yview_scroll(-int(e.delta / 120), "units")
        cvd.bind("<Enter>", lambda e: cvd.bind_all("<MouseWheel>", _on_wheel))
        cvd.bind("<Leave>", lambda e: cvd.unbind_all("<MouseWheel>"))

        self.update_idletasks()
        avail = self._main.winfo_width() - 44
        card_w = CAPA_W + 24 + GPAD * 2
        ncols = max(2, avail // card_w)
        gf = tk.Frame(content, bg=c["bg"]); gf.pack(padx=GPAD, pady=GPAD, anchor="nw")
        prog = load_progress()
        for i, fpath in enumerate(files):
            row, col = i // ncols, i % ncols
            info = get_comic_info(fpath)
            stem = Path(fpath).stem
            if info.get("number"):
                label = f"#{info['number']}"
                if info.get("title"): label += f" — {info['title']}"
            elif info.get("title"): label = info["title"]
            else: label = stem
            if len(label) > 22: label = label[:20] + "…"
            page = get_progress_page(fpath)
            if page is not None and page > 0: label = f"✓ {label}"
            card = ComicCard(gf, fpath, None,
                             lambda p, fl=files: self._open(p, fl), self, label_override=label)
            card.grid(row=row, column=col, padx=GPAD//2, pady=GPAD//2)
            if self._meta_tooltip:
                tt = self._meta_tooltip
                card.cv.bind("<Enter>", lambda e, p=fpath, w=card.cv: tt.show(w, p), add="+")
                card.cv.bind("<Leave>", lambda e: tt.hide(), add="+")
            if page is not None and page > 0:
                tk.Frame(card.frame, bg=c["read_badge_text"], width=6, height=6).place(
                    relx=0.5, rely=1.0, anchor="s", y=-2)
            def _on_loaded(p, pil, _card=card):
                try: _card.set_image(pil)
                except Exception as _e: log.debug("silenced: %s", _e)
            self._cover_loader.request(fpath, _on_loaded)

    def _toggle_theme(self):
        toggle_theme()
        save_prefs(dark=IS_DARK)
        self._capa_cache.clear()
        if self._search_bubble:
            self._search_query = self._search_bubble.get_text()
            try: self._search_bubble.destroy()
            except Exception: pass
            self._search_bubble = None
        self._build_shell()
        self.after(200, self._refresh_library)


def _rrect(cv, x1, y1, x2, y2, r, fill="", outline="", width=1):
    pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2,
           x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1, x1+r,y1]
    if fill:
        cv.create_polygon(pts, smooth=True, fill=fill, outline="")
    if outline:
        cv.create_polygon(pts, smooth=True, fill="", outline=outline, width=width)


if __name__ == "__main__":
    app = LibraryWindow()
    app.mainloop()
