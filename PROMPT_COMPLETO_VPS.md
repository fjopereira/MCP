# Prompt Completo para Instalação e Teste do MCP CrowdStrike na VPS

**ATENÇÃO**: Este é o prompt COMPLETO e ATUALIZADO para instalação do MCP Server for CrowdStrike Falcon em uma VPS Linux. Copie e cole este prompt completo para o Claude na VPS.

---

## 📋 CONTEXTO DO PROJETO

Você precisa instalar e configurar o **MCP Server for CrowdStrike Falcon** em uma VPS Linux. Este é um projeto de produção que integra a API do CrowdStrike Falcon através do Model Context Protocol (MCP).

### Informações do Projeto:
- **Repositório GitHub**: https://github.com/fjopereira/MCP.git
- **Autor**: Fábio Pereira
- **Tecnologias**: Python 3.11+, FastAPI, Docker, CrowdStrike FalconPy
- **Modo de Deploy**: Docker Compose (produção) + Python SDK

### O que o projeto faz:
- Servidor MCP que expõe 9 ferramentas da API CrowdStrike Falcon
- **Dual-mode**: Funciona como servidor Docker OU SDK Python
- **Modo Demo**: Testa SEM credenciais usando dados simulados
- 4 ferramentas de gerenciamento de hosts (incluindo containment)
- 3 ferramentas de gerenciamento de detecções
- 2 ferramentas de gerenciamento de incidentes

---

## 🎯 NOVIDADE: TESTE SEM CREDENCIAIS (MODO DEMO)

**IMPORTANTE**: Agora você pode testar o projeto **SEM precisar de credenciais CrowdStrike!**

O projeto inclui um **Modo Demonstração** que simula todas as funcionalidades com dados realistas.

### Quando usar cada modo:

| Modo | Credenciais | Internet | Dados | Uso |
|------|-------------|----------|-------|-----|
| **Demo** | ❌ NÃO precisa | ❌ NÃO precisa | Simulados | Teste/Demo |
| **SDK Real** | ✅ Precisa | ✅ Precisa | Reais | Desenvolvimento |
| **Server (Docker)** | ✅ Precisa | ✅ Precisa | Reais | Produção |

---

## 🚀 OPÇÃO 1: TESTE RÁPIDO SEM CREDENCIAIS (RECOMENDADO PRIMEIRO)

Execute esta opção PRIMEIRO para validar a instalação antes de usar credenciais reais.

### ETAPA 1: Instalar Pré-requisitos Básicos

```bash
# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar Python 3.11+ (se não tiver)
sudo apt install python3.11 python3.11-venv python3-pip git -y

# 3. Verificar versão do Python
python3 --version
# Deve mostrar Python 3.11 ou superior
```

### ETAPA 2: Clonar e Configurar o Projeto

```bash
# 1. Criar diretório para projetos
mkdir -p ~/projects
cd ~/projects

# 2. Clonar repositório
git clone https://github.com/fjopereira/MCP.git
cd MCP

# 3. Verificar arquivos
ls -la
# Deve ver: src/, docker/, tests/, README.md, etc.
```

### ETAPA 3: Executar Modo Demo (SEM Credenciais)

```bash
# 1. Criar ambiente virtual Python
python3 -m venv .venv

# 2. Ativar ambiente virtual
source .venv/bin/activate

# 3. Instalar dependências
pip install --upgrade pip
pip install -e .

# 4. Executar teste DEMO (SEM CREDENCIAIS!)
python test_demo_mode.py
```

**VERIFICAÇÃO**: Você deve ver saída como:

```
======================================================================
🎯 MCP CROWDSTRIKE - MODO DEMONSTRAÇÃO (SEM CREDENCIAIS)
======================================================================

✨ Este teste usa dados SIMULADOS - não precisa de credenciais reais!

📱 TESTE 1: Consultando Dispositivos (Hosts)
----------------------------------------------------------------------
✓ Sucesso! Encontrados 3 dispositivos (simulados)
  Device IDs: ['mock-device-001', 'mock-device-002', 'mock-device-003']

[... testa todas as 9 ferramentas ...]

✅ DEMONSTRAÇÃO COMPLETA!
🎯 Todas as 9 ferramentas funcionando perfeitamente!
```

**SE ESTE TESTE FUNCIONAR**: ✅ A instalação está correta!
**SE FALHAR**: ❌ Há problema na instalação - veja logs de erro.

---

## 🔐 OPÇÃO 2: TESTE COM CREDENCIAIS REAIS (OPCIONAL)

**SOMENTE execute esta opção SE:**
- O teste demo (Opção 1) funcionou perfeitamente
- Você tem credenciais CrowdStrike disponíveis
- Quer testar com dados reais

### Credenciais Necessárias:

1. **FALCON_CLIENT_ID**: Seu Client ID da API CrowdStrike
2. **FALCON_CLIENT_SECRET**: Seu Client Secret da API CrowdStrike
3. **FALCON_BASE_URL** (opcional): URL da região da API
   - US-1 (padrão): `https://api.crowdstrike.com`
   - US-2: `https://api.us-2.crowdstrike.com`
   - EU-1: `https://api.eu-1.crowdstrike.com`
   - US-GOV-1: `https://api.laggar.gcw.crowdstrike.com`

**SE VOCÊ NÃO TEM AS CREDENCIAIS**: PARE AQUI. O teste demo (Opção 1) já validou tudo!

### ETAPA 1: Teste SDK com Credenciais (Python)

```bash
# 1. Ainda no diretório ~/projects/MCP
cd ~/projects/MCP

# 2. Ambiente virtual deve estar ativo
source .venv/bin/activate

# 3. Editar arquivo de teste
nano test_sdk_example.py

# 4. No editor nano, vá até as linhas 22-23 e cole suas credenciais:
# client_id = "COLE_SEU_CLIENT_ID_AQUI"
# client_secret = "COLE_SEU_CLIENT_SECRET_AQUI"

# Salvar: Ctrl+O, Enter, Ctrl+X

# 5. Executar teste com credenciais REAIS
python test_sdk_example.py
```

**VERIFICAÇÃO**: Você deve ver dados REAIS da sua organização CrowdStrike.

**SE FALHAR COM ERRO 401**: Credenciais inválidas ou URL incorreta.
**SE FALHAR COM ERRO DE REDE**: Verificar conectividade com CrowdStrike.

---

## 🐳 OPÇÃO 3: DEPLOY PRODUÇÃO (DOCKER) - SOMENTE SE TIVER CREDENCIAIS

**IMPORTANTE**: Esta opção é para deployment em PRODUÇÃO e **REQUER credenciais reais**.

**Execute SOMENTE SE:**
- Você tem credenciais CrowdStrike
- Quer rodar como servidor (não apenas SDK)
- Precisa de acesso via HTTP/API

### PRÉ-REQUISITO: Instalar Docker

```bash
# 1. Verificar se Docker está instalado
docker --version

# SE NÃO ESTIVER INSTALADO:

# 2. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# 4. Aplicar mudanças (fazer logout/login ou executar)
newgrp docker

# 5. Instalar Docker Compose plugin
sudo apt install docker-compose-plugin -y

# 6. Verificar instalações
docker --version
docker compose version
```

### ETAPA 1: Configurar Credenciais

```bash
# 1. Navegar para o diretório do projeto
cd ~/projects/MCP

# 2. Copiar template de configuração
cp .env.example .env

# 3. Editar arquivo .env
nano .env

# 4. No editor, configure (SUBSTITUA com suas credenciais reais):

FALCON_CLIENT_ID=COLE_SEU_CLIENT_ID_AQUI
FALCON_CLIENT_SECRET=COLE_SEU_CLIENT_SECRET_AQUI
FALCON_BASE_URL=https://api.crowdstrike.com
SERVER_HOST=0.0.0.0
SERVER_PORT=8001
LOG_LEVEL=INFO
ENVIRONMENT=production

# Salvar: Ctrl+O, Enter, Ctrl+X

# 5. Proteger arquivo .env
chmod 600 .env

# 6. Verificar (sem mostrar secrets)
cat .env | grep -v SECRET
```

### ETAPA 2: Build e Deploy Docker

```bash
# 1. Ir para diretório docker
cd ~/projects/MCP/docker

# 2. Build da imagem (pode levar 2-5 minutos)
docker compose build

# 3. Verificar imagem criada
docker images | grep mcp-crowdstrike

# 4. Iniciar container em background
docker compose up -d

# 5. Aguardar 30 segundos para inicializar
sleep 30

# 6. Verificar status
docker compose ps
```

### ETAPA 3: Verificar Health Checks

```bash
# 1. Testar health check
curl http://localhost:8001/health
# Esperado: {"status":"healthy","environment":"production"}

# 2. Testar readiness (conexão CrowdStrike)
curl http://localhost:8001/ready
# Esperado: {"ready":true,"provider_healthy":true}

# 3. Listar ferramentas disponíveis
curl http://localhost:8001/mcp/v1/tools | jq .
# Esperado: Lista com 9 ferramentas

# 4. Testar endpoint raiz
curl http://localhost:8001/
# Esperado: Informações da API
```

**SE HEALTH CHECK FALHAR**:

```bash
# Ver logs
docker compose logs

# Ver logs específicos do container
docker compose logs mcp-crowdstrike

# Reiniciar container
docker compose restart

# Ver status detalhado
docker compose ps
docker inspect mcp-crowdstrike-server
```

### ETAPA 4: Teste Funcional (Opcional)

```bash
# Testar query de dispositivos reais
curl -X POST http://localhost:8001/mcp/v1/tools/query_devices_by_filter \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"limit": 5}}' | jq .

# Esperado: Lista de device IDs reais da sua organização
```

---

## 📊 COMANDOS ÚTEIS

### Para Modo Demo:

```bash
# Executar demo novamente
cd ~/projects/MCP
source .venv/bin/activate
python test_demo_mode.py
```

### Para Modo SDK (Python):

```bash
# Testar SDK com credenciais
cd ~/projects/MCP
source .venv/bin/activate
python test_sdk_example.py
```

### Para Modo Server (Docker):

```bash
cd ~/projects/MCP/docker

# Ver logs
docker compose logs -f

# Ver status
docker compose ps

# Parar servidor
docker compose stop

# Iniciar servidor
docker compose start

# Reiniciar servidor
docker compose restart

# Parar e remover container
docker compose down

# Reconstruir imagem
docker compose build

# Ver estatísticas
docker stats mcp-crowdstrike-server
```

---

## 🔧 CONFIGURAÇÃO DE FIREWALL (SE NECESSÁRIO)

**SOMENTE se quiser acessar de fora da VPS**:

```bash
# Verificar UFW
sudo ufw status

# Permitir porta 8001 (se UFW ativo)
sudo ufw allow 8001/tcp

# Verificar regra
sudo ufw status numbered
```

**⚠️ SEGURANÇA**: Para produção real, use reverse proxy (Nginx/Caddy) com SSL/TLS.

---

## 🔍 TROUBLESHOOTING

### Problema: Modo demo não funciona

```bash
# Verificar instalação Python
python3 --version

# Verificar ambiente virtual ativo
which python
# Deve mostrar: /home/user/projects/MCP/.venv/bin/python

# Reinstalar dependências
pip install -e .

# Ver logs de erro
python test_demo_mode.py 2>&1 | tee demo_error.log
```

### Problema: Credenciais inválidas (erro 401)

```bash
# Verificar credenciais no .env
cat .env | grep FALCON

# Verificar conectividade com CrowdStrike
curl -I https://api.crowdstrike.com

# Testar URL base correta para sua região
# US-1: https://api.crowdstrike.com
# US-2: https://api.us-2.crowdstrike.com
# EU-1: https://api.eu-1.crowdstrike.com
```

### Problema: Container não inicia

```bash
# Ver logs completos
docker compose logs

# Ver erro específico
docker compose logs | grep -i error

# Verificar porta em uso
sudo netstat -tulpn | grep 8001

# Remover container e recriar
docker compose down
docker compose up -d
```

### Problema: Health check falha

```bash
# Ver logs em tempo real
docker compose logs -f

# Verificar se container está rodando
docker compose ps

# Reiniciar container
docker compose restart

# Aguardar 30-40 segundos e testar novamente
sleep 40
curl http://localhost:8001/health
```

---

## ✅ CHECKLIST DE VERIFICAÇÃO

### Após Modo Demo (Opção 1):
- [ ] Python 3.11+ instalado
- [ ] Repositório clonado do GitHub
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -e .`)
- [ ] `python test_demo_mode.py` executado com sucesso
- [ ] Viu todas as 9 ferramentas funcionando
- [ ] Nenhum erro crítico nos logs

### Após Teste SDK (Opção 2) - SE TIVER CREDENCIAIS:
- [ ] Credenciais CrowdStrike configuradas
- [ ] `test_sdk_example.py` executado com sucesso
- [ ] Recebeu dados reais da organização
- [ ] Nenhum erro 401 (autenticação)

### Após Deploy Docker (Opção 3) - SE TIVER CREDENCIAIS:
- [ ] Docker e Docker Compose instalados
- [ ] Arquivo `.env` criado com credenciais
- [ ] Imagem Docker construída (~180-200MB)
- [ ] Container rodando com status `healthy`
- [ ] Health check retorna `{"status":"healthy"}`
- [ ] Readiness check retorna `{"ready":true,"provider_healthy":true}`
- [ ] Endpoint `/mcp/v1/tools` lista 9 ferramentas
- [ ] Container configurado para reinício automático

---

## 📚 INFORMAÇÕES ADICIONAIS

### Arquivos Importantes no Projeto:

- **`test_demo_mode.py`** - Teste SEM credenciais (RECOMENDADO PRIMEIRO)
- **`test_sdk_example.py`** - Teste COM credenciais reais
- **`DEMO_MODE.md`** - Documentação completa do modo demo
- **`PARA_TESTAR.md`** - Guia rápido de teste
- **`VPS_DEPLOYMENT_PROMPT.md`** - Deployment em produção
- **`README.md`** - Documentação completa do projeto

### URLs Úteis:

- **Repositório**: https://github.com/fjopereira/MCP
- **Demo Mode**: https://github.com/fjopereira/MCP/blob/master/DEMO_MODE.md
- **Quick Test**: https://github.com/fjopereira/MCP/blob/master/PARA_TESTAR.md

---

## 🎯 RECOMENDAÇÃO DE EXECUÇÃO

**Execute NESTA ORDEM**:

### 1️⃣ PRIMEIRO: Modo Demo (SEMPRE)
```bash
cd ~/projects/MCP
source .venv/bin/activate
python test_demo_mode.py
```
**✅ Valida**: Instalação, dependências, código funcionando

### 2️⃣ SEGUNDO: SDK Real (SE TIVER CREDENCIAIS)
```bash
# Editar test_sdk_example.py com credenciais
python test_sdk_example.py
```
**✅ Valida**: Credenciais, conectividade, API CrowdStrike

### 3️⃣ TERCEIRO: Docker Deploy (SE QUISER SERVIDOR)
```bash
cd docker
docker compose up -d
curl http://localhost:8001/health
```
**✅ Valida**: Deploy produção, servidor funcionando

---

## 🎉 RESULTADO ESPERADO

### Após Modo Demo:
```
✅ Todas as 9 ferramentas testadas
✅ Instalação validada
✅ Código funcionando
✅ PRONTO para usar (com ou sem credenciais)
```

### Após SDK Real (opcional):
```
✅ Conexão com CrowdStrike OK
✅ Credenciais válidas
✅ Dados reais recebidos
✅ PRONTO para desenvolvimento
```

### Após Docker Deploy (opcional):
```
✅ Servidor rodando em http://localhost:8001
✅ Health checks passando
✅ API REST funcionando
✅ PRONTO para produção
```

---

## 💡 DICA IMPORTANTE

**Comece SEMPRE com o Modo Demo** (Opção 1):
- ✅ Não precisa de credenciais
- ✅ Teste rápido (2-3 minutos)
- ✅ Valida toda instalação
- ✅ Sem riscos de segurança

**Só passe para as outras opções SE**:
- O modo demo funcionou perfeitamente
- Você tem credenciais disponíveis
- Você realmente precisa testar com dados reais

---

## 📞 SUPORTE

Se encontrar problemas:

1. **Verifique os logs**: Sempre leia as mensagens de erro
2. **Consulte troubleshooting**: Seção acima tem soluções comuns
3. **Veja documentação**: README.md e DEMO_MODE.md têm detalhes
4. **Issues GitHub**: https://github.com/fjopereira/MCP/issues

---

## ✨ RESUMO EXECUTIVO

**3 Comandos para Testar SEM Credenciais**:

```bash
git clone https://github.com/fjopereira/MCP.git
cd MCP && python3 -m venv .venv && source .venv/bin/activate && pip install -e .
python test_demo_mode.py
```

**Status**: Projeto 100% funcional com modo demo!

---

**BOA SORTE COM O TESTE E INSTALAÇÃO!** 🚀

Execute o Modo Demo primeiro - você vai se impressionar! ✨
