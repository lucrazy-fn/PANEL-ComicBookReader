"""Leitura de CBZ, CBR e PDF e cache de páginas em memória."""
from __future__ import annotations
import io, os, re, threading, zipfile
from pathlib import Path
from PIL import Image, ImageDraw
try:
    import rarfile
except ImportError: rarfile=None
try:
    try: import pymupdf as fitz
    except ImportError: import fitz
except ImportError: fitz=None

IMG_EXTS={".jpg",".jpeg",".png",".webp",".gif",".bmp"}
def natural_key(value): return [int(x) if x.isdigit() else x.lower() for x in re.split(r'(\d+)',str(value))]
class ArchiveBackend:
    def __init__(self,path): self.path=path; self.kind=None; self.names=[]; self._pdf_doc=None; self._detect()
    def _detect(self):
        suffix=Path(self.path).suffix.lower()
        if zipfile.is_zipfile(self.path):
            self.kind="zip"
            with zipfile.ZipFile(self.path) as source: self.names=sorted([n for n in source.namelist() if Path(n).suffix.lower() in IMG_EXTS and not Path(n).name.startswith('.')],key=natural_key)
        elif rarfile and rarfile.is_rarfile(self.path):
            self.kind="rar"
            with rarfile.RarFile(self.path) as source: self.names=sorted([n for n in source.namelist() if Path(n).suffix.lower() in IMG_EXTS and not Path(n).name.startswith('.')],key=natural_key)
        elif fitz and suffix==".pdf": self.kind="pdf"; self._pdf_doc=fitz.open(self.path); self.names=[f"page_{i}" for i in range(self._pdf_doc.page_count)]
        else: raise ValueError(f"Formato não suportado: {suffix}")
    @property
    def count(self): return len(self.names)
    def read_page(self,index):
        if not 0<=index<self.count: raise IndexError(index)
        if self.kind=="zip":
            with zipfile.ZipFile(self.path) as source:return source.read(self.names[index])
        if self.kind=="rar":
            with rarfile.RarFile(self.path) as source:return source.read(self.names[index])
        page=self._pdf_doc.load_page(index); return page.get_pixmap(matrix=fitz.Matrix(2,2)).tobytes("png")
    def close(self):
        if self._pdf_doc: self._pdf_doc.close(); self._pdf_doc=None
def extract_cover_only(path):
    backend=ArchiveBackend(path)
    try:return backend.read_page(0)
    finally:backend.close()
def pil_from_bytes(data): return Image.open(io.BytesIO(data)).convert("RGBA")
def rounded_image(image,radius):
    mask=Image.new("L",image.size,0); ImageDraw.Draw(mask).rounded_rectangle([0,0,image.width-1,image.height-1],radius=radius,fill=255)
    out=Image.new("RGBA",image.size); out.paste(image.convert("RGBA"),mask=mask); return out
class SmartPageLoader:
    WINDOW=4
    def __init__(self,path): self.backend=ArchiveBackend(path); self._cache={}; self._lock=threading.Lock(); self._prefetching=set()
    @property
    def count(self):return self.backend.count
    @property
    def names(self):return self.backend.names
    @property
    def entries(self):return self.backend.names
    def get_pil(self,index):
        with self._lock:
            if index in self._cache:return self._cache[index]
        image=pil_from_bytes(self.backend.read_page(index))
        with self._lock:
            self._cache[index]=image
            for key in list(self._cache):
                if abs(key-index)>self.WINDOW:self._cache.pop(key,None)
        return image
    def prefetch(self,index):
        if not 0<=index<self.count:return
        with self._lock:
            if index in self._cache or index in self._prefetching:return
            self._prefetching.add(index)
        def work():
            try:self.get_pil(index)
            finally:
                with self._lock:self._prefetching.discard(index)
        threading.Thread(target=work,daemon=True).start()
    def get_thumbnail_pil(self,index,width,height):
        image=self.get_pil(index).convert("RGB"); image.thumbnail((width,height),Image.BILINEAR); return image
    def close(self):self.backend.close(); self._cache.clear()
