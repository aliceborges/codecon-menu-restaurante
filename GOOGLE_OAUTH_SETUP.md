# Guia: Configurar Login com Google OAuth

## 🎯 Visão Geral

Este guia explica como configurar o login com Google no cardápio digital.

---

## 📋 Passo a Passo

### 1. Acessar Google Cloud Console

Acesse: **https://console.cloud.google.com/**

Faça login com sua conta Google.

---

### 2. Criar um Projeto

1. Clique no seletor de projetos (canto superior esquerdo)
2. Clique em **"Novo Projeto"**
3. Digite o nome: `Cardapio Digital` (ou qualquer nome)
4. Clique em **"Criar"**

```
┌─────────────────────────────────────┐
│  ➕ NOVO PROJETO                     │
│                                     │
│  Nome do projeto:                   │
│  [ Cardapio Digital        ]        │
│                                     │
│  Localização: [ Sem organização ▼ ] │
│                                     │
│  [ CANCELAR ]  [  CRIAR  ]          │
└─────────────────────────────────────┘
```

---

### 3. Habilitar API Google OAuth

1. No menu lateral, vá em **"APIs e Serviços"** → **"Visão Geral"**
2. Clique em **"+ Habilitar APIs e Serviços"**
3. Pesquise por: **"Google+ API"** ou **"Google Identity Toolkit"**
4. Clique em **"Habilitar"**

---

### 4. Configurar Tela de Consentimento OAuth

1. No menu lateral, vá em **"APIs e Serviços"** → **"Tela de consentimento OAuth"**
2. Selecione **"Externo"** (disponível para qualquer usuário)
3. Clique em **"Criar"**

```
┌─────────────────────────────────────┐
│  TIPO DE USUÁRIO                    │
│                                     │
│  ○ Interno (apenas para sua org)    │
│  ● Externo (qualquer usuário Google)│
│                                     │
│              [ CRIAR ]              │
└─────────────────────────────────────┘
```

4. Preencha as informações:
   - **Nome do app**: `Boi na Brasa` (ou nome do restaurante)
   - **E-mail de suporte**: seu email
   - **Logo**: (opcional) faça upload de uma imagem
   - **E-mail de contato**: seu email

5. Clique em **"Salvar e Continuar"**

6. Em **"Escopos"**, clique em **"Adicionar ou Remover Escopos"**
   - Adicione:
     - `.../auth/userinfo.email`
     - `.../auth/userinfo.profile`
   - Clique em **"Atualizar"** → **"Salvar e Continuar"**

7. Em **"Usuários de teste"**, clique em **"Adicionar Usuários"**
   - Adicione seu email Google
   - Clique em **"Salvar e Continuar"**

8. Clique em **"Voltar para Painel"**

---

### 5. Criar Credenciais (Client ID e Secret)

1. No menu lateral, vá em **"APIs e Serviços"** → **"Credenciais"**
2. Clique em **"+ Criar Credenciais"** → **"ID do Cliente OAuth"**

```
┌─────────────────────────────────────┐
│  CRIAR CREDENCIAIS                  │
│                                     │
│  ▸ Chave da API                     │
│  ▸ ID do cliente OAuth              │
│  ▸ Conta de serviço                 │
│  ▸ ID da conta de serviço           │
│                                     │
└─────────────────────────────────────┘
```

3. Configure o aplicativo:
   - **Tipo de aplicativo**: `Aplicativo da Web`
   - **Nome**: `Cardapio Web`

4. Em **"URI de redirecionamento autorizados"**, clique em **"Adicionar URI"**
   
   Adicione estas URLs:
   ```
   http://localhost:5000/auth/callback
   ```

```
┌─────────────────────────────────────────────┐
│  URIs de redirecionamento autorizados       │
│                                             │
│  URI 1: [ http://localhost:5000/auth/callback ]
│                                             │
│  [ + Adicionar URI ]                        │
└─────────────────────────────────────────────┘
```

5. Clique em **"Criar"**

6. **IMPORTANTE**: Anote os valores que aparecerão:
   - **ID do Cliente** (ex: `123456789-abc123.apps.googleusercontent.com`)
   - **Chave Secreta do Cliente** (ex: `GOCSPX-xyz789`)

```
┌─────────────────────────────────────────────┐
│  ID do Cliente                              │
│  123456789-xxxxxxxxxxxxxxxx.apps.googleusercontent.com  │
│  [ 📋 COPIAR ]                              │
│                                             │
│  Chave Secreta do Cliente                   │
│  GOCSPX-xxxxxxxxxxxxxxxxxxxx                │
│  [ 📋 COPIAR ]                              │
└─────────────────────────────────────────────┘
```

---

### 6. Configurar no Projeto

#### Opção 1: Arquivo .env (Recomendado)

Crie um arquivo `.env` na pasta do projeto:

```env
GOOGLE_CLIENT_ID=123456789-xxxxxxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxx
SECRET_KEY=uma-chave-qualquer-para-sessao
```

#### Opção 2: Variáveis de Ambiente (PowerShell)

```powershell
$env:GOOGLE_CLIENT_ID="123456789-xxxxxxxxxxxxxxxx.apps.googleusercontent.com"
$env:GOOGLE_CLIENT_SECRET="GOCSPX-xxxxxxxxxxxxxxxxxxxx"
$env:SECRET_KEY="uma-chave-qualquer"
python app.py
```

#### Opção 3: Variáveis de Ambiente (CMD)

```cmd
set GOOGLE_CLIENT_ID=123456789-xxxxxxxxxxxxxxxx.apps.googleusercontent.com
set GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxx
set SECRET_KEY=uma-chave-qualquer
python app.py
```

---

### 7. Testar

1. Execute o servidor:
```bash
python app.py
```

2. Acesse: http://localhost:5000/login

3. Clique em **"Entrar com Google"**

4. Selecione sua conta

5. Pronto! Você está logado! 🎉

---

## ⚠️ Solução de Problemas

### Erro: "redirect_uri_mismatch"

**Causa**: A URL de redirecionamento não está configurada corretamente

**Solução**:
1. Volte para Credenciais → ID do Cliente
2. Edite o cliente
3. Verifique se `http://localhost:5000/auth/callback` está nas URIs autorizadas
4. Salve

### Erro: "Error 403: access_denied"

**Causa**: Seu email não está na lista de usuários de teste

**Solução**:
1. Vá em "Tela de consentimento OAuth"
2. Adicione seu email em "Usuários de teste"
3. Aguarde alguns minutos e tente novamente

### Erro: "OAuth não configurado"

**Causa**: Variáveis de ambiente não definidas

**Solução**: Verifique se as variáveis estão definidas antes de executar o servidor:
```powershell
# PowerShell
$env:GOOGLE_CLIENT_ID
$env:GOOGLE_CLIENT_SECRET

# Se não mostrar nada, defina novamente
```

---

## 📝 Checklist

- [ ] Projeto criado no Google Cloud
- [ ] API OAuth habilitada
- [ ] Tela de consentimento configurada (Externo)
- [ ] Escopos email e profile adicionados
- [ ] Usuário de teste adicionado
- [ ] Credenciais criadas (Client ID e Secret)
- [ ] URI `http://localhost:5000/auth/callback` configurada
- [ ] Variáveis de ambiente definidas
- [ ] Servidor reiniciado

---

## 🔗 Links Úteis

- [Google Cloud Console](https://console.cloud.google.com/)
- [Documentação OAuth Google](https://developers.google.com/identity/protocols/oauth2)
