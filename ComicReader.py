#!/usr/bin/env python3
"""
╔══════════════════════════════════════╗
║         PANEL — CBZ/CBR Reader       ║
║   Zoom · Drag · Page Nav · Themes    ║
╚══════════════════════════════════════╝
Requires: pip install pillow
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import zipfile
import rarfile

rarfile.UNRAR_TOOL = r"C:\Program Files\WinRAR\UnRAR.exe"

import os
import sys
import io
import math
import json
import shutil
from pathlib import Path

try:
    from PIL import Image, ImageTk, ImageFilter, ImageEnhance
except ImportError:
    print("Pillow não encontrado. Instalando...")
    os.system(f"{sys.executable} -m pip install pillow")
    from PIL import Image, ImageTk, ImageFilter, ImageEnhance


LANG = "en"

TEXTS = {
    "en": {
        "open": "Open File",
        "library": "Library",
        "theme": "Theme",
        "fit": "⊞ Fit",
        "fullscreen": "⛶ Fullscreen",
        "language": "Choose Language",
        "choose_library_folder": "Choose Library Folder",
        "rename": "Rename",
        "delete": "Delete",
        "new_name": "New name:",
        "confirm_delete": "Are you sure you want to delete this file?",
        "error": "Error",
        "success": "Success",
        "file_renamed": "File renamed successfully.",
        "file_deleted": "File deleted successfully."
    },

    "pt": {
        "open": "Abrir Arquivo",
        "library": "Biblioteca",
        "theme": "Tema",
        "fit": "⊞ Encaixar",
        "fullscreen": "⛶ Tela Cheia",
        "language": "Escolha o Idioma",
        "choose_library_folder": "Escolher Pasta da Biblioteca",
        "rename": "Renomear",
        "delete": "Excluir",
        "new_name": "Novo nome:",
        "confirm_delete": "Tem certeza que deseja excluir este arquivo?",
        "error": "Erro",
        "success": "Sucesso",
        "file_renamed": "Arquivo renomeado com sucesso.",
        "file_deleted": "Arquivo excluído com sucesso."
    }
}

# ── Paleta de cores ──────────────────────────────────────────────────────────

DARK_THEME = {
    "bg": "#0f0f13",
    "surface": "#1a1a24",
    "border": "#2a2a3a",
    "accent": "#e85d3a",
    "accent2": "#f5a623",
    "text": "#e8e4dc",
    "text_dim": "#7a7590",
    "canvas_bg": "#080810",
    "btn_hover": "#2e2e42",
}

LIGHT_THEME = {
    "bg": "#f2f2f2",
    "surface": "#ffffff",
    "border": "#cccccc",
    "accent": "#e85d3a",
    "accent2": "#f5a623",
    "text": "#111111",
    "text_dim": "#666666",
    "canvas_bg": "#e8e8e8",
    "btn_hover": "#dddddd",
}

THEME = DARK_THEME.copy()

# Arquivo para salvar caminho da biblioteca
LIBRARY_CONFIG_FILE = "library_config.json"
LIBRARY_FOLDER = "Comic Books"  # padrão inicial
PROGRESS_FILE = "reading_progress.json"
FONT_TITLE  = ("Roboto", 24, "bold")
FONT_LABEL  = ("Roboto", 11)
FONT_BTN    = ("Roboto", 11, "bold")
FONT_SMALL  = ("Roboto", 9)
FONT_PAGE   = ("Roboto", 10, "bold")


# ── Utilitários ──────────────────────────────────────────────────────────────
def extract_cbz(path: str) -> list[bytes]:
    """Extrai imagens de arquivos CBZ (ZIP) ou CBR (RAR)."""
    images = []
    exts = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}

    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path, "r") as archive:
            names = sorted(
                [n for n in archive.namelist()
                 if Path(n).suffix.lower() in exts
                 and not Path(n).name.startswith(".")]
            )
            for name in names:
                images.append(archive.read(name))
        return images

    if rarfile.is_rarfile(path):
        with rarfile.RarFile(path, "r") as archive:
            names = sorted(
                [n for n in archive.namelist()
                 if Path(n).suffix.lower() in exts
                 and not Path(n).name.startswith(".")]
            )
            for name in names:
                images.append(archive.read(name))
        return images

    raise ValueError("Arquivo não é um CBZ (ZIP) nem um CBR (RAR) válido.")


def pil_from_bytes(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGBA")


# ── Tela de boas-vindas ──────────────────────────────────────────────────────
class WelcomeScreen(tk.Toplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.callback = callback
        self.title("PANEL — Bem-vindo")
        try:
            self.iconbitmap("panel.ico")
        except Exception:
            pass  # ignora se o arquivo não existir
        self.configure(bg=THEME["bg"])
        self.resizable(False, False)

        W, H = 520, 420
        self.geometry(f"{W}x{H}+{(self.winfo_screenwidth()-W)//2}+{(self.winfo_screenheight()-H)//2}")
        self.grab_set()
        self._build()

    def _build(self):
        c = THEME

        # Header decorativo
        header = tk.Canvas(self, width=520, height=90,
                           bg=c["bg"], highlightthickness=0)
        header.pack()
        header.create_rectangle(0, 0, 520, 90, fill=c["surface"], outline="")
        header.create_line(0, 89, 520, 89, fill=c["border"])
        # Linhas decorativas
        for i, col in enumerate([c["accent"], c["accent2"], c["border"]]):
            header.create_line(0, 4+i*3, 520, 4+i*3, fill=col, width=1+(i==0))

        header.create_text(260, 48, text="◈ PANEL ◈",
                           font=("Georgia", 28, "bold"),
                           fill=c["text"])
        header.create_text(260, 76, text="comic reader",
                           font=FONT_SMALL, fill=c["text_dim"])

        # Subtítulo
        tk.Label(self, text="Escolha seu modo de leitura",
                 font=("Georgia", 13), bg=c["bg"],
                 fg=c["text_dim"]).pack(pady=(22, 6))

        # Cards de modo
        frame = tk.Frame(self, bg=c["bg"])
        frame.pack(padx=30, fill="x")

        self._mode = tk.StringVar(value="pc")

        for mode, icon, label, desc in [
            ("pc",    "⬛", "Desktop",
             "Janela larga · atalhos de teclado\nseta ← → para navegar"),
            ("phone", "▯",  "Mobile / Tablet",
             "Interface compacta · botões grandes\nideal para toque"),
        ]:
            card = tk.Frame(frame, bg=c["surface"],
                            relief="flat", bd=0,
                            highlightbackground=c["border"],
                            highlightthickness=1,
                            cursor="hand2")
            card.pack(side="left", expand=True, fill="both",
                      padx=8, pady=8, ipady=10, ipadx=8)

            rb = tk.Radiobutton(card, variable=self._mode, value=mode,
                                bg=c["surface"], activebackground=c["surface"],
                                selectcolor=c["accent"],
                                fg=c["text"], activeforeground=c["text"])
            rb.pack(side="left", padx=(8, 0))

            inner = tk.Frame(card, bg=c["surface"])
            inner.pack(side="left", padx=6)
            tk.Label(inner, text=f"{icon}  {label}",
                     font=("Georgia", 13, "bold"),
                     bg=c["surface"], fg=c["text"]).pack(anchor="w")
            tk.Label(inner, text=desc,
                     font=FONT_SMALL, bg=c["surface"],
                     fg=c["text_dim"], justify="left").pack(anchor="w")

            card.bind("<Button-1>", lambda e, m=mode: self._mode.set(m))
            for ch in card.winfo_children() + inner.winfo_children():
                ch.bind("<Button-1>", lambda e, m=mode: self._mode.set(m))

        # Separador
        sep = tk.Canvas(self, height=1, bg=c["bg"], highlightthickness=0)
        sep.pack(fill="x", padx=30, pady=(10, 0))
        sep.create_line(0, 0, 520, 0, fill=c["border"])

        # Botões
        btn_frame = tk.Frame(self, bg=c["bg"])
        btn_frame.pack(pady=18)

        self._open_btn = self._make_btn(
            btn_frame, "  ◈ Abrir Comic Book  ",
            self._open_file, primary=True)
        self._open_btn.pack(side="left", padx=8)

        self._make_btn(btn_frame, "  Cancelar  ",
                       self.destroy, primary=False).pack(side="left", padx=8)

        # Dica de atalhos
        tk.Label(self,
                 text="⌨  ← → para navegar  ·  +/- zoom  ·  F para tela cheia",
                 font=FONT_SMALL, bg=c["bg"], fg=c["text_dim"]).pack(pady=(0, 14))

    def _make_btn(self, parent, text, cmd, primary=True):
        bg = THEME["accent"] if primary else THEME["surface"]
        fg = "#fff" if primary else THEME["text_dim"]
        b = tk.Label(parent, text=text, font=FONT_BTN,
                     bg=bg, fg=fg, cursor="hand2",
                     padx=12, pady=8,
                     relief="flat",
                     highlightbackground=THEME["border"],
                     highlightthickness=1)
        b.bind("<Button-1>", lambda e: cmd())
        if not primary:
            b.bind("<Enter>",
                   lambda e: b.config(bg=THEME["btn_hover"], fg=THEME["text"]))
            b.bind("<Leave>",
                   lambda e: b.config(bg=THEME["surface"], fg=THEME["text_dim"]))
        else:
            b.bind("<Enter>", lambda e: b.config(bg="#c94a2e"))
            b.bind("<Leave>", lambda e: b.config(bg=THEME["accent"]))
        return b

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Selecionar arquivo",
            filetypes=[("Comic Books", "*.cbz *.cbr *.zip *.rar"), ("Todos", "*.*")]
        )
        if path:
            self.destroy()
            self.callback(path, self._mode.get())


# ── Viewer principal ─────────────────────────────────────────────────────────
class ComicViewer(tk.Tk):
    ZOOM_STEP   = 0.15
    ZOOM_MIN    = 0.1
    ZOOM_MAX    = 5.0
    ZOOM_FIT_PC = 0.95   # fracção da janela usada no fit
    ZOOM_FIT_PH = 0.92

    def __init__(self):
        super().__init__()

        self.icons = {}

        ICON_SIZE = 16  # muda esse valor para o tamanho que quiser

        # Define caminho base
        if getattr(sys, 'frozen', False):
            self.base_path = sys._MEIPASS
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))

        for name in ["open", "library", "theme", "prev", "next", "zoom_in", "zoom_out"]:
            try:
                img = Image.open(os.path.join(self.base_path, "Icons", f"{name}.png")).resize(
                    (ICON_SIZE, ICON_SIZE), Image.LANCZOS
                )
                self.icons[name] = ImageTk.PhotoImage(img)
            except:
                self.icons[name] = None

        self._manga_mode = False
        self._dark_mode = True

        
        self.withdraw()          # esconde até estar pronto
        self.title("PANEL — Comic Reader")
        try:
            self.iconbitmap("panel.ico")
        except Exception:
            pass  # ignora se o arquivo não existir
        self.configure(bg=THEME["bg"])

        # estado
        self._pages:    list[bytes]      = []
        self._page_idx: int              = 0
        self._zoom:     float            = 1.0
        self._fit_zoom: float            = 1.0
        self._drag_start: tuple | None   = None
        self._offset    = [0, 0]
        self._tk_img: ImageTk.PhotoImage | None = None
        self._mode      = "pc"
        self._fullscreen = False
        self._file_path  = ""

        # cache de páginas renderizadas (zoom 1x PIL)
        self._cache: dict[int, Image.Image] = {}

        # Carrega configuração da biblioteca
        self._load_library_config()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Abre welcome
        self._choose_language()
        self._welcome()

    def _choose_language(self):
        win = tk.Toplevel(self)

        win.title("Language / Idioma")
        win.geometry("300x180")
        win.resizable(False, False)
        try:
            win.iconbitmap("panel.ico")
        except:
            pass

        tk.Label(
            win,
            text="Choose Language / Escolha o Idioma",
            font=FONT_LABEL
        ).pack(pady=15)

        def set_lang(lang):
            global LANG
            LANG = lang
            win.destroy()

        tk.Button(
            win,
            text="🇧🇷 Português",
            command=lambda: set_lang("pt")
        ).pack(fill="x", padx=20, pady=5)

        tk.Button(
            win,
            text="🇺🇸 English",
            command=lambda: set_lang("en")
        ).pack(fill="x", padx=20, pady=5)

        win.grab_set()
        win.wait_window()

    def _load_library_config(self):
        """Carrega caminho da biblioteca salvo, se existir"""
        global LIBRARY_FOLDER
        try:
            with open(LIBRARY_CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                if "library_folder" in config and os.path.isdir(config["library_folder"]):
                    LIBRARY_FOLDER = config["library_folder"]
        except:
            pass

    def _save_library_config(self, path):
        """Salva caminho da biblioteca"""
        global LIBRARY_FOLDER
        LIBRARY_FOLDER = path
        try:
            with open(LIBRARY_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"library_folder": path}, f, indent=4)
        except Exception as e:
            print("Erro ao salvar configuração da biblioteca:", e)

    def _choose_library_folder(self):
        """Abre janela para escolher pasta da biblioteca"""
        path = filedialog.askdirectory(
            title=TEXTS[LANG]["choose_library_folder"],
            initialdir=LIBRARY_FOLDER
        )
        if path:
            self._save_library_config(path)
        return path

    def _toggle_theme(self):
        global THEME

        self._dark_mode = not self._dark_mode

        if self._dark_mode:
            THEME = DARK_THEME.copy()
        else:
            THEME = LIGHT_THEME.copy()

        self._build_ui()
        self._show_page(reset_offset=False)

    def _toggle_manga_mode(self):
        self._manga_mode = not self._manga_mode

        estado = "ON" if self._manga_mode else "OFF"

        self.title(
            f"PANEL · {'MANGA' if self._manga_mode else 'NORMAL'} · {estado}"
        )
    
    def _load_progress(self):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def _save_progress(self):
        try:
            progress = self._load_progress()
            progress[self._file_path] = self._page_idx

            with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                json.dump(progress, f, indent=4)
        except Exception as e:
            print("Erro ao salvar progresso:", e)

    def _restore_progress(self):
        try:
            progress = self._load_progress()

            if self._file_path in progress:
                page = progress[self._file_path]

                if 0 <= page < len(self._pages):
                    self._page_idx = page
        except Exception as e:
            print("Erro ao restaurar progresso:", e)

    def _on_close(self):
        self._save_progress()
        self.destroy()

    def _scan_library(self):
        exts = (".cbz", ".cbr", ".zip", ".rar")

        if not os.path.exists(LIBRARY_FOLDER):
            os.makedirs(LIBRARY_FOLDER)

        return sorted([
            os.path.join(LIBRARY_FOLDER, f)
            for f in os.listdir(LIBRARY_FOLDER)
            if f.lower().endswith(exts)
        ])

    def _open_library(self):
        win = tk.Toplevel(self)
        win.title(TEXTS[LANG]["library"])
        win.geometry("500x600")
        win.configure(bg=THEME["bg"])

        # ✅ ÍCONE DA JANELA DA BIBLIOTECA (agora funcionando)
        try:
            caminho_png = os.path.join(self.base_path, "Icons", "library.png")
            img_icone = Image.open(caminho_png)
            img_icone = img_icone.resize((32, 32), Image.LANCZOS)
            icone_tk = ImageTk.PhotoImage(img_icone)
            win.tk.call('wm', 'iconphoto', win._w, icone_tk)
            win._icone_guardado = icone_tk # guarda pra não sumir
        except Exception as e:
            print("Não conseguiu carregar ícone da biblioteca:", e)

        win.resizable(True, True)

        # Botão para escolher pasta
        top_frame = tk.Frame(win, bg=THEME["bg"])
        top_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(
            top_frame,
            text=TEXTS[LANG]["choose_library_folder"],
            command=lambda: self._atualizar_biblioteca(win)
        ).pack(side="left")

        # Lista de arquivos
        lista = tk.Listbox(
            win,
            bg=THEME["surface"],
            fg=THEME["text"],
            font=("Courier New", 11),
            selectbackground=THEME["accent"],
            selectforeground="#ffffff"
        )
        lista.pack(fill="both", expand=True, padx=10, pady=(0,10))

        arquivos = self._scan_library()
        for arq in arquivos:
            lista.insert("end", Path(arq).stem)

        # Função abrir
        def abrir(event=None):
            sel = lista.curselection()
            if not sel: return
            path = arquivos[sel[0]]
            try:
                pages = extract_cbz(path)
            except Exception as e:
                messagebox.showerror(TEXTS[LANG]["error"], f"{e}")
                return
            if not pages:
                messagebox.showerror(TEXTS[LANG]["error"], "Nenhuma imagem encontrada.")
                return
            self._pages = pages
            self._page_idx = 0
            self._cache = {}
            self._file_path = path
            self._restore_progress()
            self._show_page()
            win.destroy()

        lista.bind("<Double-Button-1>", abrir)

        # Menu de contexto (clique com o botão direito)
        menu = tk.Menu(win, tearoff=0, bg=THEME["surface"], fg=THEME["text"], activebackground=THEME["accent"])
        menu.add_command(label=TEXTS[LANG]["rename"], command=lambda: self._renomear_arquivo(lista, arquivos, win))
        menu.add_command(label=TEXTS[LANG]["delete"], command=lambda: self._excluir_arquivo(lista, arquivos, win))

        def show_menu(e):
            try:
                menu.tk_popup(e.x_root, e.y_root)
            finally:
                menu.grab_release()

        lista.bind("<Button-3>", show_menu)

    def _atualizar_biblioteca(self, janela_pai):
        """Atualiza lista da biblioteca após escolher nova pasta"""
        novo_caminho = self._choose_library_folder()
        if novo_caminho:
            janela_pai.destroy()
            self._open_library()

    def _renomear_arquivo(self, lista, arquivos, janela):
        sel = lista.curselection()
        if not sel: return
        idx = sel[0]
        caminho_antigo = arquivos[idx]
        extensao = Path(caminho_antigo).suffix
        nome_atual = Path(caminho_antigo).stem

        novo_nome = simpledialog.askstring(
            TEXTS[LANG]["rename"],
            TEXTS[LANG]["new_name"],
            initialvalue=nome_atual,
            parent=janela
        )
        if not novo_nome or novo_nome.strip() == "":
            return

        caminho_novo = os.path.join(LIBRARY_FOLDER, novo_nome.strip() + extensao)

        try:
            os.rename(caminho_antigo, caminho_novo)
            messagebox.showinfo(TEXTS[LANG]["success"], TEXTS[LANG]["file_renamed"])
            janela.destroy()
            self._open_library()  # recarrega
        except Exception as e:
            messagebox.showerror(TEXTS[LANG]["error"], f"{e}")

    def _excluir_arquivo(self, lista, arquivos, janela):
        sel = lista.curselection()
        if not sel: return
        idx = sel[0]
        caminho = arquivos[idx]

        if messagebox.askyesno(TEXTS[LANG]["delete"], TEXTS[LANG]["confirm_delete"]):
            try:
                os.remove(caminho)
                messagebox.showinfo(TEXTS[LANG]["success"], TEXTS[LANG]["file_deleted"])
                janela.destroy()
                self._open_library()
            except Exception as e:
                messagebox.showerror(TEXTS[LANG]["error"], f"{e}")

    # ── Bootstrap ────────────────────────────────────────────────────────────
    def _welcome(self):
        WelcomeScreen(self, self._start)

    def _start(self, path: str, mode: str):
        self._mode      = mode
        self._file_path = path

        try:
            pages = extract_cbz(path)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo:\n{e}")
            self._welcome()
            return

        if not pages:
            messagebox.showerror("Erro", "Nenhuma imagem encontrada no arquivo.")
            self._welcome()
            return

        self._pages    = pages
        self._page_idx = 0
        self._cache    = {}
        self._offset   = [0, 0]

        self._restore_progress()

        self._apply_mode(mode)
        self._build_ui()
        self._deiconify()
        self._show_page()

    def _apply_mode(self, mode: str):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        if mode == "pc":
            w, h = min(1280, sw - 60), min(860, sh - 60)
        else:
            w, h = min(480, sw - 20), min(820, sh - 20)
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.minsize(320, 400)

    def _deiconify(self):
        self.update_idletasks()
        self.deiconify()

    # ── UI ───────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # limpa se estava aberto
        for w in self.winfo_children():
            w.destroy()

        c = THEME
        ph = self._mode == "phone"

        # ── Topbar ──
        topbar = tk.Frame(self, bg=c["surface"], height=48)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        # Linha de acento no topo
        accent_line = tk.Canvas(topbar, height=3,
                                bg=c["surface"], highlightthickness=0)
        accent_line.pack(fill="x", side="top")
        accent_line.create_line(0, 0, 2000, 0, fill=c["accent"], width=3)

        inner_top = tk.Frame(topbar, bg=c["surface"])
        inner_top.pack(fill="both", expand=True, padx=10)

        # Logo
        logo = tk.Label(inner_top, text="◈ PANEL",
                        font=("Georgia", 14, "bold") if not ph else ("Georgia", 11, "bold"),
                        bg=c["surface"], fg=c["text"],
                        cursor="hand2")
        logo.pack(side="left", padx=(4, 16))
        logo.bind("<Button-1>", lambda e: self._open_new())

        # Nome do arquivo
        fname = Path(self._file_path).stem
        if len(fname) > (22 if ph else 40):
            fname = fname[:19] + "..."
        tk.Label(inner_top, text=fname,
                 font=FONT_SMALL, bg=c["surface"],
                 fg=c["text_dim"]).pack(side="left")

        # Botões do topo (direita)
        btn_area = tk.Frame(inner_top, bg=c["surface"])
        btn_area.pack(side="right")

        if not ph:
            self._tb_btn(btn_area, TEXTS[LANG]["fullscreen"], self._toggle_fullscreen)
            self._tb_btn(btn_area, TEXTS[LANG]["fit"],   self._fit_page)
            self._tb_btn(btn_area, TEXTS[LANG]["library"], self._open_library, self.icons["library"])
            self._tb_btn(btn_area, TEXTS[LANG]["theme"], self._toggle_theme, self.icons["theme"])
            self._tb_btn(btn_area, TEXTS[LANG]["open"], self._open_new, self.icons["open"])

        # ── Canvas central ──
        self._canvas = tk.Canvas(
            self,
            bg=c["canvas_bg"],
            highlightthickness=0,
            cursor="crosshair"
        )
        self._canvas.pack(fill="both", expand=True)

        # ── Barra inferior ──
        self._bottombar = tk.Frame(self, bg=c["surface"], height=52 if not ph else 64)
        self._bottombar.pack(fill="x", side="bottom")
        self._bottombar.pack_propagate(False)

        # Linha de acento em baixo
        bl = tk.Canvas(self._bottombar, height=2,
                       bg=c["surface"], highlightthickness=0)
        bl.pack(fill="x", side="bottom")
        bl.create_line(0, 0, 2000, 0, fill=c["border"], width=1)

        inner_bot = tk.Frame(self._bottombar, bg=c["surface"])
        inner_bot.pack(fill="both", expand=True, padx=6)

        sz = 16 if ph else 14
        nav_font = ("Courier New", sz, "bold")

        # Botão anterior
        prev_btn = self._nav_btn(inner_bot, "◀", self._prev_page, nav_font)
        prev_btn.pack(side="left", padx=(4, 2))

        # Indicador de página
        self._page_label = tk.Label(
            inner_bot, text="",
            font=FONT_PAGE if not ph else ("Courier New", 16, "bold"),
            bg=c["surface"], fg=c["text"],
            width=10 if not ph else 8
        )
        self._page_label.pack(side="left", padx=6)

        # Botão próximo
        next_btn = self._nav_btn(inner_bot, "▶", self._next_page, nav_font)
        next_btn.pack(side="left", padx=(2, 12))

        # Controles de zoom
        zoom_frame = tk.Frame(inner_bot, bg=c["surface"])
        zoom_frame.pack(side="left", padx=4)

        self._zoom_label = tk.Label(
            zoom_frame, text="100%",
            font=FONT_SMALL, bg=c["surface"], fg=c["text_dim"],
            width=5
        )
        self._zoom_label.pack(side="left")

        self._nav_btn(zoom_frame, "−", self._zoom_out,
                      ("Courier New", 13, "bold")).pack(side="left", padx=2)
        self._nav_btn(zoom_frame, "+", self._zoom_in,
                      ("Courier New", 13, "bold")).pack(side="left", padx=2)
        self._nav_btn(zoom_frame, "⊠", self._fit_page,
                      ("Courier New", 11, "bold")).pack(side="left", padx=2)

        # Slider de zoom
        if not ph:
            self._zoom_var = tk.DoubleVar(value=1.0)
            slider = tk.Scale(
                inner_bot,
                from_=self.ZOOM_MIN, to=self.ZOOM_MAX,
                resolution=0.05,
                orient="horizontal",
                variable=self._zoom_var,
                command=self._slider_zoom,
                bg=c["surface"], fg=c["text_dim"],
                troughcolor=c["border"],
                activebackground=c["accent"],
                highlightthickness=0,
                sliderrelief="flat",
                length=140,
                showvalue=False,
                bd=0
            )
            slider.pack(side="left", padx=(8, 4))
            self._slider = slider
        else:
            self._slider = None

        # Barra de progresso de páginas
        self._progress = tk.Canvas(self._bottombar, height=3,
                                   bg=c["border"], highlightthickness=0)
        self._progress.pack(fill="x", side="top")

        # ── Binds ──
        self._canvas.bind("<ButtonPress-1>",   self._on_drag_start)
        self._canvas.bind("<B1-Motion>",        self._on_drag)
        self._canvas.bind("<ButtonRelease-1>",  self._on_drag_end)
        self._canvas.bind("<MouseWheel>",       self._on_mousewheel)
        self._canvas.bind("<Button-4>",         self._on_scroll_up)
        self._canvas.bind("<Button-5>",         self._on_scroll_down)
        self._canvas.bind("<Configure>",        self._on_resize)

        self.bind("<t>", lambda e: self._toggle_theme())
        self.bind("<T>", lambda e: self._toggle_theme())
        self.bind("<m>", lambda e: self._toggle_manga_mode())
        self.bind("<M>", lambda e: self._toggle_manga_mode())
        self.bind("<Left>",  lambda e: self._prev_page())
        self.bind("<Right>", lambda e: self._next_page())
        self.bind("<Prior>", lambda e: self._prev_page())   # Page Up
        self.bind("<Next>",  lambda e: self._next_page())   # Page Down
        self.bind("<equal>", lambda e: self._zoom_in())
        self.bind("<minus>", lambda e: self._zoom_out())
        self.bind("<f>",     lambda e: self._toggle_fullscreen())
        self.bind("<F11>",   lambda e: self._toggle_fullscreen())
        self.bind("<Escape>",lambda e: self._exit_fullscreen())
        self.bind("<Home>",  lambda e: self._goto_page(0))
        self.bind("<End>",   lambda e: self._goto_page(len(self._pages)-1))

        # Gesto de swipe (mobile)
        self._swipe_x = None
        self._canvas.bind("<ButtonPress-3>",  self._on_swipe_start)
        self._canvas.bind("<B3-Motion>",      self._on_swipe_move)
        self._canvas.bind("<ButtonRelease-3>",self._on_swipe_end)

    def _tb_btn(self, parent, text, cmd, icon=None):
        b = tk.Label(parent, text=text, font=FONT_SMALL,
                    bg=THEME["surface"], fg=THEME["text_dim"],
                    cursor="hand2", padx=8, pady=6,
                    image=icon, compound="left" if icon else "none")
        b.pack(side="right")
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.config(bg=THEME["btn_hover"],
                                          fg=THEME["text"]))
        b.bind("<Leave>", lambda e: b.config(bg=THEME["surface"],
                                          fg=THEME["text_dim"]))
        return b

    def _nav_btn(self, parent, text, cmd, font=None):
        f = font or FONT_BTN
        b = tk.Label(parent, text=text, font=f,
                     bg=THEME["surface"], fg=THEME["text"],
                     cursor="hand2", padx=10, pady=4,
                     relief="flat",
                     highlightbackground=THEME["border"],
                     highlightthickness=1)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.config(bg=THEME["accent"],
                                              fg="#fff"))
        b.bind("<Leave>", lambda e: b.config(bg=THEME["surface"],
                                              fg=THEME["text"]))
        return b

    # ── Renderização ─────────────────────────────────────────────────────────
    def _get_pil(self, idx: int) -> Image.Image:
        if idx not in self._cache:
            self._cache[idx] = pil_from_bytes(self._pages[idx])
            # limita cache a 5 páginas
            if len(self._cache) > 5:
                old = next(iter(self._cache))
                del self._cache[old]
        return self._cache[idx]

    def _show_page(self, reset_offset: bool = True):
        if not self._pages:
            return

        cw = self._canvas.winfo_width()  or 800
        ch = self._canvas.winfo_height() or 600

        img = self._get_pil(self._page_idx)
        iw, ih = img.size

        # Calcula fit zoom ao abrir / trocar página
        if reset_offset:
            factor = self.ZOOM_FIT_PC if self._mode == "pc" else self.ZOOM_FIT_PH
            self._fit_zoom = min(cw / iw, ch / ih) * factor
            self._zoom     = self._fit_zoom
            self._offset   = [0, 0]
            if self._slider:
                self._zoom_var.set(self._zoom)

        # Redimensiona
        nw = max(1, int(iw * self._zoom))
        nh = max(1, int(ih * self._zoom))
        resized = img.resize((nw, nh), Image.LANCZOS)

        # Converte para RGB (canvas não aceita RGBA direto no bg escuro)
        if self._dark_mode:
            bg_color = (8, 8, 16)
        else:
            bg_color = (240, 240, 240)

        bg_img = Image.new("RGB", (nw, nh), bg_color)
        if resized.mode == "RGBA":
            bg_img.paste(resized, mask=resized.split()[3])
        else:
            bg_img = resized.convert("RGB")

        self._tk_img = ImageTk.PhotoImage(bg_img)

        # Posição centrada + offset de drag
        x = cw // 2 + self._offset[0]
        y = ch // 2 + self._offset[1]

        self._canvas.delete("all")
        self._canvas.create_image(x, y, anchor="center",
                                  image=self._tk_img)

        # ✅ CORREÇÃO: cor sem transparência
        self._canvas.create_rectangle(
            x - nw//2 + 4, y - nh//2 + 4,
            x + nw//2 + 4, y + nh//2 + 4,
            fill="", outline="#222222", width=1
        )

        self._update_hud()

    def _update_hud(self):
        n   = len(self._pages)
        idx = self._page_idx

        self._page_label.config(
            text=f"{idx+1}/{n} {'🇯🇵' if self._manga_mode else ''}"
        )
        self._zoom_label.config(
            text=f"{self._zoom*100:.0f}%"
        )

        # Barra de progresso
        self.update_idletasks()
        pw = self._progress.winfo_width() or 300
        filled = int(pw * (idx + 1) / n)
        self._progress.delete("all")
        self._progress.create_rectangle(0, 0, filled, 3,
                                         fill=THEME["accent"], outline="")

        # Título da janela
        fname = Path(self._file_path).stem
        self.title(f"PANEL  ·  {fname}  [{idx+1}/{n}]")

    # ── Navegação ────────────────────────────────────────────────────────────
    def _goto_page(self, idx: int, reset: bool = True):
        idx = max(0, min(idx, len(self._pages) - 1))
        if idx != self._page_idx:
            self._page_idx = idx
            self._save_progress()
            self._show_page(reset_offset=reset)

    def _next_page(self):
        if self._manga_mode:
            self._goto_page(self._page_idx - 1)
        else:
            self._goto_page(self._page_idx + 1)

    def _prev_page(self):
        if self._manga_mode:
            self._goto_page(self._page_idx + 1)
        else:
            self._goto_page(self._page_idx - 1)

    # ── Zoom ─────────────────────────────────────────────────────────────────
    def _set_zoom(self, z: float, reset_offset: bool = False):
        self._zoom = max(self.ZOOM_MIN, min(self.ZOOM_MAX, z))
        if reset_offset:
            self._offset = [0, 0]
        if self._slider:
            self._zoom_var.set(self._zoom)
        self._show_page(reset_offset=False)

    def _zoom_in(self):
        self._set_zoom(self._zoom + self.ZOOM_STEP)

    def _zoom_out(self):
        self._set_zoom(self._zoom - self.ZOOM_STEP)

    def _fit_page(self):
        self._set_zoom(self._fit_zoom, reset_offset=True)

    def _slider_zoom(self, val):
        self._set_zoom(float(val))

    # ── Drag ─────────────────────────────────────────────────────────────────
    def _on_drag_start(self, event):
        self._drag_start = (event.x, event.y)
        self._canvas.config(cursor="fleur")

    def _on_drag(self, event):
        if self._drag_start:
            dx = event.x - self._drag_start[0]
            dy = event.y - self._drag_start[1]
            self._offset[0] += dx
            self._offset[1] += dy
            self._drag_start = (event.x, event.y)
            self._show_page(reset_offset=False)

    def _on_drag_end(self, event):
        self._drag_start = None
        self._canvas.config(cursor="crosshair")

    # ── Scroll / Zoom com roda ────────────────────────────────────────────────
    def _on_mousewheel(self, event):
        if event.state & 0x4:  # Ctrl pressionado → zoom
            delta = event.delta / 120 if event.delta else 0
            self._set_zoom(self._zoom + delta * self.ZOOM_STEP)
        else:
            # Scroll sem Ctrl → navega páginas
            delta = event.delta / 120 if event.delta else 0
            if delta < 0:
                self._next_page()
            else:
                self._prev_page()

    def _on_scroll_up(self, event):   # Linux button-4
        if event.state & 0x4:
            self._zoom_in()
        else:
            self._prev_page()

    def _on_scroll_down(self, event): # Linux button-5
        if event.state & 0x4:
            self._zoom_out()
        else:
            self._next_page()

    # ── Swipe (botão direito como gesto) ─────────────────────────────────────
    def _on_swipe_start(self, event):
        self._swipe_x = event.x

    def _on_swipe_move(self, event):
        pass

    def _on_swipe_end(self, event):
        if self._swipe_x is not None:
            dx = event.x - self._swipe_x
            if abs(dx) > 50:
                if dx < 0:
                    self._next_page()
                else:
                    self._prev_page()
        self._swipe_x = None

    # ── Resize ───────────────────────────────────────────────────────────────
    def _on_resize(self, event):
        self.after(50, lambda: self._show_page(reset_offset=False))

    # ── Tela cheia ───────────────────────────────────────────────────────────
    def _toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        self.attributes("-fullscreen", self._fullscreen)

    def _exit_fullscreen(self):
        if self._fullscreen:
            self._fullscreen = False
            self.attributes("-fullscreen", False)

    # ── Abrir novo arquivo ────────────────────────────────────────────────────
    def _open_new(self):
        path = filedialog.askopenfilename(
            title="Selecionar arquivo",
            filetypes=[("Comic Books", "*.cbz *.cbr *.zip *.rar"), ("Todos", "*.*")]
        )
        if path:
            try:
                pages = extract_cbz(path)
            except Exception as e:
                messagebox.showerror("Erro", f"{e}")
                return
            if not pages:
                messagebox.showerror("Erro", "Nenhuma imagem encontrada.")
                return
            self._pages     = pages
            self._page_idx  = 0
            self._cache     = {}
            self._file_path = path
            self._show_page()


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = ComicViewer()
    app.mainloop()