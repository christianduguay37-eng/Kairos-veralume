"""
TESTS UNITAIRES - Compilateur & Parser Kairos V5
"""

import unittest
from kairos_core.parser import KairosParser, KairosTuple
from kairos_core.operators import KairosOperator
from kairos_core.executor import KairosExecutor

class TestKairosCore(unittest.TestCase):

    def test_parse_valid_tuple(self):
        tuple_str = "domain:cluster_ha|split_brain|sev:P0|auto|requires:loss>2s|prevents:data_loss|fix:stonith_node(sec)>fence_disk|section:orchestrator"
        kt = KairosParser.parse(tuple_str)
        self.assertEqual(kt.domain, "cluster_ha")
        self.assertEqual(kt.pathology, "split_brain")
        self.assertEqual(kt.severity, "sev:P0")
        self.assertEqual(kt.requires, ["loss", "2s"])
        self.assertEqual(kt.prevents, ["data_loss"])
        self.assertEqual(len(kt.fix_actions), 2)
        self.assertEqual(kt.target_section, "orchestrator")

    def test_recursive_breaker_operator(self):
        op_info = KairosOperator.parse_loop_break("loop(alert>metric>alert)+break_at(metric)")
        self.assertTrue(op_info["is_loop"])
        self.assertEqual(op_info["break_node"], "metric")
        self.assertEqual(op_info["cycle"], ["alert", "metric", "alert"])

    def test_stonith_operator(self):
        op_info = KairosOperator.parse_stonith("stonith_node(node_secondary)")
        self.assertTrue(op_info["is_stonith"])
        self.assertEqual(op_info["target_node"], "node_secondary")

    def test_executor_plan_generation(self):
        tuple_str = "domain:cache|stampede|P1|on|requires:miss>85%|prevents:oom|fix:decouple_circuit(auth)>apply_backoff|gateway"
        kt = KairosParser.parse(tuple_str)
        executor = KairosExecutor()
        report = executor.execute(kt, dry_run=True)
        self.assertTrue(report["success"])
        self.assertGreaterEqual(report["total_steps"], 3)

if __name__ == "__main__":
    unittest.main()