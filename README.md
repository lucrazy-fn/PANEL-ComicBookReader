# 📚 PANEL — Comic Book Reader
**PANEL** é um leitor de quadrinhos leve, rápido e personalizável, desenvolvido em Python com Tkinter e Pillow. Ele suporta arquivos nos formatos `.cbz`, `.cbr`, `.zip` e `.rar`, e conta com uma interface moderna, modos de visualização, temas e gerenciamento de biblioteca.

---

## ✨ Funcionalidades

✅ Suporte aos formatos: `.cbz`, `.cbr`, `.zip`, `.rar`  
✅ Dois modos de interface: **Desktop** e **Mobile/Tablet**  
✅ Temas **Claro** e **Escuro**  
✅ Modo **Mangá** (leitura inversa, direita para esquerda)  
✅ Controles de **Zoom** (+ / - / Encaixar)  
✅ Arrastar página com o mouse  
✅ Navegação por teclado e gestos  
✅ **Biblioteca própria**:
   - Escolher pasta da biblioteca
   - Renomear arquivos
   - Excluir arquivos
   - Lista organizada dos seus quadrinhos
✅ Salva automaticamente o **progresso de leitura**
✅ Tela cheia
✅ Idiomas: 🇧🇷 Português | 🇺🇸 Inglês
✅ Ícones personalizados
✅ Código aberto e customizável

---

## 🚀 Como usar

### 📋 Pré-requisitos
Você precisa ter o **Python 3.8+** instalado no seu computador.

Além disso, é necessário instalar algumas bibliotecas:
```bash
pip install pillow rarfile
```

> 💡 Para arquivos `.cbr` (RAR), o programa precisa do **UnRAR** instalado. No Windows, geralmente já vem com o WinRAR. Se precisar, baixe em: win-rar.com

---

### 📁 Estrutura de arquivos
Organize os arquivos assim para tudo funcionar:
```
📦 Pasta que você escolher
 ┣ 📄 comicreader.py   # Código principal
 ┣ 📂 Icons            # Pasta com ícones (.png)
 ┃  ┣ 🖼️ open.png
 ┃  ┣ 🖼️ library.png
 ┃  ┗ ... (outros ícones)
 ┣ 📄 panel.ico         # Ícone da janela principal
```

---

### ▶️ Executando
Abra o terminal, navegue até a pasta do projeto e execute:
```bash
python comicreader.py
```

---

## 📖 Guia rápido
1. Ao abrir, escolha o modo de interface: **Desktop** ou **Mobile**.
2. Clique em `Abrir Arquivo` para ler um quadrinho ou `Biblioteca` para ver todos os arquivos da sua pasta.
3. **Na Biblioteca**:
   - Clique com o botão direito em qualquer arquivo para **Renomear** ou **Excluir**.
   - Use o botão `Escolher Pasta da Biblioteca` para definir onde seus arquivos estão.
4. **Controles**:
   - `← / →` : Página anterior / próxima
   - `+ / -` : Aumentar / diminuir zoom
   - `F` : Tela cheia
   - `T` : Alternar tema
   - `M` : Ativar/desativar modo mangá
   - `Arrastar com o mouse` : Mover a página ampliada

---

## 🤝 Como contribuir

Esse é um projeto aberto e você pode ajudar a melhorar! 💙

### 🚩 Quer ajudar?
- ✅ Reporte bugs ou sugira ideias na aba [Issues](https://github.com/seu-usuario/seu-repositorio/issues)
- ✅ Faça um **Fork** do projeto, implemente melhorias e envie um **Pull Request**
- ✅ Compartilhe o projeto com amigos

### 💡 Ideias para futuras versões
- [ ] Suporte a marcadores/favoritos
- [ ] Modo de visualização de duas páginas
- [ ] Ordenação da biblioteca (por nome, data, tamanho)
- [ ] Suporte a mais formatos de imagem
- [ ] Tradução para outros idiomas

---

## ⚠️ Avisos importantes

### 📌 Direitos autorais e créditos
- Você **pode usar, modificar e distribuir** esse código, **desde que mantenha os créditos ao autor original** e compartilhe as alterações sob a mesma licença.
- Esse software é gratuito e **não pode ser vendido** ou usado para fins comerciais sem permissão.
- Lembre-se: **você é responsável pelo uso que faz desse programa** — respeite os direitos autorais dos quadrinhos que você lê.

### 📝 Licença
Esse projeto está licenciado sob a **MIT License** — veja o arquivo LICENSE para detalhes.

---

## 💖 Agradecimentos
Obrigado por usar o **PANEL — Comic Book Reader**!  
Se gostou, deixe uma ⭐ no repositório — isso ajuda muito a continuar evoluindo o projeto.

---

**Desenvolvido por lucrazy-fn/Luan** 🚀
---
