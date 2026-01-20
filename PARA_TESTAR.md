# 🚀 Como Testar o MCP CrowdStrike (SUPER FÁCIL!)

## ✨ Teste SEM Credenciais (Recomendado!)

**Não precisa de credenciais CrowdStrike!** Use o modo demo:

### 3 Comandos e Pronto:

```bash
# 1. Clonar e entrar no projeto
git clone https://github.com/fjopereira/MCP.git
cd MCP

# 2. Instalar (cria ambiente virtual e instala tudo)
python -m venv .venv && .venv\Scripts\activate && pip install -e .
# Linux/Mac: python3 -m venv .venv && source .venv/bin/activate && pip install -e .

# 3. Executar DEMO (SEM CREDENCIAIS!)
python test_demo_mode.py
```

**✅ Pronto!** Você verá todas as 9 ferramentas funcionando!

---

## 📊 O que o Demo Mostra?

Testa **TODAS as 9 ferramentas CrowdStrike** com dados simulados:

- ✅ Query de dispositivos (hosts)
- ✅ Detalhes de dispositivos
- ✅ Containment (isolamento de host)
- ✅ Lift containment
- ✅ Query de detecções
- ✅ Detalhes de detecções
- ✅ Update de status de detecções
- ✅ Query de incidentes
- ✅ Detalhes de incidentes

**Tudo SIMULADO** - sem precisar de credenciais reais!

---

## 🎯 Se Quiser Testar com Dados Reais

### Opção 1: Código Python Direto

Crie arquivo `test.py`:

```python
import asyncio
from mcp_crowdstrike import CrowdStrikeClient

async def test():
    async with CrowdStrikeClient(
        client_id="SUA_CREDENCIAL_AQUI",
        client_secret="SUA_CREDENCIAL_AQUI"
    ) as client:
        result = await client.query_devices_by_filter(limit=5)
        print(result)

asyncio.run(test())
```

Execute:
```bash
python test.py
```

### Opção 2: Arquivo de Teste Completo

1. Abra `test_sdk_example.py`
2. Cole suas credenciais nas linhas 22-23
3. Execute: `python test_sdk_example.py`

---

## 📁 Arquivos Importantes

- **`test_demo_mode.py`** - 🎯 Teste SEM credenciais (RECOMENDADO!)
- **`test_sdk_example.py`** - Teste COM credenciais reais
- **`DEMO_MODE.md`** - Documentação completa do modo demo
- **`TESTE_RAPIDO.md`** - Guia rápido de teste
- **`README.md`** - Documentação completa do projeto

---

## ❓ Problemas Comuns

### "Module not found: mcp_crowdstrike"
```bash
# Ative o ambiente virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instale novamente
pip install -e .
```

### "python: command not found"
- Windows: Use `python`
- Linux/Mac: Use `python3`

### Ambiente virtual não ativa
- Windows: `.venv\Scripts\activate`
- Linux/Mac: `source .venv/bin/activate`

---

## 🎉 Resumo

### Para Testar SEM Credenciais (Modo Demo):
```bash
git clone https://github.com/fjopereira/MCP.git
cd MCP
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python test_demo_mode.py
```

### Para Testar COM Credenciais (Dados Reais):
```bash
# Depois de instalar (comandos acima)
# Edite test_sdk_example.py com suas credenciais
python test_sdk_example.py
```

---

## 💡 Recomendação

**Comece com o modo demo** (`test_demo_mode.py`) para:
- ✅ Ver o SDK funcionando
- ✅ Entender o formato dos dados
- ✅ Validar a instalação
- ✅ **Sem precisar de credenciais!**

Depois, se quiser, teste com credenciais reais usando `test_sdk_example.py`.

---

**Divirta-se testando!** 🚀

Qualquer dúvida, veja a documentação completa em `README.md` ou `DEMO_MODE.md`.
