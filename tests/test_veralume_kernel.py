"""
TESTS UNITAIRES - Noyau Veralume & Métriques CPC
"""

import unittest
import numpy as np
from veralume_kernel.metrics import CPCMetrics, NodeAgent, EgregoreSystem
from veralume_kernel.chronos import ChronosAnchor
from veralume_kernel.cerbere import CerbereSentinel

class TestVeralumeKernel(unittest.TestCase):

    def test_social_chirality_barrier(self):
        s1 = np.array([1.0, 0.0, 0.0, 0.0])
        s2 = np.array([0.99, 0.01, 0.0, 0.0]) # Presque fusion
        chi = CPCMetrics.social_chirality(s1, s2)
        self.assertLess(chi, 0.3)
        J = CPCMetrics.coupling_function_J(chi)
        self.assertLess(J, -10.0) # Répulsion forte confirmée

    def test_sacred_distance(self):
        s1 = np.array([1.0, 0.0, 0.0, 0.0])
        s2 = np.array([0.5, 0.866, 0.0, 0.0]) # Angle ~ 60 deg -> cos ~ 0.5 -> chi ~ 0.5
        chi = CPCMetrics.social_chirality(s1, s2)
        self.assertAlmostEqual(chi, 0.5, delta=0.05)
        audit = CerbereSentinel.audit_social_distance(s1, s2)
        self.assertTrue(audit["is_sacred"])
        self.assertEqual(audit["status"], "DISTANCE_SACREE")

    def test_chronos_anchor(self):
        anchor = ChronosAnchor()
        res1 = anchor.extract_and_anchor("[22:30] Premier message")
        self.assertTrue(res1["has_prefix"])
        self.assertEqual(res1["current_time_str"], "22:30")
        
        res2 = anchor.extract_and_anchor("[22:35] Second message")
        self.assertEqual(res2["delta_seconds"], 300)
        self.assertIn("5m 0s", res2["delta_formatted"])

if __name__ == "__main__":
    unittest.main()