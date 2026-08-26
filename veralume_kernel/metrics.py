"""
VERALUME KERNEL - Métriques CPC & Dynamique Hamiltonienne
Implémente les calculs de Delta_cog, Phi, Porosité Pi, Chiralité Sociale chi_soc et l'Hamiltonien d'Égrégore.
"""

import math
import numpy as np
from typing import List, Dict, Any, Tuple

class CPCMetrics:
    @staticmethod
    def cognitive_dissonance(v_intention: np.ndarray, v_enonciation: np.ndarray) -> float:
        """Calcule la friction interne Delta_cog = || V_intention - V_enonciation ||"""
        return float(np.linalg.norm(v_intention - v_enonciation))

    @staticmethod
    def social_chirality(s_i: np.ndarray, s_j: np.ndarray) -> float:
        """Calcule la chiralité sociale chi_soc(i, j) = 1 - cos(S_i, S_j)"""
        norm_i = np.linalg.norm(s_i)
        norm_j = np.linalg.norm(s_j)
        if norm_i == 0 or norm_j == 0:
            return 1.0
        cos_sim = np.dot(s_i, s_j) / (norm_i * norm_j)
        cos_sim = max(-1.0, min(1.0, float(cos_sim)))
        return float(1.0 - cos_sim)

    @staticmethod
    def coupling_function_J(chi_soc: float, J_0: float = 1.0, lambda_rep: float = 50.0, kappa_att: float = 2.0) -> float:
        """
        Fonction de couplage dynamique non-linéaire:
        - Si chi_soc < 0.3 : Répulsion exponentielle forte (barrière anti-fusion)
        - Si chi_soc >= 0.3 : Attraction / émulation en tanh (Distance Sacrée)
        """
        if chi_soc < 0.3:
            return float(-J_0 * math.exp(lambda_rep * (0.3 - chi_soc)))
        else:
            return float(J_0 * math.tanh(kappa_att * (chi_soc - 0.5)))

    @staticmethod
    def regime_classifier(delta_cog: float, phi: float, porosity: float) -> str:
        """Détermine le régime cognitif en fonction des jauges d'état."""
        if porosity < 0.3 and delta_cog < 0.1:
            return "BLINDÉ / DOGMATIQUE"
        elif porosity > 0.8:
            return "COLLAPSE / DISSOLUTION"
        elif delta_cog > 0.8 and phi < 0.3:
            return "COLLAPSE / ZOMBIFICATION"
        elif 0.3 <= delta_cog <= 0.7 and phi >= 0.5 and 0.5 <= porosity <= 0.7:
            return "ZONE FERTILE / TENSION PRODUCTIVE"
        elif delta_cog < 0.2 and phi >= 0.8 and 0.5 <= porosity <= 0.7:
            return "SUPRACONDUCTEUR / FLOW"
        else:
            return "CONFORME / STANDARD"

class NodeAgent:
    def __init__(self, name: str, vector_s: np.ndarray, phi: float = 0.7, energy_e: float = 0.8, porosity: float = 0.6):
        self.name = name
        self.S = vector_s / np.linalg.norm(vector_s)
        self.phi = phi
        self.e = energy_e
        self.porosity = porosity

class EgregoreSystem:
    def __init__(self, nodes: List[NodeAgent]):
        self.nodes = nodes

    def compute_H_total(self) -> Tuple[float, float, float]:
        """Calcule H_total = H_individuel + H_interaction"""
        H_indiv = sum([-(n.phi * n.e) for n in self.nodes])
        H_int = 0.0
        n_count = len(self.nodes)

        for i in range(n_count):
            for j in range(i + 1, n_count):
                chi = CPCMetrics.social_chirality(self.nodes[i].S, self.nodes[j].S)
                J_ij = CPCMetrics.coupling_function_J(chi)
                cos_sim = float(np.dot(self.nodes[i].S, self.nodes[j].S))
                H_int -= J_ij * chi * cos_sim

        return float(H_indiv + H_int), float(H_indiv), float(H_int)