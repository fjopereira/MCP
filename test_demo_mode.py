"""
🎯 DEMO MODE - Teste do MCP CrowdStrike SEM CREDENCIAIS REAIS!

Este arquivo demonstra TODAS as funcionalidades do SDK usando dados SIMULADOS.
NÃO é necessário ter credenciais CrowdStrike - perfeito para demonstração!

INSTRUÇÕES:
1. Instale as dependências: pip install -e .
2. Execute: python test_demo_mode.py
3. Veja o SDK em ação com dados simulados!

⚠️ IMPORTANTE: Este modo usa dados FALSOS para demonstração.
   Para usar com dados REAIS, veja test_sdk_example.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_crowdstrike.config import Settings
from mcp_crowdstrike.providers.mock import MockCrowdStrikeProvider
from mcp_crowdstrike.tools.crowdstrike import detections, hosts, incidents
from pydantic import SecretStr


async def demo_mode():
    """Demonstração completa do SDK com dados simulados."""

    print("=" * 70)
    print("🎯 MCP CROWDSTRIKE - MODO DEMONSTRAÇÃO (SEM CREDENCIAIS)")
    print("=" * 70)
    print()
    print("✨ Este teste usa dados SIMULADOS - não precisa de credenciais reais!")
    print("   Perfeito para demonstrar a funcionalidade do SDK.")
    print()
    print("=" * 70)
    print()

    # Create mock provider (NO CREDENTIALS NEEDED!)
    provider = MockCrowdStrikeProvider()
    await provider.initialize()

    try:
        # ===================================================================
        # TESTE 1: Query de Dispositivos
        # ===================================================================
        print("📱 TESTE 1: Consultando Dispositivos (Hosts)")
        print("-" * 70)

        result = await hosts.execute_tool(
            provider, "query_devices_by_filter", {"limit": 10}
        )

        if result.get("success"):
            device_ids = result["data"]["device_ids"]
            total = result["metadata"]["total"]

            print(f"✓ Sucesso! Encontrados {total} dispositivos (simulados)")
            print(f"  Device IDs: {device_ids}")
            print()

            # ===================================================================
            # TESTE 2: Detalhes dos Dispositivos
            # ===================================================================
            if device_ids:
                print("📋 TESTE 2: Obtendo Detalhes dos Dispositivos")
                print("-" * 70)

                details = await hosts.execute_tool(
                    provider, "get_device_details", {"device_ids": device_ids}
                )

                if details.get("success"):
                    devices = details["data"]["devices"]
                    print(f"✓ Sucesso! Detalhes de {len(devices)} dispositivos:")
                    print()

                    for device in devices:
                        print(f"  🖥️  {device['hostname']}")
                        print(f"     Platform: {device['platform_name']}")
                        print(f"     OS: {device['os_version']}")
                        print(f"     Status: {device['status']}")
                        print(f"     IP Local: {device.get('local_ip', 'N/A')}")
                        print(
                            f"     IP Externo: {device.get('external_ip', 'N/A')}"
                        )
                        print(f"     Last Seen: {device['last_seen']}")
                        print()
                else:
                    print(f"✗ Erro: {details.get('error')}")
                    print()

        else:
            print(f"✗ Erro: {result.get('error')}")
            print()

        # ===================================================================
        # TESTE 3: Containment (AÇÃO CRÍTICA - apenas simulado)
        # ===================================================================
        print("⚠️  TESTE 3: Host Containment (SIMULADO - nenhuma ação real!)")
        print("-" * 70)

        if device_ids:
            contain_result = await hosts.execute_tool(
                provider, "contain_host", {"device_id": device_ids[0]}
            )

            if contain_result.get("success"):
                print(
                    f"✓ Containment simulado com sucesso para: {device_ids[0]}"
                )
                print(f"  Status: {contain_result['data']['status']}")
                print()
                print(
                    "  ℹ️  NOTA: Esta é uma SIMULAÇÃO. Nenhum host real foi isolado."
                )
                print()
            else:
                print(f"✗ Erro: {contain_result.get('error')}")
                print()

        # ===================================================================
        # TESTE 4: Query de Detecções
        # ===================================================================
        print("🔍 TESTE 4: Consultando Detecções de Segurança")
        print("-" * 70)

        det_result = await detections.execute_tool(
            provider, "query_detections", {"limit": 10}
        )

        if det_result.get("success"):
            detection_ids = det_result["data"]["detection_ids"]
            total_detections = det_result["metadata"]["total"]

            print(f"✓ Sucesso! Encontradas {total_detections} detecções (simuladas)")
            print(f"  Detection IDs: {detection_ids}")
            print()

            # ===================================================================
            # TESTE 5: Detalhes das Detecções
            # ===================================================================
            if detection_ids:
                print("📊 TESTE 5: Obtendo Detalhes das Detecções")
                print("-" * 70)

                det_details = await detections.execute_tool(
                    provider,
                    "get_detection_details",
                    {"detection_ids": detection_ids},
                )

                if det_details.get("success"):
                    dets = det_details["data"]["detections"]
                    print(f"✓ Sucesso! Detalhes de {len(dets)} detecções:")
                    print()

                    for det in dets:
                        print(f"  🚨 {det['detection_id']}")
                        print(f"     Status: {det['status']}")
                        print(f"     Severidade: {det['severity']}")
                        print(f"     Tática: {det['tactic']}")
                        print(f"     Técnica: {det['technique']}")
                        print(
                            f"     Host: {det['device']['hostname']}"
                        )
                        print(f"     Criado: {det['created_timestamp']}")
                        print()
                else:
                    print(f"✗ Erro: {det_details.get('error')}")
                    print()

        else:
            print(f"✗ Erro: {det_result.get('error')}")
            print()

        # ===================================================================
        # TESTE 6: Update Detection Status (SIMULADO)
        # ===================================================================
        print("✏️  TESTE 6: Atualizando Status de Detecção (SIMULADO)")
        print("-" * 70)

        if detection_ids:
            update_result = await detections.execute_tool(
                provider,
                "update_detection_status",
                {
                    "detection_ids": [detection_ids[0]],
                    "status": "false_positive",
                    "comment": "Teste de demonstração - falso positivo simulado",
                },
            )

            if update_result.get("success"):
                print(f"✓ Status atualizado com sucesso (simulado)")
                print(f"  Detecção: {detection_ids[0]}")
                print(f"  Novo status: false_positive")
                print()
                print(
                    "  ℹ️  NOTA: Esta é uma SIMULAÇÃO. Nenhuma detecção real foi alterada."
                )
                print()
            else:
                print(f"✗ Erro: {update_result.get('error')}")
                print()

        # ===================================================================
        # TESTE 7: Query de Incidentes
        # ===================================================================
        print("🎯 TESTE 7: Consultando Incidentes de Segurança")
        print("-" * 70)

        inc_result = await incidents.execute_tool(
            provider, "query_incidents", {"limit": 10}
        )

        if inc_result.get("success"):
            incident_ids = inc_result["data"]["incident_ids"]
            total_incidents = inc_result["metadata"]["total"]

            print(f"✓ Sucesso! Encontrados {total_incidents} incidentes (simulados)")
            print(f"  Incident IDs: {incident_ids}")
            print()

            # ===================================================================
            # TESTE 8: Detalhes dos Incidentes
            # ===================================================================
            if incident_ids:
                print("📈 TESTE 8: Obtendo Detalhes dos Incidentes")
                print("-" * 70)

                inc_details = await incidents.execute_tool(
                    provider,
                    "get_incident_details",
                    {"incident_ids": incident_ids},
                )

                if inc_details.get("success"):
                    incs = inc_details["data"]["incidents"]
                    print(f"✓ Sucesso! Detalhes de {len(incs)} incidentes:")
                    print()

                    for inc in incs:
                        print(f"  🎯 {inc['name']}")
                        print(f"     ID: {inc['incident_id']}")
                        print(f"     Status: {inc['status']}")
                        print(f"     Estado: {inc['state']}")
                        print(f"     Descrição: {inc['description']}")
                        print(f"     Hosts afetados: {len(inc['hosts'])}")
                        print(
                            f"     Detecções relacionadas: {len(inc['detections'])}"
                        )
                        print(f"     Táticas: {', '.join(inc['tactics'])}")
                        print(f"     Início: {inc['start']}")
                        print()
                else:
                    print(f"✗ Erro: {inc_details.get('error')}")
                    print()

        else:
            print(f"✗ Erro: {inc_result.get('error')}")
            print()

        # ===================================================================
        # TESTE 9: Lift Containment (SIMULADO)
        # ===================================================================
        print("🔓 TESTE 9: Removendo Containment (SIMULADO)")
        print("-" * 70)

        if device_ids:
            lift_result = await hosts.execute_tool(
                provider, "lift_containment", {"device_id": device_ids[0]}
            )

            if lift_result.get("success"):
                print(f"✓ Containment removido com sucesso (simulado)")
                print(f"  Device: {device_ids[0]}")
                print(f"  Status: {lift_result['data']['status']}")
                print()
                print(
                    "  ℹ️  NOTA: Esta é uma SIMULAÇÃO. Nenhum host real foi liberado."
                )
                print()
            else:
                print(f"✗ Erro: {lift_result.get('error')}")
                print()

        # ===================================================================
        # RESUMO FINAL
        # ===================================================================
        print("=" * 70)
        print("✅ DEMONSTRAÇÃO COMPLETA!")
        print("=" * 70)
        print()
        print("📊 Ferramentas Testadas:")
        print("   ✓ 1. query_devices_by_filter - Buscar dispositivos")
        print("   ✓ 2. get_device_details - Detalhes de dispositivos")
        print("   ✓ 3. contain_host - Isolar host (CRÍTICO)")
        print("   ✓ 4. lift_containment - Remover isolamento")
        print("   ✓ 5. query_detections - Buscar detecções")
        print("   ✓ 6. get_detection_details - Detalhes de detecções")
        print("   ✓ 7. update_detection_status - Atualizar status")
        print("   ✓ 8. query_incidents - Buscar incidentes")
        print("   ✓ 9. get_incident_details - Detalhes de incidentes")
        print()
        print("🎯 Todas as 9 ferramentas funcionando perfeitamente!")
        print()
        print("=" * 70)
        print("💡 PRÓXIMOS PASSOS:")
        print("=" * 70)
        print()
        print("1. Para usar com dados REAIS do CrowdStrike:")
        print("   → Veja o arquivo: test_sdk_example.py")
        print("   → Você precisará de credenciais CrowdStrike")
        print()
        print("2. Para deploy em produção (servidor Docker):")
        print("   → Veja o arquivo: VPS_DEPLOYMENT_PROMPT.md")
        print("   → Modo servidor com health checks e API REST")
        print()
        print("3. Para integrar em seus scripts Python:")
        print("   → Importe: from mcp_crowdstrike import CrowdStrikeClient")
        print("   → Use as mesmas funções mostradas acima")
        print()
        print("=" * 70)
        print()
        print("✨ Obrigado por testar o MCP CrowdStrike! ✨")
        print()

    finally:
        await provider.shutdown()


if __name__ == "__main__":
    print()
    print("🚀 Iniciando demonstração do MCP CrowdStrike...")
    print()

    try:
        asyncio.run(demo_mode())
    except KeyboardInterrupt:
        print()
        print("⚠️  Demonstração interrompida pelo usuário.")
        print()
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERRO DURANTE A DEMONSTRAÇÃO")
        print("=" * 70)
        print(f"Erro: {str(e)}")
        print()
        import traceback

        traceback.print_exc()
        print()
        print("Por favor, verifique:")
        print("1. As dependências estão instaladas? (pip install -e .)")
        print("2. Você está no diretório correto do projeto?")
        print()
