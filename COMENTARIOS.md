# Comentários do código

Comentários movidos sem alterar o código executável. As linhas indicam a posição original. Docstrings e diretivas técnicas foram preservadas.

## panel_app/auth_views.py

Linha 28:

~~~~text
# "login" | "register"
~~~~

Linha 31:

~~~~text
# nome -> (entry, placeholder)
~~~~

Linha 43:

~~~~text
# ---------- janela ----------
~~~~

Linha 60:

~~~~text
# debounce: só reconstrói quando o redimensionamento se estabiliza,
~~~~

Linha 61:

~~~~text
# pra não recalcular a cada pixel arrastado
~~~~

Linha 73:

~~~~text
# ---------- construção ----------
~~~~

Linha 110:

~~~~text
# ---- fase 1: calcular posições (sem desenhar), tudo em função de scale ----
~~~~

Linha 118:

~~~~text
# Cadastro e login possuem três campos. O login ganhou o código
~~~~

Linha 119:

~~~~text
# 2FA opcional; manter "2" aqui fazia o botão ser desenhado por
~~~~

Linha 120:

~~~~text
# cima do terceiro campo.
~~~~

Linha 133:

~~~~text
# ---- fase 2: desenhar ----
~~~~

Linha 142:

~~~~text
# ---- abas segmentadas (Entrar / Cadastrar) ----
~~~~

Linha 159:

~~~~text
# ---- avatar ----
~~~~

Linha 163:

~~~~text
# ---- campos ----
~~~~

Linha 179:

~~~~text
# ---- status (erro/info) ----
~~~~

Linha 186:

~~~~text
# ---- botão principal ----
~~~~

Linha 194:

~~~~text
# ---- link de troca de modo ----
~~~~

Linha 205:

~~~~text
# ---- convidado, fora do cartão ----
~~~~

Linha 289:

~~~~text
# ---------- interação ----------
~~~~

## panel_app/library_views.py

Linha 43:

~~~~text
# None = convidado; preenchido após login/cadastro
~~~~

Linha 70:

~~~~text
# Restaura uma sessão somente depois de validá-la sem bloquear a UI.
~~~~

Linha 78:

~~~~text
# A biblioteca local continua utilizável offline.
~~~~

Linha 99:

~~~~text
# auth é None no modo convidado, ou um AuthResponse/LocalSession
~~~~

Linha 100:

~~~~text
# com token+usuário. Em nenhum dos dois casos isso bloqueia o
~~~~

Linha 101:

~~~~text
# restante do app — biblioteca, leitor e coleções continuam
~~~~

Linha 102:

~~~~text
# funcionando exatamente como hoje.
~~~~

Linha 188:

~~~~text
# best-effort; segue com a limpeza local
~~~~

Linha 191:

~~~~text
# Reabre a tela de login por cima da biblioteca (mesmo padrão do
~~~~

Linha 192:

~~~~text
# início do app); ao escolher de novo, _on_auth_done reconstrói
~~~~

Linha 193:

~~~~text
# o shell — biblioteca local, progresso e favoritos não mudam.
~~~~

Linha 590:

~~~~text
# Animate the canvas background rather than rebuilding its icons each frame.
~~~~

## panel_app/publishing_views.py

Linha 104:

~~~~text
# Window transparency is optional on some platforms.
~~~~

## panel_app/runtime.py

Linha 48:

~~~~text
# compatibilidade com versões antigas do PyMuPDF
~~~~

Linha 64:

~~~~text
# runtime.py fica em panel_app/, enquanto os recursos distribuídos
~~~~

Linha 65:

~~~~text
# (Icons, logo e panel.ico) permanecem na raiz do projeto.
~~~~

Linha 157:

~~~~text
# Fonte canônica extraída; os aliases locais preservam a compatibilidade
~~~~

Linha 158:

~~~~text
# durante a migração das telas restantes.
~~~~

Linha 181:

~~~~text
# necessário no Windows p/ as cores serem respeitadas
~~~~

Linha 500:

~~~~text
# Implementações canônicas extraídas do monólito. As definições antigas acima
~~~~

Linha 501:

~~~~text
# serão removidas quando os consumidores restantes estiverem migrados.
~~~~

Linha 737:

~~~~text
# panel_client não instalado (ex: dependência 'requests' ausente) ->
~~~~

Linha 738:

~~~~text
# o app continua 100% funcional no modo convidado, sem tela de conta.
~~~~

## panel_app/storage.py

Linha 22:

~~~~text
# Alguns diretórios sincronizados pelo OneDrive podem deixar um item
~~~~

Linha 23:

~~~~text
# fantasma com este nome que o Explorer enxerga, mas o Python não
~~~~

Linha 24:

~~~~text
# consegue abrir como pasta. Usa um diretório novo sem apagar o cache.
~~~~

## panel_app/themes.py

Linha 7:

~~~~text
# Paleta refinada: contraste um pouco maior, vermelho menos "puro"/saturado
~~~~

Linha 8:

~~~~text
# (fica menos agressivo em áreas grandes), acento com gradiente quente
~~~~

Linha 9:

~~~~text
# vermelho->laranja, e cinzas com uma leve nota violeta para dar
~~~~

Linha 10:

~~~~text
# profundidade sem parecer só "preto e branco".
~~~~

## panel_client/api_client.py

Linha 109:

~~~~text
# Nome novo; o antigo permanece como compatibilidade para integrações existentes.
~~~~

## panel_client/session_store.py

Linha 41:

~~~~text
# Arquivo corrompido/formato antigo -> trata como "sem sessão",
~~~~

Linha 42:

~~~~text
# nunca trava o app por causa disso.
~~~~

## panel_backend/accounts/models.py

Linha 26:

~~~~text
# SQLite armazena DateTime sem fuso; geramos UTC explicitamente e
~~~~

Linha 27:

~~~~text
# removemos apenas o tzinfo na borda de persistência.
~~~~

## panel_backend/accounts/service.py

Linha 69:

~~~~text
# garante user.id preenchido antes de criar o token
~~~~

## panel_backend/api/deps.py

Linha 25:

~~~~text
# A mesma sessão é reutilizada pelo FastAPI na requisição. Isso coloca
~~~~

Linha 26:

~~~~text
# Comic, decisão de moderação e Publication na mesma transação.
~~~~

## panel_backend/api/routes/publications.py

Linha 37:

~~~~text
# Keep moderation history and stored bytes for audit; no public route can access them.
~~~~

## panel_backend/api/schemas.py

Linha 15:

~~~~text
# ---------- Auth ----------
~~~~

Linha 181:

~~~~text
# ---------- Publications ----------
~~~~

Linha 256:

~~~~text
# ---------- Moderation ----------
~~~~

## panel_backend/catalog/assets.py

Linha 70:

~~~~text
# Alguns distribuidores usam extensão .cbr em arquivos que são ZIP.
~~~~

Linha 71:

~~~~text
# Detectamos pelo conteúdo, assim como o leitor desktop.
~~~~

## panel_backend/catalog/models.py

Linha 40:

~~~~text
# CSV simples por enquanto
~~~~

Linha 42:

~~~~text
# caminho/chave de storage
~~~~

Linha 64:

~~~~text
# Espelha panel_backend.moderation.models.ModerationStatus, mas guardado
~~~~

Linha 65:

~~~~text
# como string simples aqui pra este módulo não depender do pacote de
~~~~

Linha 66:

~~~~text
# moderação em nível de import de enum (evita acoplamento circular).
~~~~

## panel_backend/catalog/service.py

Linha 69:

~~~~text
# garante comic.id preenchido
~~~~

Linha 88:

~~~~text
# A automação sugere risco, mas não publica nem rejeita sozinha.
~~~~

## panel_backend/db.py

Linha 34:

~~~~text
# Importa os módulos de modelo para que suas tabelas sejam registradas
~~~~

Linha 35:

~~~~text
# em Base.metadata antes do create_all.
~~~~

## panel_backend/demo_full_flow.py

Linha 27:

~~~~text
# 1. Cadastro (ou login, se já existir de uma execução anterior)
~~~~

Linha 35:

~~~~text
# 2. Envio de um quadrinho autoral, com declaração e licença
~~~~

Linha 55:

~~~~text
# 3. Tentativa suspeita, pelo mesmo usuário
~~~~

## panel_backend/moderation/analyzers/ai_analyzer.py

Linha 32:

~~~~text
# Se não houver chave configurada, o service pula este analisador
~~~~

Linha 33:

~~~~text
# em vez de quebrar a triagem inteira.
~~~~

Linha 45:

~~~~text
# TODO (v2): implementar a chamada real ao provedor configurado em
~~~~

Linha 46:

~~~~text
# self._config.ai_provider, usando self._config.ai_api_key.
~~~~

Linha 47:

~~~~text
# A resposta do provedor deve ser convertida para AnalyzerFinding
~~~~

Linha 48:

~~~~text
# aqui dentro — o resto do sistema nunca deve saber qual provedor
~~~~

Linha 49:

~~~~text
# está sendo usado.
~~~~

## panel_backend/moderation/analyzers/base.py

Linha 23:

~~~~text
#: nome curto usado em logs e no campo `analyzer_name` do finding
~~~~

## panel_backend/moderation/analyzers/metadata_rules.py

Linha 28:

~~~~text
# Acima disso, consideramos que título/autor "batem" com uma obra conhecida.
~~~~

Linha 31:

~~~~text
# Editoras/estúdios comerciais grandes — se aparecerem em metadados
~~~~

Linha 32:

~~~~text
# embutidos, isso é um sinal forte, mesmo sem bater no fuzzy match do título.
~~~~

Linha 49:

~~~~text
# regras simples nunca merecem confiança alta
~~~~

Linha 51:

~~~~text
# 1. Fuzzy match do título contra obras conhecidas
~~~~

Linha 71:

~~~~text
# 2. Ausência de declaração de autoria/autorização
~~~~

Linha 78:

~~~~text
# 3. A licença é somente uma declaração do usuário. Ela é registrada
~~~~

Linha 79:

~~~~text
# como sinal, mas não reduz risco automaticamente sem validação.
~~~~

Linha 84:

~~~~text
# 4. Metadados embutidos no arquivo (ex.: ComicInfo.xml -> Publisher)
~~~~

## panel_backend/moderation/config.py

Linha 18:

~~~~text
# Limiares gerais de decisão
~~~~

Linha 19:

~~~~text
# confiança mínima p/ status = rejected
~~~~

Linha 20:

~~~~text
# confiança mínima p/ status = pending_review
~~~~

Linha 22:

~~~~text
# Configuração do futuro analisador de IA (opcional — ver ai_analyzer.py)
~~~~

Linha 23:

~~~~text
# ex: "anthropic", "openai" — nunca usado ainda na v1
~~~~

Linha 24:

~~~~text
# lido de env, NUNCA hardcoded
~~~~

## panel_backend/moderation/demo.py

Linha 30:

~~~~text
# Cenário 1: obra autoral original, tudo declarado -> deve aprovar
~~~~

Linha 42:

~~~~text
# Cenário 2: título muito parecido com obra conhecida -> deve rejeitar/pending
~~~~

Linha 52:

~~~~text
# Cenário 3: sem declaração de autoria, mas título neutro -> pending_review
~~~~

## panel_backend/moderation/known_works.py

Linha 27:

~~~~text
# Exemplo mínimo — troque por um arquivo externo (KNOWN_WORKS_FILE) assim
~~~~

Linha 28:

~~~~text
# que houver uma lista de verdade para carregar.
~~~~

## panel_backend/moderation/models.py

Linha 24:

~~~~text
# baixo risco — publicação liberada
~~~~

Linha 25:

~~~~text
# indícios de risco — aguarda revisão humana
~~~~

Linha 26:

~~~~text
# fortes indícios de conteúdo não permitido
~~~~

Linha 47:

~~~~text
# Declaração feita pelo próprio usuário no momento do envio.
~~~~

Linha 48:

~~~~text
# "eu sou o autor" ou
~~~~

Linha 49:

~~~~text
# "tenho autorização para publicar"
~~~~

Linha 50:

~~~~text
# ex: "CC-BY-4.0", "Domínio Público", None
~~~~

Linha 52:

~~~~text
# Metadados técnicos do arquivo (extraídos automaticamente, não digitados)
~~~~

Linha 54:

~~~~text
# hash do conteúdo, útil p/ dedupe/similaridade
~~~~

Linha 56:

~~~~text
# ex: ComicInfo.xml, EXIF, etc.
~~~~

Linha 69:

~~~~text
# 0.0 a 1.0 — confiança do próprio analisador no achado
~~~~

Linha 70:

~~~~text
# justificativa interna, legível por humano (não jurídica)
~~~~

Linha 71:

~~~~text
# dados brutos p/ auditoria/debug
~~~~

Linha 83:

~~~~text
# texto interno, para logs e revisão humana
~~~~

## panel_backend/moderation/service.py

Linha 40:

~~~~text
# Ordem dos analisadores na lista não importa para o resultado —
~~~~

Linha 41:

~~~~text
# o pior risco encontrado por qualquer um deles prevalece.
~~~~

Linha 56:

~~~~text
# Analisadores ainda não implementados (ex: AIAnalyzer na v1)
~~~~

Linha 57:

~~~~text
# são simplesmente pulados — não devem derrubar a triagem.
~~~~

Linha 60:

~~~~text
# Falha real de um analisador (ex: API externa fora do ar)
~~~~

Linha 61:

~~~~text
# também não deve travar a publicação inteira; registramos
~~~~

Linha 62:

~~~~text
# como um finding de baixa confiança e seguimos.
~~~~

Linha 80:

~~~~text
# Nenhum analisador disponível/rodou — não aprova automaticamente
~~~~

Linha 81:

~~~~text
# às cegas; manda para revisão humana por segurança.
~~~~

Linha 95:

~~~~text
# Confiança do resultado combinado = maior confiança entre os
~~~~

Linha 96:

~~~~text
# analisadores que apontaram o risco mais alto encontrado.
~~~~

Linha 121:

~~~~text
# Baixíssima confiança mesmo em risco baixo -> por segurança,
~~~~

Linha 122:

~~~~text
# revisão humana em vez de aprovação automática.
~~~~

## panel_backend/moderation/storage.py

Linha 40:

~~~~text
# Preparado para o futuro: revisão manual sobrescreve o status automático
~~~~

Linha 151:

~~~~text
# Gravação atômica: uma interrupção não deixa o JSON pela metade.
~~~~

Linha 176:

~~~~text
# O lock cobre leitura + alteração + escrita para evitar perda de
~~~~

Linha 177:

~~~~text
# registros quando duas requisições chegam ao mesmo tempo.
~~~~

## panel_backend/web/moderators.html

Linha 3:

~~~~text
/* acabamento visual 2.0 */
~~~~

# Docstrings extraídas

Linhas originais antes desta extração. Os textos deixam de estar disponíveis em `__doc__` e `help()`.

## ComicReader.py

### módulo — linha 1

~~~~text
Compatibilidade com o antigo ponto de entrada do PANEL.

O aplicativo foi dividido no pacote :mod:`panel_app`. Novos códigos devem
importar diretamente o módulo responsável; este arquivo permanece para que
atalhos antigos que executam ``ComicReader.py`` continuem funcionando.

~~~~

## panel_app/__init__.py

### módulo — linha 1

~~~~text
Aplicativo desktop PANEL.

O pacote concentra o launcher e serviços extraídos do antigo módulo único.
As telas serão migradas gradualmente sem quebrar imports existentes.

~~~~

## panel_app/account_views.py

### módulo — linha 1

~~~~text
Telas completas de perfil e notificações embutidas na janela principal.
~~~~

### _pill_button — linha 23

~~~~text
Botão com cantos arredondados no mesmo espírito visual do resto do
    app — versão enxuta e independente (sem depender do make_pill do
    ComicReader.py), pra este módulo continuar autônomo.
~~~~

### _card — linha 55

~~~~text
'Cartão' com borda sutil — mesma linguagem visual do resto do app,
    sem desenhar em canvas (mais robusto pra um formulário de altura
    variável).
~~~~

### _role_badge — linha 86

~~~~text
Selo em formato de cápsula usando arco+linha (mais confiável que
    polígono arredondado 'smooth' em formas pequenas, onde a curva do
    Tkinter distorce).
~~~~

## panel_app/archive.py

### módulo — linha 1

~~~~text
Leitura de CBZ, CBR e PDF e cache de páginas em memória.
~~~~

## panel_app/auth.py

### módulo — linha 1

~~~~text
Apresentação dos cargos da conta.
~~~~

## panel_app/auth_views.py

### módulo — linha 1

~~~~text
Interface de autenticação e cadastro.
~~~~

### AuthWindow — linha 5

~~~~text

    Tela inicial: entrar, criar conta, ou continuar como convidado.
    Um cartão único com abas (Entrar/Cadastrar) trocando o conteúdo do
    formulário; "continuar como convidado" fica fora do cartão, sempre
    visível. Ao terminar, chama self.cb(user) e se destrói — user=None
    significa convidado, igual antes.
    
~~~~

### _scale_factor — linha 76

~~~~text

        Fator de escala do cartão em relação ao tamanho base (400x660).
        Usa o menor dos dois eixos pra o cartão nunca estourar a janela
        em nenhuma direção (mesmo com proporção bem larga ou bem alta),
        e nunca fica menor que 1x nem passa de 1.6x (senão fica gigante
        e vazio numa tela ultrawide).
        
~~~~

### _capture_values — linha 219

~~~~text
Preserva o que o usuário já digitou ao reconstruir a tela
        (redimensionar janela, maximizar, entrar/sair de tela cheia).
~~~~

## panel_app/collections.py

### módulo — linha 1

~~~~text
Operações de coleção sem dependência da interface gráfica.
~~~~

## panel_app/community.py

### módulo — linha 1

~~~~text
Cache offline do catálogo da comunidade.
~~~~

## panel_app/community_views.py

### módulo — linha 1

~~~~text
Descoberta, detalhes e downloads da comunidade.
~~~~

### CommunityWindow — linha 6

~~~~text
Catálogo público ou histórico de envios da conta.
~~~~

### CommunityTab — linha 239

~~~~text
Catálogo em grade embutido, com a mesma linguagem da Biblioteca.
~~~~

## panel_app/components.py

### módulo — linha 1

~~~~text
Pequenos utilitários reutilizáveis de interface.
~~~~

## panel_app/downloads.py

### módulo — linha 1

~~~~text
Fila de downloads com progresso, pausa, cancelamento e histórico.
~~~~

## panel_app/launcher.py

### módulo — linha 1

~~~~text
Ponto de entrada oficial do aplicativo desktop.
~~~~

### _ensure_local_api — linha 9

~~~~text
Inicia a API junto com o app quando o endereço configurado é local.
~~~~

## panel_app/library.py

### módulo — linha 1

~~~~text
Descoberta de arquivos da biblioteca local.
~~~~

## panel_app/library_views.py

### módulo — linha 1

~~~~text
Janela principal e navegação da biblioteca.
~~~~

### _sync_shared_settings — linha 59

~~~~text
Atualiza valores imutáveis importados antes da leitura das preferências.
~~~~

### _siblings_of — linha 835

~~~~text
Acha as outras edições da mesma série/pasta, ordenadas.
~~~~

## panel_app/library_widgets.py

### módulo — linha 1

~~~~text
Cartões, metadados, pesquisa e coleções da biblioteca.
~~~~

## panel_app/moderation.py

### módulo — linha 1

~~~~text
Políticas de acesso à moderação compartilhadas pela interface.
~~~~

## panel_app/moderation_views.py

### módulo — linha 1

~~~~text
Fila visual de moderação e análise de publicações.
~~~~

### ModerationWindow — linha 6

~~~~text
Fila administrativa de publicações que aguardam revisão humana.
~~~~

## panel_app/publishing_views.py

### módulo — linha 1

~~~~text
Envio de novas obras e capítulos.
~~~~

### PublishDialog — linha 5

~~~~text

    Formulário pra enviar um quadrinho da biblioteca local pra moderação
    e, se aprovado, pra comunidade. Só os METADADOS são enviados agora —
    o arquivo em si continua no computador do usuário (upload de arquivo
    de verdade é um passo futuro separado, de armazenamento).
    
~~~~

## panel_app/reader.py

### módulo — linha 1

~~~~text
Estado persistente específico do leitor.
~~~~

## panel_app/reader_views.py

### módulo — linha 1

~~~~text
Janelas e componentes do leitor de quadrinhos.
~~~~

### _check_visible — linha 124

~~~~text
Carrega só páginas visíveis + margem.
~~~~

### _processed_pil — linha 369

~~~~text
Aplica rotação + brilho.
~~~~

### _compose_pages — linha 378

~~~~text
Retorna a imagem a desenhar (1 ou 2 páginas).
~~~~

### _update_done_btn — linha 494

~~~~text
Mostra/esconde o botão 'Concluído' na última página.
~~~~

## panel_app/runtime.py

### módulo — linha 1

~~~~text

╔══════════════════════════════════════╗
║         PANEL — CBZ/CBR Reader       ║
║   Zoom · Drag · Page Nav · Themes    ║
╚══════════════════════════════════════╝
Requires: pip install pillow rarfile
Opcional (PDF): pip install pymupdf

~~~~

### apply_scrollbar_style — linha 175

~~~~text
Estiliza as ttk.Scrollbar pra combinar com o resto da interface —
    sem isso elas ficam com o cinza padrão do Windows, destoando de uma
    UI toda customizada em tons escuros/acento vermelho.
~~~~

### _generated_icon — linha 199

~~~~text
Desenha os ícones novos em alta resolução e reduz com antialiasing.
~~~~

### ArchiveBackend — linha 303

~~~~text

    Abstrai o acesso ao arquivo (zip/rar/pdf).
    NÃO guarda bytes de páginas — só os nomes das entradas.
    Extrai bytes sob demanda via read_page(idx).
    
~~~~

### read_page — linha 349

~~~~text
Retorna os bytes da página idx (decodificável pelo PIL).
~~~~

### extract_cover_only — linha 372

~~~~text
Lê só a primeira página (capa) — usado em listagens.
~~~~

### SmartPageLoader — linha 420

~~~~text

    Carrega páginas sob demanda mantendo só uma janela em RAM.
    Decodifica em thread; entrega PIL.Image (não PhotoImage, pra ser thread-safe).
    
~~~~

### prefetch — linha 461

~~~~text
Pré-carrega página em background (não bloqueia).
~~~~

### animate_color — linha 636

~~~~text
Small interruptible transition, cancelled when its widget is destroyed.
~~~~

### _draw_field_icon — linha 743

~~~~text
Ícone vetorial simples (sem depender de arquivo de imagem), no
    mesmo espírito monocromático dos ícones da barra lateral.
~~~~

## panel_app/storage.py

### módulo — linha 1

~~~~text
Persistência local da biblioteca, independente da interface Tk.
~~~~

## panel_app/sync.py

### módulo — linha 1

~~~~text
Identidade por conteúdo e preparação do estado sincronizável.
~~~~

## panel_app/themes.py

### módulo — linha 1

~~~~text
Paletas, traduções e estado visual compartilhado do desktop.
~~~~

## panel_app/translations.py

### módulo — linha 1

~~~~text
Helpers de tradução; o catálogo permanece em themes durante a migração.
~~~~

## panel_app/updater.py

### módulo — linha 1

~~~~text
Consulta opcional de versão; nunca substitui arquivos sem confirmação.
~~~~

## panel_client/api_client.py

### módulo — linha 1

~~~~text

Cliente HTTP fino pra falar com panel_backend/api. Nada no ComicReader.py
deveria montar uma URL ou fazer uma request diretamente; tudo passa por
aqui.

Qualquer falha de rede (API fora do ar, sem internet) é tratada como
"não foi possível fazer isso agora" — nunca derruba o app. O modo
convidado continua 100% funcional mesmo com a API offline.

~~~~

### ApiUnavailableError — linha 24

~~~~text
API fora do ar, sem internet, ou timeout. Não é erro de credenciais.
~~~~

### ApiAuthError — linha 28

~~~~text
Usuário/senha inválidos, usuário já em uso, sessão expirada, etc — erro do usuário, não da rede.
~~~~

### ApiServerError — linha 32

~~~~text
A API respondeu, mas não conseguiu concluir a operação.
~~~~

### logout — linha 66

~~~~text

    Best-effort: revoga o token no servidor, mas nunca lança exceção.
    O chamador (ComicReader.py) deve limpar a sessão local independente
    do resultado — "sair" não pode falhar do ponto de vista do usuário
    só porque a internet caiu.
    
~~~~

### get_current_user — linha 83

~~~~text
Valida um token salvo antes de restaurar a sessão.
~~~~

### submit_publication — linha 182

~~~~text

    Envia os METADADOS do quadrinho pra moderação/comunidade. O arquivo em
    si continua no computador do usuário — não existe upload de arquivo
    ainda (isso é um passo futuro separado, de armazenamento). Por
    enquanto file_reference é só o caminho local, útil pra rastrear qual
    arquivo originou a publicação.
    
~~~~

## panel_client/session_store.py

### módulo — linha 1

~~~~text

Guarda a sessão (token + dados básicos do usuário) localmente, no mesmo
padrão de pasta que o resto do ComicReader.py já usa
(%APPDATA%/Panel/*.json). Assim o usuário não precisa logar de novo toda
vez que abre o app — igual funciona hoje com prefs.json.

Ausência de sessão salva = modo convidado. Nunca é tratado como erro.

~~~~

## panel_backend/accounts/models.py

### módulo — linha 1

~~~~text

Modelos de conta de usuário.

Modo convidado NÃO gera um registro aqui — "continuar como convidado"
significa simplesmente não ter usuário/token, e o ComicReader.py continua
usando o armazenamento local (JSON) que já existe hoje, sem tocar nesse
módulo. Só quem cria conta passa a existir nesta tabela.

~~~~

### SessionToken — linha 59

~~~~text

    Token opaco de sessão (não é JWT). Escolha deliberada pra v1: mais
    simples de revogar (basta apagar a linha) e não exige biblioteca
    externa de JWT. Pode ser trocado por JWT depois sem mudar o resto do
    sistema — quem consome só chama `accounts.service.get_user_by_token`.
    
~~~~

### ModeratorInvite — linha 81

~~~~text
Convite temporário; o segredo original nunca é armazenado.
~~~~

### AdminAuditLog — linha 99

~~~~text
Registro imutável das ações executadas no painel administrativo.
~~~~

## panel_backend/accounts/security.py

### módulo — linha 1

~~~~text

Hash de senha com PBKDF2-HMAC-SHA256 (só biblioteca padrão — sem bcrypt/
argon2 por enquanto pra não adicionar dependência de compilação nativa
antes de definir onde isso vai rodar). Se depois quiser trocar para
argon2/bcrypt, só este arquivo muda.

~~~~

### hash_password — linha 21

~~~~text
Retorna (hash_hex, salt_hex).
~~~~

## panel_backend/accounts/service.py

### módulo — linha 1

~~~~text

Serviço de contas — cadastro, login, validação de sessão.

Assim como o ModerationService, este é o único ponto de entrada que a
futura API (ou a tela de login do ComicReader.py, via panel_client/)
deveria chamar. Ninguém fora daqui deveria fazer query direta nas tabelas
de User/SessionToken.

~~~~

## panel_backend/api/app.py

### módulo — linha 1

~~~~text

Ponto de entrada da API. Rodar localmente com:

    uvicorn panel_backend.api.app:app --reload

Isso sobe em http://localhost:8000 — que é exatamente o default que
panel_client/api_client.py já espera (troque via variável de ambiente
PANEL_API_BASE_URL dos dois lados se for rodar em outro endereço).

~~~~

## panel_backend/api/deps.py

### módulo — linha 1

~~~~text

Dependências injetadas nas rotas via FastAPI Depends(). Centralizar aqui
evita cada rota reimplementar "como pegar uma sessão de banco" ou "como
validar o token" do próprio jeito.

~~~~

### get_current_user — linha 34

~~~~text

    Uso: `user: User = Depends(get_current_user)` em qualquer rota.
    O FastAPI resolve get_db() automaticamente por baixo — não precisa
    passar db manualmente.
    
~~~~

## panel_backend/api/routes/auth.py

### me — linha 39

~~~~text
Valida a sessão e devolve o usuário atualmente autenticado.
~~~~

### claim_moderator — linha 55

~~~~text
Eleva moderador a administrador; o token mestre cria/recupera o dono.
~~~~

### logout — linha 127

~~~~text

    Idempotente de propósito: mesmo com token ausente/já inválido, retorna
    204 em vez de erro — do ponto de vista do cliente, "sair" sempre deu
    certo (a sessão local é apagada de qualquer forma).
    
~~~~

## panel_backend/api/routes/publications.py

### submit — linha 182

~~~~text

    Requer conta (modo convidado não pode publicar na comunidade — só
    usar o leitor/biblioteca local). O status retornado nunca é uma
    garantia jurídica, só o resultado da triagem — ver
    panel_backend/moderation/models.py:ModerationResult.public_message().
    
~~~~

### discovery — linha 216

~~~~text

    Pública, sem autenticação — mas só retorna o que passou pela
    moderação com status 'approved'. Esta é a ÚNICA query que deveria
    alimentar a futura página de descoberta; nunca listar Publication
    direto sem esse filtro.
    
~~~~

## panel_backend/api/schemas.py

### módulo — linha 1

~~~~text

Contratos de entrada/saída da API. Mantidos separados das rotas
propositalmente — dá pra ver o "contrato público" da API inteiro num
único arquivo, sem precisar ler lógica de negócio junto.

~~~~

## panel_backend/catalog/assets.py

### módulo — linha 1

~~~~text
Armazenamento e validação dos arquivos enviados à comunidade.
~~~~

## panel_backend/catalog/models.py

### módulo — linha 1

~~~~text

Comic: metadados de um quadrinho enviado por um usuário.
Publication: o "ato" de tornar um Comic visível na comunidade — carrega
o status vindo da moderação. Um Comic pode existir sem Publication (ex:
está só na biblioteca pessoal do usuário, nunca foi enviado à comunidade).

moderation_record_id aponta para a trilha de auditoria persistida no mesmo
banco pela camada de moderação. A coluna permanece string para manter o
catálogo desacoplado da implementação do armazenamento.

~~~~

### is_visible_to_community — linha 77

~~~~text
Única checagem que a futura página de descoberta deveria usar.
~~~~

## panel_backend/catalog/service.py

### módulo — linha 1

~~~~text

Aqui é onde o fluxo completo se encontra:

    Usuário → Upload → Análise de moderação → Aprovação/Revisão → Publicação

`submit_publication()` é a única função que a futura rota de upload da API
deveria chamar. Ela:
  1. Cria o registro do Comic
  2. Monta a submissão de moderação a partir dos dados do Comic + usuário
  3. Chama o ModerationService (já pronto, sistema anterior)
  4. Guarda o risco sugerido pelo analisador
  5. Envia toda publicação para decisão humana antes de torná-la pública

~~~~

### SubmissionInput — linha 28

~~~~text
O que a UI (tela de publicação) precisa coletar do usuário.
~~~~

## panel_backend/db.py

### módulo — linha 1

~~~~text

Configuração central do banco. SQLite por padrão (zero-config, arquivo
local) — troque PANEL_DATABASE_URL por uma URL Postgres quando o projeto
for hospedado de verdade. Nenhum outro módulo deveria abrir conexão
diretamente; todos usam `get_session()` / `init_db()` daqui.

~~~~

### init_db — linha 33

~~~~text
Cria as tabelas que ainda não existem. Chame uma vez na subida da API.
~~~~

### _migrate_legacy_schema — linha 45

~~~~text
Migrações mínimas para bancos locais criados antes dos papéis.

    O projeto ainda não usa Alembic; esta alteração aditiva mantém o banco
    existente utilizável sem apagar contas.
    
~~~~

## panel_backend/demo_full_flow.py

### módulo — linha 1

~~~~text

Demonstração do fluxo completo: cadastro -> login -> envio de quadrinho
-> moderação -> publicação. Rode com:

    python -m panel_backend.demo_full_flow

Usa SQLite local (panel.db, criado na primeira execução) e o JSON de
moderação (_demo_moderation_records.json). Apague os dois se quiser
recomeçar do zero.

~~~~

## panel_backend/migrate_legacy_assets.py

### módulo — linha 1

~~~~text
Importa caminhos locais das primeiras versões para o storage seguro.
~~~~

## panel_backend/moderation/analyzers/ai_analyzer.py

### módulo — linha 1

~~~~text

Esqueleto do futuro analisador baseado em IA externa (visão computacional,
comparação de capa, análise de texto extraído, etc.).

Propositalmente NÃO implementado ainda — o pedido original foi priorizar
a arquitetura antes de uma solução complexa. Isso aqui existe para provar
que o encaixe funciona: quando alguém implementar `_call_provider`, nada
no resto do sistema (service.py, rotas da API) precisa mudar.

Nunca coloque chaves de API aqui no código. Elas vêm de variável de
ambiente (ver panel_backend/moderation/config.py).

~~~~

## panel_backend/moderation/analyzers/base.py

### módulo — linha 1

~~~~text

Contrato que todo analisador de risco precisa seguir.

A ideia central do ponto 8 do pedido original: o ModerationService nunca
sabe COMO um analisador decide algo — só chama `.analyze(submission)` e
recebe um AnalyzerFinding de volta. Isso permite:

  - trocar o analisador de regras por um baseado em IA sem tocar no service
  - rodar vários analisadores em paralelo e combinar os resultados
  - desligar um analisador problemático sem quebrar os outros

~~~~

### BaseAnalyzer — linha 21

~~~~text
Toda nova forma de analisar risco (regras, IA, comparação de hash, etc.) implementa isso.
~~~~

### analyze — linha 28

~~~~text

        Recebe os dados da submissão e retorna UM finding.
        Nunca deve lançar exceção por "achar" risco — isso é modelado no
        próprio retorno (risk_level). Exceções devem ser reservadas para
        falhas reais (ex: analisador externo fora do ar).
        
~~~~

### is_available — linha 37

~~~~text

        Permite ao analisador se auto-desabilitar (ex: falta variável de
        ambiente com chave de API). O service deve pular analisadores
        indisponíveis em vez de derrubar toda a triagem.
        
~~~~

## panel_backend/moderation/analyzers/metadata_rules.py

### módulo — linha 1

~~~~text

Analisador v1: regras simples sobre metadados, sem IA e sem visão
computacional. É o que o pedido original chamou de "não implementar algo
extremamente complexo na primeira versão".

O que ele checa:
  1. Título/autor muito parecidos com uma obra conhecida (fuzzy match)
  2. Ausência de declaração de autoria/autorização
  3. Presença de licença informada (reduz risco)
  4. Metadados embutidos no arquivo (ex: campo "Publisher" de ComicInfo.xml)
     batendo com editoras conhecidas

Isso é deliberadamente simples — o objetivo é ter uma triagem honesta e
auditável no dia 1, não um sistema que "parece" inteligente mas na
prática é uma caixa-preta.

~~~~

## panel_backend/moderation/config.py

### módulo — linha 1

~~~~text

Configuração do módulo de moderação.

Regra do ponto 9 do pedido original: nenhuma chave de API no código-fonte.
Tudo vem de variável de ambiente. Em desenvolvimento local, use um arquivo
`.env` (não versionado — adicione ao .gitignore) e carregue com
`python-dotenv`, ou exporte as variáveis no terminal antes de rodar.

~~~~

## panel_backend/moderation/db_models.py

### módulo — linha 1

~~~~text
Modelo SQL da trilha de auditoria da moderação.
~~~~

## panel_backend/moderation/demo.py

### módulo — linha 1

~~~~text

Demonstração manual do fluxo de moderação. Rode com:
    python -m panel_backend.moderation.demo

Não é um teste automatizado formal (isso viria depois, com pytest) —
serve só para você ver o sistema funcionando de ponta a ponta e revisar
se as decisões fazem sentido antes de integrar ao resto do backend.

~~~~

## panel_backend/moderation/known_works.py

### módulo — linha 1

~~~~text

Base de "obras conhecidas" usada para comparar título/autor da submissão.

ATENÇÃO: a lista `_SEED_KNOWN_WORKS` abaixo é só um EXEMPLO MÍNIMO para a
triagem não ficar totalmente cega no dia 1. Ela está longe de ser uma
lista real de obras protegidas — não use isso como base jurídica de nada.
Em produção, isso deveria vir de uma fonte mantida (arquivo de config
carregado externamente, ou serviço de terceiros), nunca hardcoded no
código-fonte igual está aqui na v1.

~~~~

### KnownWorksRepository — linha 40

~~~~text

    Interface simples de leitura. Troca de fonte de dados (arquivo local
    -> banco -> serviço externo) não deve exigir mudanças no analisador
    que a consome.
    
~~~~

### from_env_or_seed — linha 51

~~~~text

        Carrega de um JSON externo se KNOWN_WORKS_FILE estiver definido;
        cai para a lista-semente caso contrário.
        
~~~~

### best_match — linha 71

~~~~text

        Retorna a obra conhecida mais parecida com `text` e a similaridade
        (0.0-1.0), ou None se a lista estiver vazia. Comparação simples por
        string — suficiente para uma v1, não é reconhecimento semântico.
        
~~~~

## panel_backend/moderation/models.py

### módulo — linha 1

~~~~text

Modelos de dados do sistema de moderação.

Este módulo define apenas estruturas de dados (sem lógica de negócio).
A lógica de decisão vive em `service.py` e nos analisadores em `analyzers/`.

~~~~

### ModerationStatus — linha 17

~~~~text

    Status final de uma publicação após a triagem.

    IMPORTANTE: nenhum desses status representa uma conclusão jurídica.
    'approved' significa apenas "baixo risco identificado pela triagem
    automática", nunca "confirmado como legal".
    
~~~~

### PublicationSubmission — linha 37

~~~~text

    Dados enviados pelo usuário ao tentar publicar um quadrinho.
    Isso é o "input" da moderação — nada aqui é gerado pelo sistema.
    
~~~~

### AnalyzerFinding — linha 63

~~~~text

    Resultado de UM analisador individual (ver analyzers/base.py).
    O ModerationService combina vários findings num ModerationResult.
    
~~~~

### ModerationResult — linha 76

~~~~text

    Resultado final e consolidado da triagem — o que o resto do sistema usa.
    
~~~~

### public_message — linha 88

~~~~text

        Mensagem segura para mostrar ao usuário final.
        NUNCA usar internal_justification diretamente na UI — ela pode
        conter linguagem técnica que soa como veredito jurídico.
        
~~~~

## panel_backend/moderation/service.py

### módulo — linha 1

~~~~text

ModerationService: ponto único de entrada do sistema de moderação.

Este é o único módulo que o resto do backend (rota de upload/publicação)
deveria importar. Ele:
  1. Roda todos os analisadores disponíveis sobre a submissão
  2. Combina os achados num único resultado
  3. Decide o status final (approved / pending_review / rejected)
  4. Persiste o registro para histórico/futura revisão manual
  5. Nunca decide "isto é ilegal" — só classifica risco (ver ModerationResult.public_message)

~~~~

## panel_backend/moderation/storage.py

### módulo — linha 1

~~~~text

Guarda o histórico de decisões de moderação — necessário desde já para
viabilizar (no futuro) revisão manual, denúncias e apelações (ponto 7 do
pedido original), mesmo que essas features ainda não existam.

A API usa SqlAlchemyModerationStore para manter a decisão na mesma transação
da publicação. JsonModerationStore continua disponível para demos e para
ler dados legados criados pelas primeiras versões.

~~~~

### ModerationRecord — linha 31

~~~~text
Uma decisão de moderação, associada a uma publicação, com histórico.
~~~~

### effective_status — linha 46

~~~~text
Status que deve valer de fato — revisão manual tem prioridade.
~~~~

### ModerationStore — linha 68

~~~~text

    Interface mínima de persistência. `JsonModerationStore` é a
    implementação v1; troque por uma baseada em banco depois sem alterar
    quem consome (`ModerationService`).
    
~~~~

### SqlAlchemyModerationStore — linha 85

~~~~text
Persistência transacional usada pela API.
~~~~
