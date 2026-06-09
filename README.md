# <img width="150" height="150" alt="panellogo" src="https://github.com/user-attachments/assets/2a81e833-9854-4823-a0f3-5134dd2823c2" />


> Leitor de quadrinhos leve, bonito e rápido para Windows.

![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=flat&logo=windows)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)
![Version](https://img.shields.io/badge/Versão-1.2_Beta-orange?style=flat)
![License](https://img.shields.io/badge/Licença-MIT-green?style=flat)

---

## Download

Baixe o instalador na aba [**Releases**](https://github.com/lucrazy-fn/PANEL-ComicBookReader/releases) e execute o `Panel_Reader_Setup_v1.2.exe`.

> ⚠️ **v1.2 Beta** — Atualização grande com muitas features novas. O Panel é feito por uma pessoa só, então pode conter bugs. Se encontrar algum problema, [abre uma issue](https://github.com/lucrazy-fn/PANEL-ComicBookReader/issues)!

---

## Sobre

Panel é um leitor de quadrinhos feito em Python com foco em ser simples, rápido e visualmente agradável. Sem propagandas, sem conta, sem internet — só você e seus quadrinhos.

---

## Screenshots

**Biblioteca**
<img width="1920" height="1032" alt="{665B1181-5D3D-457B-8391-F0D69DA6513C}" src="https://github.com/user-attachments/assets/4c4a5d9f-bb73-4168-b752-f7056dc79b82" />


---

**Hover nas capas**
<img width="1920" height="1032" alt="{A5FBAFE0-D6DB-4E30-9576-5C1BEE25B8AB}" src="https://github.com/user-attachments/assets/b48b07cf-1543-4e7f-bd35-e4357ad06982" />


---

**Leitor**
<img width="1920" height="1080" alt="{E7D8B7CA-3CE4-4A12-AC8B-1B3DD0936D6C}" src="https://github.com/user-attachments/assets/0716f1d7-a6b7-4375-b6dd-7a538e4c024e" />


---

**Coleções**
<img width="1920" height="1032" alt="{379E4AD8-43AD-4326-8E4F-124AB2EAF3F2}" src="https://github.com/user-attachments/assets/c7aa22d4-af69-4af9-8d30-875d5de88e21" />


---

## Funcionalidades

### 📚 Biblioteca
- Visualização em grade com capas carregadas em segundo plano
- Hover animado nas capas com efeito de zoom e overlay
- Filtros de status: *Não lidos*, *Lendo*, *Concluídos*, *Favoritos*
- Busca por título, série, autor e editora
- Seção "Continuar Lendo" com os últimos abertos
- Progresso de leitura salvo automaticamente

### 🖱️ Menu de contexto
- Clique com botão direito em qualquer capa
- Favoritar/desfavoritar com ★ dourado visível no card
- Marcar como *Lendo* (badge azul) ou *Concluído* (badge verde)

### 📖 Leitor
- Zoom livre com scroll, botões ou slider
- Zoom centrado no cursor com `Ctrl + Scroll`
- Arrasto da imagem com o mouse
- Rotação de página (`R`)
- Controle de brilho (`[` e `]`)
- Animação de transição suave entre páginas
- Barra de progresso clicável para pular páginas
- Modo tela cheia (`F` / `F11`)
- Modo imersivo (`I`) — esconde toda a interface
- Bookmarks marcados na barra de progresso

### ▭▭ Página Dupla
- Visualiza duas páginas lado a lado
- Funciona junto com o modo mangá

### 🖼️ Miniaturas
- Faixa de miniaturas de todas as páginas
- Clique em qualquer miniatura para ir direto

### 📚 Coleções
- Subpastas da biblioteca viram coleções automaticamente
- Arquivos com nome similar são agrupados em séries
- Filtros: *Todos*, *Pastas*, *Séries*
- Ordenação por *Nome*, *Data* ou *Progresso*
- Progresso da série visível no card da coleção
- Botão "Continuar Lendo" retoma da última edição aberta

### 💾 Backup
- Exporta progresso, bookmarks e favoritos em `.json`
- Importa de volta — útil ao trocar de computador

---

## Como usar

### 1. Configurar a biblioteca
Clique em **Pasta** no menu lateral e selecione a pasta com seus quadrinhos.

### 2. Abrir um quadrinho
Dê **duplo clique** em qualquer capa. Ou clique duas vezes num arquivo `.cbz` / `.cbr` direto pelo Windows Explorer.

### 3. Controles do leitor

| Ação | Tecla / Mouse |
|---|---|
| Próxima página | `→` · `PageDown` · Scroll ↓ |
| Página anterior | `←` · `PageUp` · Scroll ↑ |
| Zoom in/out | `=` / `-` · Ctrl + Scroll |
| Encaixar na tela | Botão **Encaixar** |
| Arrastar imagem | Clique e arraste |
| Girar página | `R` |
| Brilho | `[` diminui · `]` aumenta |
| Tela cheia | `F` · `F11` |
| Modo imersivo | `I` |
| Bookmark | `B` |
| Miniaturas | `G` |
| Alternar tema | `T` |
| Atalhos | `?` |
| Sair tela cheia | `Esc` |

---

## Formatos suportados

| Formato | Suporte |
|---|---|
| `.cbz` / `.zip` | ✅ Nativo |
| `.cbr` / `.rar` | ✅ Com [WinRAR](https://www.win-rar.com/) instalado |
| `.pdf` | ✅ Com `pip install pymupdf` |

---

## Instalação manual (código fonte)

```bash
git clone https://github.com/lucrazy-fn/PANEL-ComicBookReader
cd panel
python -m pip install pillow rarfile pymupdf
python ComicReader.py
```

---

## Plataformas

| Sistema | Suporte |
|---|---|
| Windows 10 / 11 | ✅ |
| Linux | 🔜 Futuramente |
| macOS | 🔜 Futuramente |

---

## Licença

Veja o arquivo [LICENSE](https://github.com/lucrazy-fn/PANEL-ComicBookReader?tab=MIT-1-ov-file).
