"""
Exemplo de teste do MCP CrowdStrike SDK - Modo SDK (sem Docker)

INSTRUÇÕES:
1. Substitua 'YOUR_CLIENT_ID_HERE' pelo seu CrowdStrike Client ID
2. Substitua 'YOUR_CLIENT_SECRET_HERE' pelo seu CrowdStrike Client Secret
3. (Opcional) Altere a base_url se estiver em outra região
4. Execute: python test_sdk_example.py
"""

import asyncio
from mcp_crowdstrike import CrowdStrikeClient


async def test_crowdstrike_sdk():
    """Teste básico do SDK CrowdStrike."""

    # ============================================
    # COLE SUAS CREDENCIAIS AQUI:
    # ============================================
    client_id = "YOUR_CLIENT_ID_HERE"
    client_secret = "YOUR_CLIENT_SECRET_HERE"

    # Região da API (opcional - padrão é US-1)
    # US-1: https://api.crowdstrike.com
    # US-2: https://api.us-2.crowdstrike.com
    # EU-1: https://api.eu-1.crowdstrike.com
    # US-GOV: https://api.laggar.gcw.crowdstrike.com
    base_url = "https://api.crowdstrike.com"

    print("=" * 60)
    print("MCP CrowdStrike SDK - Teste de Conexão")
    print("=" * 60)
    print()

    try:
        # Criar cliente CrowdStrike
        async with CrowdStrikeClient(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url
        ) as client:

            print("✓ Cliente inicializado com sucesso!")
            print()

            # Teste 1: Query de dispositivos
            print("Teste 1: Consultando dispositivos (limit=5)...")
            print("-" * 60)

            result = await client.query_devices_by_filter(limit=5)

            if result.get("success"):
                device_ids = result["data"]["device_ids"]
                total = result["metadata"]["total"]

                print(f"✓ Sucesso! Encontrados {total} dispositivos no total.")
                print(f"  Primeiros 5 IDs: {device_ids}")
                print()

                # Teste 2: Detalhes dos dispositivos (se houver)
                if device_ids:
                    print("Teste 2: Obtendo detalhes dos dispositivos...")
                    print("-" * 60)

                    details = await client.get_device_details(
                        device_ids=device_ids[:3]  # Apenas os 3 primeiros
                    )

                    if details.get("success"):
                        devices = details["data"]["devices"]
                        print(f"✓ Sucesso! Detalhes de {len(devices)} dispositivos:")
                        print()

                        for device in devices:
                            hostname = device.get("hostname", "N/A")
                            platform = device.get("platform_name", "N/A")
                            status = device.get("status", "N/A")
                            last_seen = device.get("last_seen", "N/A")

                            print(f"  • {hostname}")
                            print(f"    Platform: {platform}")
                            print(f"    Status: {status}")
                            print(f"    Last Seen: {last_seen}")
                            print()
                    else:
                        print(f"✗ Erro ao obter detalhes: {details.get('error')}")
                        print()

                # Teste 3: Query de detecções
                print("Teste 3: Consultando detecções recentes (limit=5)...")
                print("-" * 60)

                detections = await client.query_detections(limit=5)

                if detections.get("success"):
                    detection_ids = detections["data"]["detection_ids"]
                    total_detections = detections["metadata"]["total"]

                    print(f"✓ Sucesso! Encontradas {total_detections} detecções no total.")
                    print(f"  Primeiros 5 IDs: {detection_ids}")
                    print()
                else:
                    print(f"✗ Erro ao consultar detecções: {detections.get('error')}")
                    print()

                # Teste 4: Query de incidentes
                print("Teste 4: Consultando incidentes (limit=5)...")
                print("-" * 60)

                incidents = await client.query_incidents(limit=5)

                if incidents.get("success"):
                    incident_ids = incidents["data"]["incident_ids"]
                    total_incidents = incidents["metadata"]["total"]

                    print(f"✓ Sucesso! Encontrados {total_incidents} incidentes no total.")
                    print(f"  Primeiros 5 IDs: {incident_ids}")
                    print()
                else:
                    print(f"✗ Erro ao consultar incidentes: {incidents.get('error')}")
                    print()

            else:
                print(f"✗ Erro na consulta: {result.get('error')}")
                print()

            print("=" * 60)
            print("Testes concluídos!")
            print("=" * 60)

    except Exception as e:
        print()
        print("=" * 60)
        print("✗ ERRO DURANTE O TESTE")
        print("=" * 60)
        print(f"Erro: {str(e)}")
        print()
        print("Possíveis causas:")
        print("1. Credenciais inválidas ou incorretas")
        print("2. URL base incorreta para sua região")
        print("3. Sem conectividade com a API CrowdStrike")
        print("4. Permissões insuficientes nas credenciais")
        print()
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Executar teste
    asyncio.run(test_crowdstrike_sdk())
