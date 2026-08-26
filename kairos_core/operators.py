"""
KAIROS V5 - Opérateurs Formels & Causalité
Modélise les opérateurs causaux stricts, disjoncteurs récursifs et consensus.
"""

from typing import List, Dict, Any
import re

class KairosOperator:
    @staticmethod
    def parse_loop_break(action_str: str) -> Dict[str, Any]:
        """Parse loop(A>B>C)+break_at(X)"""
        match = re.match(r"loop\((.*?)\)\+break_at\((.*?)\)", action_str)
        if match:
            cycle = [x.strip() for x in match.group(1).split(">")]
            break_node = match.group(2).strip()
            return {
                "type": "recursive_breaker",
                "cycle": cycle,
                "break_node": break_node,
                "is_loop": True
            }
        return {"type": "standard_action", "raw": action_str, "is_loop": False}

    @staticmethod
    def parse_stonith(action_str: str) -> Dict[str, Any]:
        """Parse stonith_node(X)"""
        match = re.match(r"stonith_node\((.*?)\)", action_str)
        if match:
            target_node = match.group(1).strip()
            return {
                "type": "stonith_fencing",
                "target_node": target_node,
                "is_stonith": True
            }
        return {"type": "standard_action", "raw": action_str, "is_stonith": False}

    @staticmethod
    def parse_decouple(action_str: str) -> Dict[str, Any]:
        """Parse decouple_circuit(X)"""
        match = re.match(r"decouple_circuit\((.*?)\)", action_str)
        if match:
            circuit = match.group(1).strip()
            return {
                "type": "circuit_breaker",
                "circuit": circuit,
                "is_decouple": True
            }
        return {"type": "standard_action", "raw": action_str, "is_decouple": False}