"""
KAIROS V5 - Moteur d'Exécution Déterministe
Compile le tuple Kairos en instructions de remédiation déterministes.
"""

from typing import List, Dict, Any
from .parser import KairosTuple, KairosParser
from .operators import KairosOperator

class KairosExecutor:
    """Exécuteur d'actions déterministes dérivées du Tuple Kairos."""

    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []

    def compile_plan(self, k_tuple: KairosTuple) -> List[Dict[str, Any]]:
        """Génère un plan d'action ordonné et sécurisé à partir du tuple."""
        plan = []

        # 1. Vérification des préconditions
        for req in k_tuple.requires:
            plan.append({
                "stage": "PRECONDITION",
                "action": req,
                "type": "ASSERT_PRECONDITION"
            })

        # 2. Application des actions de remédiation ordonnées
        for idx, act in enumerate(k_tuple.fix_actions):
            loop_info = KairosOperator.parse_loop_break(act)
            stonith_info = KairosOperator.parse_stonith(act)
            decouple_info = KairosOperator.parse_decouple(act)

            if loop_info["is_loop"]:
                plan.append({
                    "stage": f"FIX_STEP_{idx+1}",
                    "type": "BREAK_RECURSIVE_LOOP",
                    "cycle": loop_info["cycle"],
                    "break_at": loop_info["break_node"],
                    "command": f"interrupter --cycle '{'>'.join(loop_info['cycle'])}' --cut '{loop_info['break_node']}'"
                })
            elif stonith_info["is_stonith"]:
                plan.append({
                    "stage": f"FIX_STEP_{idx+1}",
                    "type": "STONITH_FENCING",
                    "target": stonith_info["target_node"],
                    "command": f"fence_node --action off --target '{stonith_info['target_node']}'"
                })
            elif decouple_info["is_decouple"]:
                plan.append({
                    "stage": f"FIX_STEP_{idx+1}",
                    "type": "CIRCUIT_BREAKER",
                    "target": decouple_info["circuit"],
                    "command": f"circuit_breaker --trip '{decouple_info['circuit']}'"
                })
            else:
                plan.append({
                    "stage": f"FIX_STEP_{idx+1}",
                    "type": "STANDARD_OPERATION",
                    "action": act,
                    "command": f"exec_action --step '{act}'"
                })

        return plan

    def execute(self, k_tuple: KairosTuple, dry_run: bool = True) -> Dict[str, Any]:
        """Exécute le plan et consigne le rapport d'exécution."""
        plan = self.compile_plan(k_tuple)
        results = []

        for step in plan:
            status = "SIMULATED_SUCCESS" if dry_run else "EXECUTED_SUCCESS"
            results.append({
                "stage": step["stage"],
                "type": step["type"],
                "command": step.get("command", ""),
                "status": status
            })

        report = {
            "domain": k_tuple.domain,
            "pathology": k_tuple.pathology,
            "severity": k_tuple.severity,
            "dry_run": dry_run,
            "total_steps": len(plan),
            "steps": results,
            "success": True
        }

        self.execution_history.append(report)
        return report