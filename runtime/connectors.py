"""
RUNTIME CONNECTORS - Interfaces d'Inférence Multi-Modèles
Supporte LM Studio, Ollama, OpenAI-compatible et Offline Deterministic Engine.
"""

from typing import Dict, Any, Optional
import urllib.request
import json

class LLMConnector:
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

class OfflineDeterministicConnector(LLMConnector):
    """Moteur hors-ligne déterministe pour résolution instantanée d'incidents Kairos."""

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        prompt_lower = prompt.lower()
        if "split_brain" in prompt_lower or "quorum" in prompt_lower:
            return "domain:cluster_ha|split_brain_quorum_lost|sev:P0|auto_quarantine|requires:check_heartbeat_loss>2s|prevents:concurrent_data_corruption|fix:stonith_node(secondary)>fence_shared_storage>force_master_read_only|section:ha_orchestrator"
        elif "thundering_herd" in prompt_lower or "cache" in prompt_lower:
            return "domain:cache_layer|thundering_herd_stampede|sev:P1|circuit_breaker_on|requires:cache_miss_rate>85%|prevents:db_connection_pool_exhaustion|fix:decouple_circuit(auth_service)>enable_probabilistic_early_expiration>apply_exponential_backoff_jitter|section:gateway_proxy"
        elif "mobius" in prompt_lower or "boucle" in prompt_lower or "recursiv" in prompt_lower:
            return "domain:alert_pipeline|recursive_telemetry_loop|sev:P0|cut_feed|requires:self_referential_alert_metric|prevents:log_buffer_saturation_oom|fix:loop(alert>metric>alert)+break_at(metric_ingest)>flush_telemetry_queue|section:telemetry_daemon"
        elif "byzantin" in prompt_lower or "traitor" in prompt_lower or "divergence" in prompt_lower:
            return "domain:consensus_engine|byzantine_fault_detected|sev:P0|isolate_node|requires:divergent_vector_signature>threshold|prevents:state_fork_corruption|fix:decouple_circuit(node_malicious)>force_view_change>resync_state_quorum|section:consensus_core"
        else:
            return f"domain:general_system|standard_state_evaluation|sev:P3|normal|requires:none|prevents:none|fix:log_state>monitor_health|section:system_monitor"

class LMStudioConnector(LLMConnector):
    def __init__(self, endpoint: str = "http://localhost:1234/v1"):
        self.endpoint = endpoint.rstrip("/") + "/chat/completions"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt or "You are Kairos V5 deterministic compiler."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0,
            "max_tokens": 128
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.endpoint, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode("utf-8"))
            return res["choices"][0]["message"]["content"].strip()