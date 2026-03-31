# Cardápio Digital - Boi na Brasa

Sistema de cardápio digital com tema de churrasco, login via Google OAuth e avaliações.

## 🚀 Instalação

```bash
pip install -r requirements.txt
```

## ⚙️ Configuração Google OAuth

Para habilitar o login com Google:

1. Acesse: https://console.cloud.google.com/
2. Crie um projeto ou selecione existente
3. Vá em "APIs e Serviços" > "Credenciais"
4. Clique em "Criar Credenciais" > "ID do Cliente OAuth"
5. Configure a tela de consentimento OAuth
6. Adicione como URI de redirecionamento autorizado:
   ```
   http://localhost:5000/auth/callback
   ```
7. Copie o Client ID e Client Secret

## 🔧 Variáveis de Ambiente

Crie um arquivo `.env` na raiz:

```env
GOOGLE_CLIENT_ID=seu_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_client_secret_aqui
SECRET_KEY=uma_chave_secreta_qualquer
```

Ou defina diretamente no terminal:

**Windows (PowerShell):**
```powershell
$env:GOOGLE_CLIENT_ID="seu_client_id"
$env:GOOGLE_CLIENT_SECRET="seu_client_secret"
```

**Linux/Mac:**
```bash
export GOOGLE_CLIENT_ID="seu_client_id"
export GOOGLE_CLIENT_SECRET="seu_client_secret"
```

## ▶️ Executar

```bash
python app.py
```

Acesse: http://localhost:5000

## 🎨 Funcionalidades

- ✅ Cardápio com horários (Almoço 11h-15h / Jantar 18h-23h)
- ✅ Login com Google OAuth
- ✅ Avaliações de restaurante e itens (requer login)
- ✅ Tema Churrasco fixo
- ✅ Pagamento via PIX ou Dinheiro
- ✅ Simulador de horário para testes (`/admin`)

## 📁 Estrutura

```
.
├── app.py              # Aplicação Flask
├── models.py           # Modelos do banco de dados
├── themes.py           # Configuração de temas
├── templates/          # Templates HTML
├── static/            # CSS e JS
├── requirements.txt   # Dependências
└── .env              # Variáveis de ambiente (não commitar)
```

## ⚠️ Importante

O arquivo `.env` e o banco de dados `*.db` estão no `.gitignore` e não devem ser commitados.
