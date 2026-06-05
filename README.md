# ◈ Panel — Comic Reader

> Leitor de quadrinhos leve, bonito e rápido para Windows.

![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=flat&logo=windows)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)
![License](https://img.shields.io/badge/Licença-MIT-green?style=flat)

---

## Download

Baixe o instalador na aba [**Releases**](https://github.com/lucrazy-fn/PANEL-ComicBookReader/releases/tag/v1.0) e execute o `Panel_ComicReader_Setup.exe`.

---

## O que é o Panel?

Panel é um leitor de quadrinhos feito em Python com foco em ser simples, rápido e visualmente agradável. Sem propagandas, sem conta, sem internet — só você e seus quadrinhos.

---

## Funcionalidades

### 📚 Biblioteca
- Visualização em grade com capas dos quadrinhos
- Escolha qualquer pasta do seu computador como biblioteca
- Hover animado nas capas com efeito de zoom e overlay
- Progresso de leitura salvo automaticamente — retoma de onde parou

### 📖 Leitor
- Zoom livre com scroll, botões ou slider
- Arrasto da imagem com o mouse
- Animação de transição suave entre páginas
- Barra de progresso de leitura na parte inferior
- Modo tela cheia

### 🇯🇵 Modo Mangá
- Inverte a direção da leitura para direita → esquerda
- Ativado com um clique, direto no leitor

### 🎨 Temas
- Modo escuro e modo claro
- Alternável a qualquer momento, tanto na biblioteca quanto no leitor

### 🌐 Idiomas
- Português e Inglês
- Escolha na tela inicial ao abrir o app

---

## Formatos suportados

| Formato | Suporte |
|---|---|
| `.cbz` / `.zip` | ✅ Nativo |
| `.cbr` / `.rar` | ✅ Com [WinRAR](https://www.win-rar.com/) instalado |

---

## Como usar

### 1. Configurar a biblioteca
Ao abrir o Panel pela primeira vez, clique em **Pasta** na barra lateral esquerda e selecione a pasta onde estão seus arquivos de quadrinhos. O Panel vai carregar as capas automaticamente.

### 2. Abrir um quadrinho
Dê **dois cliques** em qualquer capa para abrir o leitor.

### 3. Navegar pelas páginas

| Ação | Tecla / Mouse |
|---|---|
| Próxima página | `→` · `PageDown` · Scroll ↓ |
| Página anterior | `←` · `PageUp` · Scroll ↑ |
| Zoom in | `=` · Ctrl + Scroll ↑ |
| Zoom out | `-` · Ctrl + Scroll ↓ |
| Encaixar na tela | Botão **Encaixar** |
| Arrastar imagem | Clique e arraste |
| Tela cheia | `F` · `F11` |
| Sair da tela cheia | `Esc` |
| Alternar tema | `T` |

### 4. Modo Mangá
Clique no botão 🇯🇵 no leitor para ativar a leitura da direita pra esquerda. Clique novamente para desativar.

### 5. Progresso de leitura
O Panel salva automaticamente em qual página você parou. Na próxima vez que abrir o mesmo quadrinho, ele retoma de onde parou.

---

## Instalação manual (código fonte)

Se preferir rodar direto pelo Python:

```bash
git clone https://github.com/seuusuario/panel.git
cd panel
python -m pip install pillow rarfile
python ComicReader.py
```

> Para arquivos `.cbr`, instale o [WinRAR](https://www.rarlab.com/) em `C:\Program Files\WinRAR\`.

---

## Plataformas

| Sistema | Suporte |
|---|---|
| Windows 10 / 11 | ✅ |
| Linux | 🔜 Futuramente |
| macOS | 🔜 Futuramente |

---

## Estrutura do projeto

```
Panel/
├── ComicReader.py          # Código principal
├── panel.ico               # Ícone do app
├── Icons/                  # Ícones da interface
│   ├── library.png
│   ├── next.png
│   ├── prev.png
│   ├── zoom_in.png
│   ├── zoom_out.png
│   ├── theme.png
│   └── open.png
├── library_config.json     # Pasta da biblioteca (gerado automaticamente)
└── reading_progress.json   # Progresso de leitura (gerado automaticamente)
```

---

## Licença

Veja o arquivo [LICENSE](LICENSE).
