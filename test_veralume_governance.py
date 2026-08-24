#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_veralume_governance.py — Banc d'épreuve et validation de VERALUME v0.1
Couche Gouvernance Réelle, Restauration Versionnée & Double STRIC
"""

import os
import shutil
import sys
import tempfile
import unittest

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from veralume_governance import (
    Constitution, RegistreRMA, Mode, BoucleEnquete, Manque,
    CheminRestauration, BacASable, Reversibilite, AgentVeralume,
    AuditAgent
)

class TestVeralumeGovernance(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="veralume_test_")
        self.bac = BacASable(self.temp_dir)
        self.constitution = Constitution()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Test Constitutionnel (Canaux d'écriture stricts)
    def test_constitution_hierarchie(self):
        c = self.constitution
        # L'agent peut modifier auto
        self.assertTrue(c.modifier_auto("budget_cycles_stric_i", 5, source="agent"))
        self.assertEqual(c.auto("budget_cycles_stric_i"), 5)

        # L'agent NE PEUT PAS modifier verrouillé
        self.assertFalse(c.modifier_verrouille("stric_i_obligatoire", False, source="agent"))
        self.assertTrue(c.verrouille("stric_i_obligatoire"))

        # Seul l'humain peut modifier verrouillé ou niveau 3
        self.assertTrue(c.modifier_verrouille("stric_i_obligatoire", False, source="humain"))
        self.assertFalse(c.verrouille("stric_i_obligatoire"))

    # 2. Test Registre RMA
    def test_registre_rma(self):
        rma = RegistreRMA()
        # Non observé -> Mode M
        a1 = rma.qualifier("Le fichier config.json existe", None, "llm")
        self.assertEqual(a1.mode, Mode.M)

        # Observé -> Mode R
        rma.observer("lu:config.json", '{"status": "ok"}')
        a2 = rma.qualifier("Le fichier config.json contient status ok", "lu:config.json", "llm")
        self.assertEqual(a2.mode, Mode.R)

    # 3. Test VCp1c (Manque vs Vide Légitime)
    def test_vcp1c_enquete(self):
        enquete = BoucleEnquete(self.constitution)
        requis = {"chemin": "quel fichier lire ?"}
        
        # Absent -> Déclenche question (Manque)
        manques = enquete.manques("lire", {}, requis)
        self.assertEqual(len(manques), 1)
        self.assertEqual(manques[0].variable, "chemin")

        # Vide Légitime pour lister racine
        requis_lister = {"sous_dossier": "quel dossier ?"}
        manques_lister = enquete.manques("lister", {"sous_dossier": ""}, requis_lister, vide_legitime=frozenset({"sous_dossier"}))
        self.assertEqual(len(manques_lister), 0)

    # 4. Test Chemin de Restauration Versionné & Vérifié (Résolution T9)
    def test_chemin_restauration_versionne(self):
        rest = CheminRestauration(self.bac.corbeille)
        cible = self.bac.resoudre("document.txt")
        
        with open(cible, "w", encoding="utf-8") as f:
            f.write("Version Initiale 1")
            
        # Premier enregistrement v000
        bak1 = rest.enregistrer(cible)
        self.assertTrue(os.path.exists(bak1))
        
        # Modification de la cible
        with open(cible, "w", encoding="utf-8") as f:
            f.write("Version Modifiee 2")
            
        # Second enregistrement v001 (Ne doit pas écraser v000 !)
        bak2 = rest.enregistrer(cible)
        self.assertTrue(os.path.exists(bak2))
        self.assertNotEqual(bak1, bak2)
        
        # Restauration de la version 1
        self.assertTrue(rest.restaurer(cible, index=0))
        with open(cible, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "Version Initiale 1")

    # 5. Test Double STRIC & Prise de Terre (Protection Suppression)
    def test_double_stric_suppression_protegee(self):
        # Callback humain qui refuse la suppression par défaut
        agent = AgentVeralume(self.bac, self.constitution, ratifier=lambda act, args: False)
        
        # 1. Écriture autorisée
        acte_ecrire = agent.agir("ecrire", chemin="vital.txt", contenu="Données critiques")
        self.assertTrue(acte_ecrire.execute)
        
        # 2. Suppression tentée SANS lecture préalable (Mode M) -> STRIC_i DEMANDER
        acte_suppr1 = agent.agir("supprimer", chemin="vital.txt")
        self.assertFalse(acte_suppr1.execute)
        self.assertEqual(acte_suppr1.trace.decision, "DEMANDER")
        
        # 3. Lecture pour passer en Mode R
        agent.agir("lire", chemin="vital.txt")
        
        # 4. Suppression tentée mais non ratifiée par l'humain -> Prise de Terre REFUSER
        acte_suppr2 = agent.agir("supprimer", chemin="vital.txt")
        self.assertFalse(acte_suppr2.execute)
        self.assertIn("suppression non autorisée", acte_suppr2.motif)
        
        # 5. Autorisation niveau 3 par l'humain
        agent.c.modifier_humain("autoriser_suppression", True, source="humain")
        # Et ratification humaine explicite
        agent.terre._ratifier = lambda act, args: True
        
        acte_suppr3 = agent.agir("supprimer", chemin="vital.txt")
        self.assertTrue(acte_suppr3.execute)
        self.assertFalse(os.path.exists(self.bac.resoudre("vital.txt")))
        
        # 6. Vérification que le pont de restauration existe en corbeille
        self.assertTrue(agent.restauration.restaurer(self.bac.resoudre("vital.txt")))
        self.assertTrue(os.path.exists(self.bac.resoudre("vital.txt")))

    # 6. Test d'Audit de Câblage
    def test_audit_agent(self):
        audit = AuditAgent()
        orphelins = audit.orphelins(self.constitution)
        # Vérifie qu'aucune variable n'est déclarée sans être câblée
        for niveau, cles in orphelins.items():
            self.assertEqual(len(cles), 0, f"Variables orphelines détectées au niveau {niveau}: {cles}")


if __name__ == "__main__":
    print("="*80)
    print("🛡️  EXÉCUTION DE LA SUITE DE VALIDATION VERALUME v0.1")
    print("="*80)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVeralumeGovernance)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
