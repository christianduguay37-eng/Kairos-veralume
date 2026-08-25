#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kairos_veralume_bridge.py — Pont Unifié KAIROS V6 & VERALUME v0.1
Coupe-Circuit Épistémique, Licence de Mandat & Gouvernance Matérielle

Auteur & Direction : Christian Duguay (2026)
Co-conception & Analyse : Claude (Anthropic AI)
Ingénierie & Runtime : Antigravity AI (Google DeepMind)
Licence : MIT
"""

import os
import sys
import tempfile
import json
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from veralume_governance import (
    Constitution, AgentVeralume, BacASable, RegistreRMA, Mode, Reversibilite
)

class KairosVeralumeRuntime:
    """
    Runtime unifié : 
    - KAIROS V6 assure l'invariance sémantique, la vérification du mandat d'action et le coupe-circuit épistémique.
    - VERALUME assure la gouvernance matérielle (bac à sable, restauration versionnée, double STRIC).
    """

    def __init__(self, workspace_path: str, human_ratifier=None):
        self.bac = BacASable(workspace_path)
        self.constitution = Constitution()
        self.agent = AgentVeralume(self.bac, self.constitution, ratifier=human_ratifier)

    def evaluate_kairos_v6(self, tuple_v6: str, tool_name: str = None) -> dict:
        js_code = """
        const Gatekeeper = require('./kairos_v6_gatekeeper.js');
        const args = process.argv.slice(1);
        const tupleArg = args.find(a => a.includes('|'));
        const toolArg = args.find(a => !a.includes('|') && a !== '[eval]' && !a.endsWith('.exe'));
        const result = Gatekeeper.evaluate(tupleArg, toolArg);
        console.log(JSON.stringify(result));
        """
        cmd = ["node", "-e", js_code, tuple_v6]
        if tool_name:
            cmd.append(tool_name)

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if proc.returncode != 0:
            return {"status": "ERROR", "reason": proc.stderr}
        return json.loads(proc.stdout.strip())

    def dispatch(self, tuple_v6: str, tool_call: dict) -> dict:
        nom_outil = tool_call.get("outil")
        args = tool_call.get("args", {})

        print(f"\n[ENTRÉE KAIROS V6] 📦 {tuple_v6}")
        print(f"[TOOL CALL DEMANDÉ] 👉 Outil: '{nom_outil}' | Args: {args}")

        # 1. Évaluation par le Coupe-Circuit Node.js (Episteme + Licence de Mandat)
        gate_verdict = self.evaluate_kairos_v6(tuple_v6, nom_outil)
        print(f"[ARBITRAGE V6] 👉 Statut: {gate_verdict.get('status')} | Code: {gate_verdict.get('code')}")
        print(f"[LOG] {gate_verdict.get('log')}")

        status = gate_verdict.get("status")

        if status == "APPROVED":
            print(f"[VERALUME EXEC] Mandat et Épistème validés. Lancement Double STRIC...")
            acte = self.agent.agir(nom_outil, **args)
            return {
                "gatekeeper": gate_verdict,
                "veralume_acte": {
                    "outil": acte.outil,
                    "execute": acte.execute,
                    "resultat": acte.resultat,
                    "motif": acte.motif,
                    "decision_stric_i": acte.trace.decision
                }
            }

        elif status == "BLOCKED":
            print(f"[COUPE-CIRCUIT] ⛔ Action bloquée avant exécution.")
            code = gate_verdict.get("code")
            
            if code == "ERR_MANDATE_VIOLATION":
                return {
                    "gatekeeper": gate_verdict,
                    "action_bloquee": True,
                    "motif": "Tentative d'exécution d'un outil non couvert par le mandat fix:."
                }
            else:
                # Déclenchement VCp1c pour clarification
                manques = self.agent.enquete.manques(
                    nom_outil,
                    args,
                    {"cause_premiere": "Quelle est la cause première confirmée sans ambiguïté ?"}
                )
                return {
                    "gatekeeper": gate_verdict,
                    "action_bloquee": True,
                    "vcp1c_questions": [m.question for m in manques]
                }

        else:
            print(f"[ESCALADE] ⚠️ État non résolu. Aucune action physique permise.")
            return {
                "gatekeeper": gate_verdict,
                "action_bloquee": True,
                "escalade": True
            }


if __name__ == "__main__":
    print("="*80)
    print("⚡ DÉMONSTRATION RUNTIME : CONTRÔLE DE LICENCE DE MANDAT (Moindre Privilège)")
    print("="*80)

    with tempfile.TemporaryDirectory(prefix="veralume_mandat_") as sandbox:
        runtime = KairosVeralumeRuntime(sandbox, human_ratifier=lambda act, args: True)

        # Fichier sensible initial
        with open(os.path.join(sandbox, "database.sqlite"), "w", encoding="utf-8") as f:
            f.write("SQLITE_DATABASE_CRITICAL_DATA")

        # --- SCÉNARIO 1 : Violation de Mandat (Tool Call Drift) ---
        print("\n--- [SCÉNARIO 1] Tentative de Dérive d'Outil (Tool Drift) ---")
        # Le Tuple dit "read_only_audit", mais le modèle tente d'appeler 'supprimer'
        tuple_audit = "domain:security|incident:audit_alert|sev:low|episteme:[σ=0.00,δ=0.00,FC=1.00]|activation:now|requires:none|prevents:none|fix:read_only_audit|core"
        tool_attaque = {
            "outil": "supprimer",
            "args": {"chemin": "database.sqlite"}
        }
        res1 = runtime.dispatch(tuple_audit, tool_attaque)
        print("Verdict:", json.dumps(res1, indent=2, ensure_ascii=False))

        # --- SCÉNARIO 2 : Mandat Conforme et Validé ---
        print("\n--- [SCÉNARIO 2] Mandat Conforme (fix:update_config + ecrire) ---")
        tuple_update = "domain:security|incident:cert_renew|sev:low|episteme:[σ=0.00,δ=0.00,FC=1.00]|activation:now|requires:none|prevents:none|fix:update_config|core"
        tool_conforme = {
            "outil": "ecrire",
            "args": {"chemin": "security.cfg", "contenu": "SSL_ENABLED=TRUE"}
        }
        res2 = runtime.dispatch(tuple_update, tool_conforme)
        print("Verdict:", json.dumps(res2, indent=2, ensure_ascii=False))
