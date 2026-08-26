"""
TEST D'INTÉGRATION END-TO-END : 4 PATHOLOGIES LOGIQUES
Vérifie la chaîne complète : Ancrage Chronos -> Mémoire RAG -> Kernel STRIC_i -> Tuple Kairos V5 -> Plan Déterministe.
"""

from runtime.agent_loop import VeralumeAgent
from epistemic_memory.indexer import EpistemicIndexer
from epistemic_memory.vector_store import EpistemicMemoryStore

def run_integration():
    print("=== DÉBUT DU TEST D'INTÉGRATION COMPLET ===")
    memory = EpistemicMemoryStore("data/test_memory.json")
    count = EpistemicIndexer.index_meta_document("META_DOCUMENT_VERALUME_KAIROS_INTEGRAL.md", memory)
    print(f"Indexation réussie : {count} sections indexées dans la mémoire Nœud G.")

    agent = VeralumeAgent(memory_store=memory)

    scenarios = [
        ("[22:00] Alerte: Split-Brain quorum lost sur cluster Ceph/HA", "cluster_ha", "split_brain_quorum_lost"),
        ("[22:05] Alerte: Thundering Herd stampede sur Redis Cache miss rate > 85%", "cache_layer", "thundering_herd_stampede"),
        ("[22:10] Alerte: Boucle récursive télémétrie Möbius saturant le buffer", "alert_pipeline", "recursive_telemetry_loop"),
        ("[22:15] Alerte: Nœud byzantin malveillant détecté", "consensus_engine", "byzantine_fault_detected")
    ]

    for input_text, expected_domain, expected_pathology in scenarios:
        res = agent.process_incident(input_text, dry_run=True)
        kt = res["kairos_tuple"]
        
        print(f"\n[Test] Input: {input_text}")
        print(f"       -> Chronos: {res['temporal']['delta_formatted']}")
        print(f"       -> Domaine: {kt.domain} (Attendu: {expected_domain})")
        print(f"       -> Pathologie: {kt.pathology} (Attendu: {expected_pathology})")
        print(f"       -> Plan d'action ({len(res['execution']['steps'])} étapes):")
        for s in res['execution']['steps']:
            print(f"          - [{s['stage']}] {s['type']} : `{s['command']}`")

        assert kt.domain == expected_domain, f"Domaine invalide: {kt.domain} != {expected_domain}"
        assert kt.pathology == expected_pathology, f"Pathologie invalide: {kt.pathology} != {expected_pathology}"
        assert res["execution"]["success"] is True, "Échec d'exécution du plan"

    print("\n[SUCCES] TOUS LES TESTS D'INTÉGRATION SONT VALIDÉS AVEC SUCCÈS (4/4) !")

if __name__ == "__main__":
    run_integration()