"""
KAIROS V5 - Parser & Grammaire Canonique
Structure du Tuple Vectoriel (8 facettes orthogonales):
domain:<DOM>|<PATHOLOGIE>|<GRAVITÉ>|<ACTIVATION>|requires:<PRÉCONDITIONS>|prevents:<RISQUES>|fix:<ACTIONS_ORDONNÉES>|<SECTION_CIBLE>
"""

import re
from dataclasses import dataclass
from typing import List

def split_outside_parens(s: str, delimiter: str = ">") -> List[str]:
    """Divise une chaîne par un délimiteur uniquement hors des parenthèses (...)."""
    parts = []
    current = []
    depth = 0
    for char in s:
        if char == "(":
            depth += 1
            current.append(char)
        elif char == ")":
            depth = max(0, depth - 1)
            current.append(char)
        elif char == delimiter and depth == 0:
            part = "".join(current).strip()
            if part and part != "none" and part != "noop":
                parts.append(part)
            current = []
        else:
            current.append(char)
    part = "".join(current).strip()
    if part and part != "none" and part != "noop":
        parts.append(part)
    return parts

@dataclass
class KairosTuple:
    domain: str
    pathology: str
    severity: str
    activation: str
    requires: List[str]
    prevents: List[str]
    fix_actions: List[str]
    target_section: str
    raw_tuple: str = ""

    def to_vector_string(self) -> str:
        req_str = "requires:" + ">".join(self.requires) if self.requires else "requires:none"
        prev_str = "prevents:" + ">".join(self.prevents) if self.prevents else "prevents:none"
        fix_str = "fix:" + ">".join(self.fix_actions) if self.fix_actions else "fix:noop"
        return f"domain:{self.domain}|{self.pathology}|{self.severity}|{self.activation}|{req_str}|{prev_str}|{fix_str}|{self.target_section}"

class KairosParser:
    """Parse et valide la grammaire formelle Kairos V5."""

    @staticmethod
    def parse(tuple_str: str) -> KairosTuple:
        tuple_str = tuple_str.strip()
        if not tuple_str:
            raise ValueError("Le tuple Kairos ne peut pas être vide.")
        
        parts = [p.strip() for p in tuple_str.split("|")]
        if len(parts) != 8:
            raise ValueError(f"Le tuple Kairos doit comporter exactement 8 facettes (reçu {len(parts)}). Tuple: {tuple_str}")

        # Facette 1 : domain:<nom>
        if not parts[0].startswith("domain:"):
            raise ValueError(f"Facette 1 invalide, doit débuter par 'domain:' (reçu: {parts[0]})")
        domain = parts[0][len("domain:"):].strip()

        # Facette 2 : pathologie
        pathology = parts[1].strip()

        # Facette 3 : gravité
        severity = parts[2].strip()

        # Facette 4 : activation
        activation = parts[3].strip()

        # Facette 5 : requires:<preconditions>
        if not parts[4].startswith("requires:"):
            raise ValueError(f"Facette 5 invalide, doit débuter par 'requires:' (reçu: {parts[4]})")
        req_content = parts[4][len("requires:"):].strip()
        requires = split_outside_parens(req_content, ">")

        # Facette 6 : prevents:<risques>
        if not parts[5].startswith("prevents:"):
            raise ValueError(f"Facette 6 invalide, doit débuter par 'prevents:' (reçu: {parts[5]})")
        prev_content = parts[5][len("prevents:"):].strip()
        prevents = split_outside_parens(prev_content, ">")

        # Facette 7 : fix:<actions>
        if not parts[6].startswith("fix:"):
            raise ValueError(f"Facette 7 invalide, doit débuter par 'fix:' (reçu: {parts[6]})")
        fix_content = parts[6][len("fix:"):].strip()
        fix_actions = split_outside_parens(fix_content, ">")

        # Facette 8 : target_section
        target_section = parts[7].strip()
        if target_section.startswith("section:"):
            target_section = target_section[len("section:"):].strip()

        return KairosTuple(
            domain=domain,
            pathology=pathology,
            severity=severity,
            activation=activation,
            requires=requires,
            prevents=prevents,
            fix_actions=fix_actions,
            target_section=target_section,
            raw_tuple=tuple_str
        )

    @staticmethod
    def is_valid(tuple_str: str) -> bool:
        try:
            KairosParser.parse(tuple_str)
            return True
        except Exception:
            return False