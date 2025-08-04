# 🚀 Guia de Deploy - IA Tributária Internacional

## 📋 Pré-requisitos
- Conta no GitHub
- API Key da OpenAI válida
- Conta no Render.com (gratuita)
- Conta no Vercel (gratuita)

## 🔧 Deploy do Backend (Python) - Render.com

### 1. Preparar Repositório
```bash
# 1. Subir código para GitHub
git init
git add .
git commit -m "Deploy: IA Tributária Backend"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/ia-tributaria-backend.git
git push -u origin main
```

### 2. Deploy no Render
1. **Acesse**: https://render.com
2. **Conecte seu GitHub**
3. **Crie Web Service**
4. **Configure**:
   - **Repository**: seu-repo/ia-tributaria-backend
   - **Branch**: main
   - **Root Directory**: (deixe vazio)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python simple_server.py`

### 3. Variáveis de Ambiente
No painel do Render, adicione:
```
OPENAI_API_KEY=sk-proj-sua-key-aqui
PORT=8001
HOST=0.0.0.0
```

### 4. Deploy
- Clique **"Create Web Service"**
- Aguarde deploy (~5-10 min)
- Anote URL: `https://ia-tributaria-backend.onrender.com`

## 🎨 Deploy do Frontend (Next.js) - Vercel

### 1. Preparar Frontend
```bash
cd ia-tributaria-frontend

# Instalar Vercel CLI
npm i -g vercel
```

### 2. Configurar Variáveis
Crie arquivo `.env.production`:
```bash
NEXT_PUBLIC_API_URL=https://ia-tributaria-backend.onrender.com
PYTHON_BACKEND_URL=https://ia-tributaria-backend.onrender.com
```

### 3. Deploy
```bash
# Deploy para Vercel
vercel --prod

# Seguir prompts:
# - Project name: ia-tributaria-frontend
# - Framework: Next.js
# - Deploy: Yes
```

### 4. Configurar Domínio (Opcional)
No painel Vercel:
- **Settings** > **Domains**
- Adicionar domínio customizado

## 🔗 URLs Finais
- **Frontend**: https://ia-tributaria-frontend.vercel.app
- **Backend**: https://ia-tributaria-backend.onrender.com
- **API Docs**: https://ia-tributaria-backend.onrender.com/docs

## 💰 Custos Estimados
- **Vercel**: Gratuito (até 100GB bandwidth)
- **Render**: Gratuito por 750h/mês (depois $7/mês)
- **OpenAI**: ~$2-10/mês (dependendo do uso)
- **Total**: $0-17/mês

## 🔧 Troubleshooting

### Backend não inicia
- Verificar variáveis de ambiente
- Checar logs no Render
- Confirmar requirements.txt

### Frontend não conecta
- Verificar NEXT_PUBLIC_API_URL
- Checar CORS no backend
- Testar endpoints da API

### OpenAI não funciona
- Verificar API key válida
- Checar billing na OpenAI
- Confirmar limits não excedidos

## 📊 Monitoramento
- **Render**: Logs em tempo real
- **Vercel**: Analytics integrado
- **OpenAI**: Usage dashboard

---

🎉 **Seu sistema estará online e acessível globalmente!**