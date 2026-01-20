# 🎯 Modo Demonstração - Teste SEM Credenciais!

## ✨ O que é o Modo Demo?

O **Modo Demonstração** permite testar **TODAS as funcionalidades** do MCP CrowdStrike **SEM precisar de credenciais reais**!

Perfeito para:
- 🎓 Aprender a usar o SDK
- 🎬 Demonstrações e apresentações
- ✅ Validar a instalação e configuração
- 🧪 Testar integrações antes de conectar ao CrowdStrike real
- 📚 Entender o formato de dados retornados

## 🚀 Como Usar (3 passos)

### Passo 1: Instalar

```bash
# Clonar repositório
git clone https://github.com/fjopereira/MCP.git
cd MCP

# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -e .
```

### Passo 2: Executar Modo Demo

```bash
python test_demo_mode.py
```

### Passo 3: Ver os Resultados!

Você verá saída como:

```
======================================================================
🎯 MCP CROWDSTRIKE - MODO DEMONSTRAÇÃO (SEM CREDENCIAIS)
======================================================================

✨ Este teste usa dados SIMULADOS - não precisa de credenciais reais!
   Perfeito para demonstrar a funcionalidade do SDK.

======================================================================

📱 TESTE 1: Consultando Dispositivos (Hosts)
----------------------------------------------------------------------
✓ Sucesso! Encontrados 3 dispositivos (simulados)
  Device IDs: ['mock-device-001', 'mock-device-002', 'mock-device-003']

📋 TESTE 2: Obtendo Detalhes dos Dispositivos
----------------------------------------------------------------------
✓ Sucesso! Detalhes de 3 dispositivos:

  🖥️  WIN-SERVER-DEMO-01
     Platform: Windows
     OS: Windows Server 2019
     Status: normal
     IP Local: 192.168.1.100
     IP Externo: 203.0.113.100
     Last Seen: 2024-01-19T10:30:00Z

  🖥️  LINUX-WEB-DEMO-01
     Platform: Linux
     OS: Ubuntu 22.04
     Status: normal
     IP Local: 192.168.1.101
     IP Externo: 203.0.113.101
     Last Seen: 2024-01-19T10:25:00Z

...

✅ DEMONSTRAÇÃO COMPLETA!
🎯 Todas as 9 ferramentas funcionando perfeitamente!
```

## 📊 O que é Testado?

O modo demo testa **TODAS as 9 ferramentas**:

### Host Management (4 ferramentas)
1. ✅ `query_devices_by_filter` - Buscar dispositivos
2. ✅ `get_device_details` - Obter detalhes
3. ✅ `contain_host` - Isolar host (simulado)
4. ✅ `lift_containment` - Remover isolamento (simulado)

### Detection Management (3 ferramentas)
5. ✅ `query_detections` - Buscar detecções
6. ✅ `get_detection_details` - Obter detalhes
7. ✅ `update_detection_status` - Atualizar status (simulado)

### Incident Management (2 ferramentas)
8. ✅ `query_incidents` - Buscar incidentes
9. ✅ `get_incident_details` - Obter detalhes

## 🎭 Dados Simulados

O modo demo usa dados **realistas** mas **falsos**:

### Dispositivos Simulados:
- **WIN-SERVER-DEMO-01** - Windows Server 2019
- **LINUX-WEB-DEMO-01** - Ubuntu 22.04
- **MAC-LAPTOP-DEMO-01** - macOS 14.0

### Detecções Simuladas:
- **Phishing** - Severidade: High
- **PowerShell Execution** - Severidade: Medium

### Incidentes Simulados:
- **Suspicious Activity on WIN-SERVER-DEMO-01**

## ⚠️ Importante

**O modo demo é apenas para demonstração!**

- ❌ **NÃO** se conecta ao CrowdStrike real
- ❌ **NÃO** executa ações reais (contain, update status, etc.)
- ❌ **NÃO** retorna dados reais da sua organização

**Para usar com dados reais:**
- Veja o arquivo: `test_sdk_example.py`
- Você precisará de credenciais CrowdStrike
- Configure suas credenciais no código

## 💡 Como Funciona?

O modo demo usa um **Mock Provider** que:

1. Simula as respostas da API CrowdStrike
2. Retorna dados em formato idêntico ao real
3. Valida o funcionamento de todas as ferramentas
4. **NÃO precisa de internet ou credenciais**

Código do mock provider: `src/mcp_crowdstrike/providers/mock.py`

## 🔄 Comparação: Demo vs Real

| Característica | Modo Demo | Modo Real |
|----------------|-----------|-----------|
| **Credenciais** | ❌ NÃO precisa | ✅ Precisa |
| **Internet** | ❌ NÃO precisa | ✅ Precisa |
| **Dados** | Simulados/Falsos | Reais da organização |
| **Ações** | Simuladas | Executadas no CrowdStrike |
| **Uso** | Demonstração/Testes | Produção |

## 📚 Próximos Passos

Após testar o modo demo:

### 1. Teste com Dados Reais
```bash
# Edite test_sdk_example.py com suas credenciais
python test_sdk_example.py
```

### 2. Use em Seus Scripts
```python
from mcp_crowdstrike import CrowdStrikeClient

async with CrowdStrikeClient(
    client_id="sua-credencial",
    client_secret="sua-credencial"
) as client:
    devices = await client.query_devices_by_filter(limit=10)
```

### 3. Deploy em Produção
```bash
# Ver VPS_DEPLOYMENT_PROMPT.md para instruções completas
cd docker
docker compose up -d
```

## 🎓 Para Aprender

O modo demo é perfeito para:

1. **Entender o formato dos dados** retornados
2. **Testar sua integração** antes de conectar ao real
3. **Desenvolver scripts** sem consumir API calls
4. **Fazer demos** sem expor dados sensíveis
5. **Treinar sua equipe** no uso das ferramentas

## 🆘 Problemas?

### Erro: "Module not found: mcp_crowdstrike"
**Solução:**
```bash
# Certifique-se de estar no diretório MCP
cd MCP

# Ative o ambiente virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instale o pacote
pip install -e .
```

### Erro: "No module named 'pydantic'"
**Solução:**
```bash
pip install -e .
```

### Modo demo muito lento?
**Resposta:** O modo demo deve ser INSTANTÂNEO pois não faz chamadas reais à API.
Se estiver lento, pode haver problema com a instalação.

## ✨ Benefícios do Modo Demo

### Para Desenvolvedores:
- 🚀 Desenvolvimento rápido sem API calls
- 🧪 Testes unitários sem mocks complexos
- 📖 Documentação de exemplos

### Para Apresentações:
- 🎬 Demonstrações sem credenciais sensíveis
- 💼 Apresentações para clientes
- 🎓 Treinamentos e workshops

### Para Validação:
- ✅ Verificar instalação correta
- 🔍 Entender estrutura de dados
- 🎯 Validar integrações

## 🎉 Conclusão

O **Modo Demo** é a maneira mais fácil de:
- Conhecer o MCP CrowdStrike
- Testar sem credenciais
- Aprender a usar o SDK
- Validar instalação

**Experimente agora:**
```bash
python test_demo_mode.py
```

---

**Divirta-se explorando o MCP CrowdStrike!** 🚀
