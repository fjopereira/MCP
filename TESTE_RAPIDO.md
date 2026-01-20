# 🚀 Teste Rápido do MCP CrowdStrike - Modo SDK

Este é um guia **SUPER SIMPLES** para testar o SDK CrowdStrike **SEM precisar de Docker**.

## 🎯 NOVO! Teste SEM Credenciais (Modo Demo)

**Não quer passar suas credenciais CrowdStrike?** Sem problemas!

Use o **modo demonstração** com dados simulados:

```bash
# 1. Clonar o repositório
git clone https://github.com/fjopereira/MCP.git
cd MCP

# 2. Instalar dependências
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -e .

# 3. Executar modo demo (SEM CREDENCIAIS!)
python test_demo_mode.py
```

**✨ Pronto!** Você verá todas as 9 ferramentas funcionando com dados simulados!

**Vantagens do Modo Demo:**
- ✅ **NÃO precisa de credenciais CrowdStrike**
- ✅ Testa TODAS as 9 ferramentas
- ✅ Dados realistas simulados
- ✅ Perfeito para demonstração
- ✅ Ideal para aprender a usar o SDK

**Limitação:** Os dados são simulados/falsos. Para dados reais, veja o teste completo abaixo.

---

## ⚡ Teste Completo com Dados Reais (5 minutos)

### Passo 1: Instalar Python 3.11+

```bash
# Verificar se tem Python 3.11 ou superior
python --version
# ou
python3 --version
```

**Se não tiver Python 3.11+**, baixe em: https://www.python.org/downloads/

---

### Passo 2: Clonar o Repositório

```bash
git clone https://github.com/fjopereira/MCP.git
cd MCP
```

---

### Passo 3: Instalar Dependências

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

### Passo 4: Editar o Arquivo de Teste

Abra o arquivo `test_sdk_example.py` e cole suas credenciais:

```python
# Linha 22 e 23 - COLE SUAS CREDENCIAIS AQUI:
client_id = "SUA_CREDENCIAL_CLIENT_ID_AQUI"
client_secret = "SUA_CREDENCIAL_CLIENT_SECRET_AQUI"
```

**Como obter as credenciais:**
1. Acesse o console CrowdStrike Falcon
2. Vá em **Support > API Clients & Keys**
3. Copie o **Client ID** e **Client Secret**

---

### Passo 5: Executar o Teste

```bash
python test_sdk_example.py
```

**Resultado esperado:**
```
============================================================
MCP CrowdStrike SDK - Teste de Conexão
============================================================

✓ Cliente inicializado com sucesso!

Teste 1: Consultando dispositivos (limit=5)...
------------------------------------------------------------
✓ Sucesso! Encontrados 42 dispositivos no total.
  Primeiros 5 IDs: ['device-id-1', 'device-id-2', ...]

Teste 2: Obtendo detalhes dos dispositivos...
------------------------------------------------------------
✓ Sucesso! Detalhes de 3 dispositivos:

  • WIN-SERVER-01
    Platform: Windows
    Status: normal
    Last Seen: 2024-01-19T10:30:00Z
...
```

---

## 🎯 Teste Alternativo - Uma Linha de Código

Se você só quer testar **UMA CONSULTA RÁPIDA**, pode usar este código:

```python
import asyncio
from mcp_crowdstrike import CrowdStrikeClient

async def test():
    async with CrowdStrikeClient(
        client_id="SUA_CREDENCIAL_CLIENT_ID",
        client_secret="SUA_CREDENCIAL_CLIENT_SECRET"
    ) as client:
        result = await client.query_devices_by_filter(limit=5)
        print(result)

asyncio.run(test())
```

**Como executar:**
```bash
# Salve o código acima em test_quick.py
python test_quick.py
```

---

## 📋 Checklist de Verificação

- [ ] Python 3.11+ instalado
- [ ] Repositório clonado
- [ ] Virtual environment criado e ativado
- [ ] Dependências instaladas (`pip install -e .`)
- [ ] Credenciais CrowdStrike obtidas
- [ ] Credenciais coladas no arquivo `test_sdk_example.py`
- [ ] Teste executado com sucesso

---

## ❌ Problemas Comuns

### Erro: "Client not initialized"
**Solução**: Use `async with` ou chame `await client.initialize()` antes de usar.

### Erro: "Authentication failed"
**Solução**: Verifique se suas credenciais estão corretas e se a URL base está correta para sua região.

### Erro: "Module not found: mcp_crowdstrike"
**Solução**:
1. Certifique-se de estar no diretório `MCP`
2. Ative o virtual environment (`.venv\Scripts\activate` ou `source .venv/bin/activate`)
3. Execute `pip install -e .`

### Erro: "Invalid credentials"
**Solução**: Suas credenciais estão incorretas ou expiraram. Gere novas credenciais no console CrowdStrike.

### Erro: URL base incorreta
**Solução**: Se você estiver em outra região (EU, US-2, etc.), altere a `base_url`:
```python
# Para EU
base_url = "https://api.eu-1.crowdstrike.com"

# Para US-2
base_url = "https://api.us-2.crowdstrike.com"
```

---

## 🔧 Regiões CrowdStrike

Altere a `base_url` conforme sua região:

- **US-1** (padrão): `https://api.crowdstrike.com`
- **US-2**: `https://api.us-2.crowdstrike.com`
- **EU-1**: `https://api.eu-1.crowdstrike.com`
- **US-GOV-1**: `https://api.laggar.gcw.crowdstrike.com`

---

## 🎉 Próximos Passos

Se o teste funcionou, você pode:

1. **Explorar todas as 9 ferramentas** - Ver `README.md` para lista completa
2. **Integrar com seus scripts** - Importar `CrowdStrikeClient` em qualquer código Python
3. **Testar em produção** - Deploy no Docker (ver `VPS_DEPLOYMENT_PROMPT.md`)

---

## 📚 Documentação Completa

- **README.md** - Documentação completa do projeto
- **VPS_DEPLOYMENT_PROMPT.md** - Instalação em servidor (modo Docker)
- **test_sdk_example.py** - Este arquivo de teste

---

## 💡 Dica

**Não quer criar arquivo `.env`?** Não precisa! O SDK aceita as credenciais diretamente no código:

```python
client = CrowdStrikeClient(
    client_id="sua-credencial",
    client_secret="sua-credencial"
)
```

O arquivo `.env` é **só para o modo servidor Docker**. Para testes rápidos e uso como biblioteca Python, pode passar as credenciais direto no código! 🚀

---

**Boa sorte com o teste!** Se funcionar, significa que o SDK está 100% operacional! ✨
