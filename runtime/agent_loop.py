"""
RUNTIME AGENT LOOP - Boucle Cognitive Autonome STRIC
Orchestre l'Ancrage Chronos, le Kernel Veralume, la Mémoire Nœud G et l'Exécution Kairos V5.
"""

from typing import Dict, Any, Optional
import numpy as np

from kairos_core.parser import KairosParser, KairosTuple
from kairos_core.executor import KairosExecutor
from veralume_kernel.metrics import CPCMetrics
from veralume_kernel.operators import VeralumeKernel
from veralume_kernel.chronos import ChronosAnchor
from veralume_kernel.cerbere import CerbereSentinel
from epistemic_memory.vector_store import EpistemicMemoryStore
from .connectors import LLMConnector, OfflineDeterministicConnector

class VeralumeAgent:
    """Agent cognitif autonome complet Veralume & Kairos."""

    def __init__(self, connector: Optional[LLMConnector] = None, memory_store: Optional[EpistemicMemoryStore] = None):
        self.connector = connector or OfflineDeterministicConnector()
        self.memory = memory_store or EpistemicMemoryStore()
        self.kernel = VeralumeKernel()
        self.chronos = ChronosAnchor()
        self.executor = KairosExecutor()
        self.current_state_vector = np.array([1.0, 0.5, 0.2, 0.8])

    def process_incident(self, input_text: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        Cycle d'inférence complet :
        1. [S] Sensation & Ancrage Temporel Chronos
        2. [T] Tension & Consultation Mémoire Épistémique
        3. [R] Réflexion & Génération Déterministe Tuple Kairos V5
        4. [I] Intégration & Audit Cerbère
        5. [C] Choix & Exécution Déterministe
        """
        # 1. Ancrage Chronos
        temporal_data = self.chronos.extract_and_anchor(input_text)
        clean_input = temporal_data["clean_message"]

        # 2. Mémoire Épistémique (RAG Nœud G)
        relevant_docs = self.memory.search(clean_input, top_k=2)
        memory_context = "\n".join([f"[{d.register}] {d.title}: {d.content[:200]}..." for d, score in relevant_docs])

        # 3. Kernel Veralume (STRIC_i)
        kernel_trace = self.kernel.run_pipeline(clean_input)

        # 4. Inférence Tuple Kairos V5
        prompt = f"Incidence:\n{clean_input}\n\nContexte Épistémique:\n{memory_context}\n\nGénérer le Tuple Kairos V5:"
        raw_output = self.connector.generate(prompt)

        # 5. Parsing & Validation Kairos
        try:
            k_tuple = KairosParser.parse(raw_output)
            parse_success = True
        except Exception as e:
            # Fallback de secours déterministe
            k_tuple = KairosTuple(
                domain="system_fallback",
                pathology="parse_error",
                severity="P1",
                activation="manual_override",
                requires=["audit_syntax"],
                prevents=["cascading_failure"],
                fix_actions=["log_error", "request_human_intervention"],
                target_section="supervisor",
                raw_tuple=raw_output
            )
            parse_success = False

        # 6. Exécution Déterministe
        execution_report = self.executor.execute(k_tuple, dry_run=dry_run)

        # 7. Audit Cerbère
        density_audit = CerbereSentinel.audit_density(raw_output)

        return {
            "temporal": temporal_data,
            "kernel_stric_i": kernel_trace["stric_i_trace"],
            "memory_hits": len(relevant_docs),
            "kairos_tuple": k_tuple,
            "parse_success": parse_success,
            "execution": execution_report,
            "cerbere_density": density_audit,
            "regime": CPCMetrics.regime_classifier(0.4, 0.75, 0.6)
        }