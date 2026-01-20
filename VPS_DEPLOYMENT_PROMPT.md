# Prompt para Instalação do MCP CrowdStrike na VPS Linux

**ATENÇÃO**: Este é um prompt completo e detalhado para instalação do MCP Server for CrowdStrike Falcon em uma VPS Linux. Copie e cole este prompt completo para o Claude na VPS.

---

## CONTEXTO DO PROJETO

Você precisa instalar e configurar o **MCP Server for CrowdStrike Falcon** em uma VPS Linux. Este é um projeto de produção que integra a API do CrowdStrike Falcon através do Model Context Protocol (MCP).

### Informações do Projeto:
- **Repositório GitHub**: https://github.com/fjopereira/MCP.git
- **Autor**: Fábio Pereira
- **Tecnologias**: Python 3.11+, FastAPI, Docker, CrowdStrike FalconPy
- **Modo de Deploy**: Docker Compose (produção)

### O que o projeto faz:
- Servidor MCP que expõe 9 ferramentas da API CrowdStrike Falcon
- Dual-mode: Funciona como servidor Docker OU SDK Python
- 4 ferramentas de gerenciamento de hosts (incluindo containment)
- 3 ferramentas de gerenciamento de detecções
- 2 ferramentas de gerenciamento de incidentes

---

## CREDENCIAIS NECESSÁRIAS

**ANTES DE COMEÇAR**, eu preciso que você me forneça as seguintes credenciais do CrowdStrike Falcon:

1. **FALCON_CLIENT_ID**: Seu Client ID da API CrowdStrike
2. **FALCON_CLIENT_SECRET**: Seu Client Secret da API CrowdStrike
3. **FALCON_BASE_URL** (opcional): URL da região da API
   - US-1 (padrão): `https://api.crowdstrike.com`
   - US-2: `https://api.us-2.crowdstrike.com`
   - EU-1: `https://api.eu-1.crowdstrike.com`
   - US-GOV-1: `https://api.laggar.gcw.crowdstrike.com`

**POR FAVOR, FORNEÇA AS CREDENCIAIS ACIMA ANTES DE PROSSEGUIR COM A INSTALAÇÃO.**

---

## TAREFA: INSTALAÇÃO COMPLETA NA VPS

Você deve executar TODAS as etapas abaixo, na ordem especificada. Esta é uma instalação de produção, então cada passo é crítico.

### ETAPA 1: Verificar Pré-requisitos do Sistema

Execute os seguintes comandos e me informe os resultados:

```bash
# 1. Verificar sistema operacional
cat /etc/os-release

# 2. Verificar se Docker está instalado
docker --version

# 3. Verificar se Docker Compose está instalado
docker compose version

# 4. Verificar espaço em disco disponível
df -h

# 5. Verificar memória disponível
free -h

# 6. Verificar conectividade com GitHub
curl -I https://github.com

# 7. Verificar conectividade com CrowdStrike API
curl -I https://api.crowdstrike.com
```

**Se Docker ou Docker Compose NÃO estiverem instalados**, execute:

```bash
# Atualizar pacotes
sudo apt update

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker (evita precisar de sudo)
sudo usermod -aG docker $USER

# Instalar Docker Compose (plugin)
sudo apt install docker-compose-plugin -y

# Verificar instalação
docker --version
docker compose version

# IMPORTANTE: Fazer logout e login novamente para aplicar grupo docker
# Ou execute: newgrp docker
```

---

### ETAPA 2: Clonar o Repositório

```bash
# 1. Criar diretório para o projeto (se não existir)
mkdir -p ~/projects
cd ~/projects

# 2. Clonar o repositório do GitHub
git clone https://github.com/fjopereira/MCP.git

# 3. Entrar no diretório do projeto
cd MCP

# 4. Verificar estrutura do projeto
ls -la

# 5. Verificar que todos os arquivos críticos estão presentes
ls -la docker/
ls -la src/mcp_crowdstrike/
ls -la .env.example

# 6. Mostrar o branch atual
git branch
git log --oneline -5
```

**VERIFICAÇÃO**: Confirme que você vê os seguintes diretórios/arquivos:
- `docker/` (contém Dockerfile e docker-compose.yml)
- `src/mcp_crowdstrike/` (código-fonte)
- `.env.example` (template de configuração)
- `README.md` (documentação)
- `pyproject.toml` (dependências Python)

---

### ETAPA 3: Configurar Variáveis de Ambiente

```bash
# 1. Navegar para o diretório do projeto (se ainda não estiver)
cd ~/projects/MCP

# 2. Copiar o arquivo de exemplo para .env
cp .env.example .env

# 3. Editar o arquivo .env com as credenciais
nano .env
```

**Dentro do editor `nano`, configure:**

```bash
# CrowdStrike Falcon API Credentials (OBRIGATÓRIO)
FALCON_CLIENT_ID=<COLE_SEU_CLIENT_ID_AQUI>
FALCON_CLIENT_SECRET=<COLE_SEU_CLIENT_SECRET_AQUI>

# CrowdStrike API Configuration (OPCIONAL)
FALCON_BASE_URL=https://api.crowdstrike.com

# Server Configuration (OPCIONAL - padrões OK para produção)
SERVER_HOST=0.0.0.0
SERVER_PORT=8001

# Logging (OPCIONAL)
LOG_LEVEL=INFO

# Environment (OBRIGATÓRIO)
ENVIRONMENT=production
```

**IMPORTANTE**:
- Substitua `<COLE_SEU_CLIENT_ID_AQUI>` pela credencial real
- Substitua `<COLE_SEU_CLIENT_SECRET_AQUI>` pela credencial real
- Altere `FALCON_BASE_URL` se estiver em outra região (EU, US-2, etc.)
- Mantenha `ENVIRONMENT=production` para ambiente de produção

**Para salvar no nano**:
1. Pressione `Ctrl + O` (salvar)
2. Pressione `Enter` (confirmar nome do arquivo)
3. Pressione `Ctrl + X` (sair)

```bash
# 4. Verificar que o arquivo .env foi criado corretamente
cat .env | grep -v "SECRET"  # Mostra configuração sem revelar secrets

# 5. Verificar permissões do arquivo .env (deve ser privado)
ls -la .env
chmod 600 .env  # Garantir que apenas o dono pode ler/escrever
```

---

### ETAPA 4: Build da Imagem Docker

```bash
# 1. Navegar para o diretório docker
cd ~/projects/MCP/docker

# 2. Fazer build da imagem Docker (multi-stage build otimizado)
docker compose build

# Isso pode levar 2-5 minutos. Aguarde a conclusão.
```

**VERIFICAÇÃO**: Após o build, execute:

```bash
# 3. Verificar que a imagem foi criada
docker images | grep mcp-crowdstrike

# 4. Verificar tamanho da imagem (deve ser ~180-200MB)
docker images mcp-crowdstrike:latest --format "{{.Size}}"
```

**ESPERADO**: Você deve ver uma imagem chamada `mcp-crowdstrike` com tamanho aproximado de 180-200MB.

---

### ETAPA 5: Iniciar o Servidor

```bash
# 1. Ainda no diretório docker
cd ~/projects/MCP/docker

# 2. Iniciar o container em modo detached (background)
docker compose up -d

# 3. Verificar que o container está rodando
docker compose ps

# 4. Ver logs iniciais
docker compose logs

# 5. Seguir logs em tempo real (Ctrl+C para sair)
docker compose logs -f
```

**VERIFICAÇÃO**: O container deve estar com status `healthy` após ~30-40 segundos.

---

### ETAPA 6: Verificar Health Checks

```bash
# 1. Aguardar 30 segundos para o servidor inicializar
sleep 30

# 2. Testar health check endpoint
curl http://localhost:8001/health

# ESPERADO: {"status":"healthy","environment":"production"}

# 3. Testar readiness check (verifica conexão com CrowdStrike)
curl http://localhost:8001/ready

# ESPERADO: {"ready":true,"provider_healthy":true}

# 4. Listar todas as ferramentas disponíveis
curl http://localhost:8001/mcp/v1/tools | jq .

# ESPERADO: Lista de 9 ferramentas CrowdStrike

# 5. Testar endpoint raiz
curl http://localhost:8001/

# ESPERADO: Informações da API
```

**SE ALGUM TESTE FALHAR**:

```bash
# Ver logs para diagnosticar
docker compose logs

# Ver logs apenas do container MCP
docker compose logs mcp-crowdstrike

# Verificar status do container
docker compose ps

# Ver detalhes do container
docker inspect mcp-crowdstrike-server
```

---

### ETAPA 7: Testar Ferramenta CrowdStrike (Opcional mas Recomendado)

```bash
# Testar query de dispositivos (consulta básica)
curl -X POST http://localhost:8001/mcp/v1/tools/query_devices_by_filter \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"limit": 5}}' | jq .

# ESPERADO:
# {
#   "success": true,
#   "data": {
#     "device_ids": ["..."]
#   },
#   "metadata": {
#     "total": ...,
#     "limit": 5,
#     "offset": 0
#   }
# }
```

**Se retornar erro de autenticação (401)**:
- Verifique se as credenciais no `.env` estão corretas
- Verifique se a URL base está correta para sua região
- Reinicie o container: `docker compose restart`

---

### ETAPA 8: Configurar Firewall (Se Aplicável)

**Se você quiser acessar o servidor de fora da VPS** (não recomendado para produção sem SSL):

```bash
# Verificar se UFW está ativo
sudo ufw status

# Se UFW estiver ativo, permitir porta 8001
sudo ufw allow 8001/tcp

# Verificar regra foi adicionada
sudo ufw status numbered
```

**RECOMENDAÇÃO DE SEGURANÇA**:
- Para produção, configure um reverse proxy (Nginx/Caddy) com SSL/TLS
- Use certificado SSL (Let's Encrypt)
- Não exponha a porta 8001 diretamente para a internet
- Configure autenticação adicional (API keys, OAuth2)

---

### ETAPA 9: Configurar Reinício Automático

O Docker Compose já está configurado com `restart: unless-stopped`, então o container reiniciará automaticamente se a VPS reiniciar.

**Verificar configuração**:

```bash
cd ~/projects/MCP/docker
cat docker-compose.yml | grep restart
```

**ESPERADO**: `restart: unless-stopped`

**Testar reinício automático**:

```bash
# Parar o container
docker compose stop

# Aguardar alguns segundos
sleep 5

# Verificar que está parado
docker compose ps

# Iniciar novamente
docker compose up -d

# Verificar que subiu corretamente
docker compose ps
curl http://localhost:8001/health
```

---

### ETAPA 10: Monitoramento e Logs

```bash
# 1. Ver logs em tempo real
docker compose logs -f

# 2. Ver apenas últimas 100 linhas
docker compose logs --tail=100

# 3. Ver logs com timestamp
docker compose logs -t

# 4. Ver estatísticas do container (CPU, memória, rede)
docker stats mcp-crowdstrike-server

# 5. Ver saúde do container
docker inspect mcp-crowdstrike-server --format='{{.State.Health.Status}}'

# ESPERADO: "healthy"
```

**Configurar rotação de logs** (opcional):

O Docker Compose já está configurado com rotação automática:
- Máximo 10MB por arquivo de log
- Máximo 3 arquivos de log

---

### ETAPA 11: Backup e Atualização

**Para fazer backup da configuração**:

```bash
# Backup do arquivo .env (contém credenciais)
cp ~/projects/MCP/.env ~/mcp-backup-env-$(date +%Y%m%d).bak

# Verificar backup
ls -la ~/mcp-backup-env-*
```

**Para atualizar o código no futuro**:

```bash
# 1. Parar o servidor
cd ~/projects/MCP/docker
docker compose down

# 2. Atualizar código do GitHub
cd ~/projects/MCP
git pull origin master

# 3. Rebuild da imagem (se houver mudanças no código)
cd docker
docker compose build

# 4. Reiniciar o servidor
docker compose up -d

# 5. Verificar saúde
curl http://localhost:8001/health
```

---

### ETAPA 12: Comandos Úteis para Operação

```bash
# Ver status do container
docker compose ps

# Parar o servidor
docker compose stop

# Iniciar o servidor
docker compose start

# Reiniciar o servidor
docker compose restart

# Parar e remover container (mantém dados)
docker compose down

# Ver logs
docker compose logs -f

# Ver estatísticas
docker stats mcp-crowdstrike-server

# Executar comando dentro do container
docker compose exec mcp-crowdstrike /bin/bash

# Ver configuração do container
docker compose config

# Limpar recursos não utilizados
docker system prune -a
```

---

## CHECKLIST DE VERIFICAÇÃO FINAL

Após completar todas as etapas, verifique:

- [ ] Docker e Docker Compose instalados
- [ ] Repositório clonado do GitHub
- [ ] Arquivo `.env` criado com credenciais corretas
- [ ] Imagem Docker construída (~180-200MB)
- [ ] Container rodando com status `healthy`
- [ ] Health check retorna `{"status":"healthy"}`
- [ ] Readiness check retorna `{"ready":true,"provider_healthy":true}`
- [ ] Endpoint `/mcp/v1/tools` lista 9 ferramentas
- [ ] Teste de query de dispositivos funciona
- [ ] Logs não mostram erros críticos
- [ ] Container configurado para reinício automático

---

## INFORMAÇÕES DE ACESSO

Após instalação bem-sucedida:

- **URL Local**: `http://localhost:8001`
- **Health Check**: `http://localhost:8001/health`
- **Readiness Check**: `http://localhost:8001/ready`
- **API Root**: `http://localhost:8001/`
- **Lista de Tools**: `http://localhost:8001/mcp/v1/tools`
- **SSE Stream**: `http://localhost:8001/sse`

**Se acessar de fora da VPS**:
- Substitua `localhost` pelo IP público da VPS
- Certifique-se de ter configurado firewall/segurança adequadamente

---

## SOLUÇÃO DE PROBLEMAS COMUNS

### Container não inicia:
```bash
docker compose logs
# Ver erro específico e corrigir
```

### Erro de autenticação CrowdStrike:
```bash
# Verificar credenciais no .env
cat .env | grep FALCON

# Testar credenciais manualmente
docker compose exec mcp-crowdstrike python -c "
from mcp_crowdstrike.config import get_settings
settings = get_settings()
print(f'Client ID: {settings.falcon_client_id.get_secret_value()[:10]}...')
print(f'Base URL: {settings.falcon_base_url}')
"
```

### Health check falha:
```bash
# Ver logs detalhados
docker compose logs -f

# Reiniciar container
docker compose restart

# Verificar se porta está em uso
sudo netstat -tulpn | grep 8001
```

### Sem conectividade com CrowdStrike:
```bash
# Testar DNS e conectividade
curl -I https://api.crowdstrike.com

# Ver logs de erro
docker compose logs | grep -i error
```

---

## SEGURANÇA EM PRODUÇÃO

**IMPORTANTE** - Para ambiente de produção real:

1. **SSL/TLS**: Configure reverse proxy com certificado SSL
2. **Firewall**: Não exponha porta 8001 diretamente
3. **Autenticação**: Adicione camada de autenticação (API keys)
4. **Monitoramento**: Configure alertas de saúde
5. **Backups**: Faça backup regular do `.env`
6. **Logs**: Configure agregação de logs (ELK, Grafana Loki)
7. **Recursos**: Configure limites adequados de CPU/memória
8. **Rede**: Use rede privada/VPN quando possível

---

## PRÓXIMOS PASSOS APÓS INSTALAÇÃO

1. Testar todas as 9 ferramentas CrowdStrike
2. Configurar monitoramento e alertas
3. Documentar endpoints para sua equipe
4. Criar scripts de automação usando as ferramentas
5. Configurar backups automáticos
6. Implementar SSL/TLS com reverse proxy
7. Integrar com ferramentas de observabilidade

---

## CONTATO E SUPORTE

- **Repositório**: https://github.com/fjopereira/MCP
- **Documentação**: Ver README.md no repositório
- **Issues**: https://github.com/fjopereira/MCP/issues

---

## RESUMO DO QUE FOI INSTALADO

✅ **MCP Server for CrowdStrike Falcon** em modo Docker
✅ **9 ferramentas CrowdStrike** (hosts, detections, incidents)
✅ **FastAPI server** com health checks e MCP protocol
✅ **Logging estruturado** em JSON para observabilidade
✅ **Docker containerizado** com reinício automático
✅ **Pronto para produção** com segurança e qualidade

**Status**: Servidor rodando em `http://localhost:8001` ✨

---

**BOA SORTE COM A INSTALAÇÃO!** 🚀

Se encontrar qualquer problema, consulte os logs com `docker compose logs -f` e verifique a seção de Solução de Problemas acima.
