# Prompt Resumido - Teste Rápido MCP CrowdStrike na VPS

**Para Claude na VPS**: Execute estes comandos para testar o MCP CrowdStrike.

---

## 🎯 Teste SEM Credenciais (3 minutos)

```bash
# 1. Instalar pré-requisitos
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip git

# 2. Clonar e configurar
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/fjopereira/MCP.git
cd MCP

# 3. Criar ambiente e instalar
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .

# 4. EXECUTAR TESTE DEMO (SEM CREDENCIAIS!)
python test_demo_mode.py
```

**Resultado Esperado**:
```
✅ DEMONSTRAÇÃO COMPLETA!
🎯 Todas as 9 ferramentas funcionando perfeitamente!
```

---

## ✅ O que Este Teste Faz?

- Testa **TODAS as 9 ferramentas** CrowdStrike
- Usa dados **SIMULADOS** (não precisa credenciais)
- Valida a instalação completa
- **NÃO** se conecta ao CrowdStrike real

---

## 🔐 Teste com Credenciais Reais (Opcional)

**SOMENTE se tiver credenciais CrowdStrike**:

```bash
# 1. Editar arquivo de teste
cd ~/projects/MCP
source .venv/bin/activate
nano test_sdk_example.py

# 2. Nas linhas 22-23, colar suas credenciais:
# client_id = "SEU_CLIENT_ID"
# client_secret = "SEU_CLIENT_SECRET"

# Salvar: Ctrl+O, Enter, Ctrl+X

# 3. Executar teste com dados REAIS
python test_sdk_example.py
```

---

## 🐳 Deploy Docker (Produção)

**SOMENTE se precisar de servidor em produção**:

```bash
# 1. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
sudo apt install docker-compose-plugin -y

# 2. Configurar credenciais
cd ~/projects/MCP
cp .env.example .env
nano .env
# Editar com suas credenciais e salvar

# 3. Build e deploy
cd docker
docker compose build
docker compose up -d

# 4. Verificar
sleep 30
curl http://localhost:8001/health
curl http://localhost:8001/ready
```

---

## 📊 Comandos Úteis

```bash
# Ver logs do demo
cd ~/projects/MCP
source .venv/bin/activate
python test_demo_mode.py

# Ver logs do Docker
cd ~/projects/MCP/docker
docker compose logs -f

# Status do container
docker compose ps

# Reiniciar servidor
docker compose restart
```

---

## ❓ Problemas?

### Demo não funciona:
```bash
# Reinstalar
cd ~/projects/MCP
source .venv/bin/activate
pip install -e .
python test_demo_mode.py
```

### Docker não inicia:
```bash
cd ~/projects/MCP/docker
docker compose logs
docker compose restart
```

---

## ✨ Recomendação

**Execute SEMPRE o modo demo primeiro**:
- ✅ Valida instalação
- ✅ Não precisa credenciais
- ✅ Teste rápido (2-3 min)

**Só use credenciais reais SE**:
- Modo demo funcionou
- Você tem as credenciais
- Precisa testar dados reais

---

**Repositório**: https://github.com/fjopereira/MCP
**Documentação**: Ver `DEMO_MODE.md` e `README.md` no repo

---

**Comece com**: `python test_demo_mode.py` 🚀
