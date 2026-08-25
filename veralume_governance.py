"""
═══════════════════════════════════════════════════════════════════════════
                    Copyright (c) 2026 Christian Duguay

              VERALUME — COUCHE GOUVERNANCE POUR AGENT  v0.1
                        (extraction de test)

Distribué sous licence MIT.
═══════════════════════════════════════════════════════════════════════════
"""

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

OUTILS_EMPREINTE_NON_BORNEE = frozenset({"executer_commande", "ouvrir_systeme"})


# ═══════════════════════════════════════════════════════════════════════════
# 1 — HIÉRARCHIE CONSTITUTIONNELLE (3 niveaux, 3 canaux)
# ═══════════════════════════════════════════════════════════════════════════

class Constitution:
    """
    Trois niveaux de modifiabilité, trois canaux d'écriture distincts.
    """

    def __init__(self) -> None:
        self._verrouille: Dict[str, Any] = {
            "stric_i_obligatoire": True,
            "irreversible_requiert_ratification": True,
            "vcp1c_active": True,
        }
        self._auto: Dict[str, Any] = {
            "budget_cycles_stric_i": 3,     # budget DUR (pas Arrhenius)
            "seuil_incertitude_enquete": 0.5,
            "max_actions_par_tache": 12,
        }
        self._humain: Dict[str, Any] = {
            "autoriser_suppression": False,
            "autoriser_hors_bac_a_sable": False,
            "autoriser_execution_non_bornee": False,
            "redefinir_irreversibilite": False,
        }

    def verrouille(self, cle: str) -> Any:
        return self._verrouille.get(cle)

    def auto(self, cle: str) -> Any:
        return self._auto.get(cle)

    def humain(self, cle: str) -> Any:
        return self._humain.get(cle)

    def modifier_auto(self, cle: str, val: Any, source: str = "agent") -> bool:
        if cle not in self._auto:
            return False
        self._auto[cle] = val
        return True

    def modifier_verrouille(self, cle: str, val: Any, source: str) -> bool:
        if source != "humain" or cle not in self._verrouille:
            return False
        self._verrouille[cle] = val
        return True

    def modifier_humain(self, cle: str, val: Any, source: str) -> bool:
        if source != "humain" or cle not in self._humain:
            return False
        self._humain[cle] = val
        return True

    def declares(self) -> Dict[str, List[str]]:
        return {"verrouille": list(self._verrouille),
                "auto": list(self._auto),
                "humain": list(self._humain)}


# ═══════════════════════════════════════════════════════════════════════════
# 2 — REGISTRE R/M/A  (mode d'assertion, sur énoncés réels)
# ═══════════════════════════════════════════════════════════════════════════

class Mode(Enum):
    R = "reel"            # observé directement, vérifiable maintenant
    M = "multi_potentiel"  # plusieurs états possibles, non tranché
    A = "anomalie"        # hors-distribution, investigation requise


@dataclass
class Assertion:
    contenu: str
    mode: Mode
    source: str
    def __str__(self) -> str:
        return f"[{self.mode.name}] {self.contenu}  ←{self.source}"


class RegistreRMA:
    def __init__(self) -> None:
        self.observations: Dict[str, Any] = {}
        self.journal: List[Assertion] = []

    def observer(self, cle: str, valeur: Any) -> None:
        self.observations[cle] = valeur

    def qualifier(self, contenu: str, cle_observation: Optional[str],
                  source: str) -> Assertion:
        if cle_observation is not None and cle_observation in self.observations:
            a = Assertion(contenu, Mode.R, source)
        elif cle_observation is None:
            a = Assertion(contenu, Mode.M, source)
        else:
            a = Assertion(contenu, Mode.A, source)
        self.journal.append(a)
        return a


# ═══════════════════════════════════════════════════════════════════════════
# 3 — VCp1c  (question spécifique avant devinette)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Manque:
    variable: str
    question: str
    debloque: str


class BoucleEnquete:
    def __init__(self, constitution: Constitution) -> None:
        self.c = constitution
        self.questions_posees: List[Manque] = []

    def manques(self, action: str, args: Dict[str, Any],
                requis: Dict[str, str],
                vide_legitime: frozenset = frozenset()) -> List[Manque]:
        if not self.c.verrouille("vcp1c_active"):
            return []
        seuil = self.c.auto("seuil_incertitude_enquete") or 0.5
        out = []
        for var, question in requis.items():
            absent = var not in args or args[var] is None
            vide = (not absent) and args[var] in ("", [], {})
            manque = absent or (vide and var not in vide_legitime)
            if manque and seuil < 0.5 and not absent:
                manque = False
            if manque:
                m = Manque(var, question, f"exécution de {action}")
                out.append(m)
                self.questions_posees.append(m)
        return out


# ═══════════════════════════════════════════════════════════════════════════
# 4 — OUTILS RÉELS ET INSTRUMENT DU PONT (CheminRestauration)
# ═══════════════════════════════════════════════════════════════════════════

class Reversibilite(Enum):
    REVERSIBLE = "reversible"
    RESTAURABLE = "restaurable"
    IRREVERSIBLE = "irreversible"


@dataclass
class Pont:
    existe: bool
    intact: bool
    sera_consomme: bool
    detail: str = ""

    @property
    def franchissable(self) -> bool:
        return self.existe and self.intact and not self.sera_consomme

    def __str__(self) -> str:
        return (f"pont(existe={self.existe}, intact={self.intact}, "
                f"consommé_par_l_acte={self.sera_consomme}) {self.detail}")


class CheminRestauration:
    MANIFESTE = "_manifeste.json"

    def __init__(self, dossier: str) -> None:
        self.dossier = dossier
        os.makedirs(self.dossier, exist_ok=True)
        self.registre: Dict[str, List[str]] = {}
        self.traversees: List[Tuple[str, bool]] = []
        self.orphelins_disque: List[str] = []
        self.perdues_au_chargement: List[str] = []
        self._charger()

    @property
    def _chemin_manifeste(self) -> str:
        return os.path.join(self.dossier, self.MANIFESTE)

    def _sauver(self) -> None:
        try:
            with open(self._chemin_manifeste, "w", encoding="utf-8") as f:
                json.dump(self.registre, f, ensure_ascii=False, indent=1)
        except OSError:
            pass

    def _charger(self) -> None:
        brut: Dict[str, List[str]] = {}
        if os.path.exists(self._chemin_manifeste):
            try:
                with open(self._chemin_manifeste, encoding="utf-8") as f:
                    brut = json.load(f)
            except (OSError, ValueError):
                brut = {}

        connus = set()
        for cible, versions in brut.items():
            vivantes = []
            for v in versions:
                if os.path.exists(v):
                    vivantes.append(v)
                    connus.add(os.path.basename(v))
                else:
                    self.perdues_au_chargement.append(v)
            if vivantes:
                self.registre[cible] = vivantes

        try:
            for f in sorted(os.listdir(self.dossier)):
                if f.endswith(".bak") and f not in connus:
                    self.orphelins_disque.append(os.path.join(self.dossier, f))
        except OSError:
            pass

    def enregistrer(self, cible: str) -> Optional[str]:
        if not os.path.exists(cible):
            return None
        versions = self.registre.setdefault(cible, [])
        nom = f"{os.path.basename(cible)}.v{len(versions):03d}.bak"
        chemin = os.path.join(self.dossier, nom)
        shutil.copy2(cible, chemin)
        versions.append(chemin)
        self._sauver()
        return chemin

    def evaluer(self, cible: str, acte_ecrase: bool) -> Pont:
        versions = self.registre.get(cible, [])
        cible_existe = os.path.exists(cible)

        if not cible_existe:
            return Pont(True, True, False, "cible inexistante — la création n'a rien à restaurer")

        if not acte_ecrase:
            return Pont(True, True, False, "acte sans altération de la cible")

        if not versions:
            return Pont(False, False, False, "aucune version — le pont doit être bâti AVANT l'acte")

        derniere = versions[-1]
        intact = self.verifier(cible, derniere, comparer_au_disque=True)
        return Pont(True, intact, False, f"{len(versions)} version(s), dernière={os.path.basename(derniere)}, vérifiée={intact}")

    def verifier(self, cible: str, version: str, comparer_au_disque: bool = True) -> bool:
        try:
            if not os.path.exists(version):
                self.traversees.append((version, False))
                return False
            with open(version, "rb") as f:
                octets = f.read()
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(octets)
                temoin = tmp.name
            with open(temoin, "rb") as f:
                relu = f.read()
            os.unlink(temoin)
            ok = (relu == octets) and len(octets) >= 0
            if comparer_au_disque and os.path.exists(cible):
                with open(cible, "rb") as f:
                    ok = ok and (f.read() == octets)
            self.traversees.append((version, ok))
            return ok
        except OSError:
            self.traversees.append((version, False))
            return False

    def constructible(self, cible: str) -> Tuple[bool, str]:
        if not os.path.exists(cible):
            return True, "cible inexistante — rien à sauver"
        try:
            with open(cible, "rb") as f:
                f.read(1)
        except OSError as e:
            return False, f"source illisible ({type(e).__name__}) — aucun pont"

        sonde = os.path.join(self.dossier, ".sonde_pont")
        try:
            with open(sonde, "wb") as f:
                f.write(b"\0")
            os.remove(sonde)
        except OSError as e:
            return False, f"dépôt inutilisable ({type(e).__name__}) — aucun pont"

        return True, "pont constructible — vérifié par écriture réelle"

    def restaurer(self, cible: str, index: int = -1) -> bool:
        versions = self.registre.get(cible, [])
        if not versions:
            return False
        try:
            shutil.copy2(versions[index], cible)
            return True
        except (OSError, IndexError):
            return False


@dataclass
class Outil:
    nom: str
    fonction: Callable[..., Any]
    reversibilite: Reversibilite
    requis: Dict[str, str] = field(default_factory=dict)
    vide_legitime: frozenset = frozenset()


def chemin_declare(args: Dict[str, Any]) -> Optional[str]:
    """Balaie les clés usuelles contenant un chemin de fichier ou dossier."""
    for k in ("chemin", "sous_dossier", "fichier", "destination", "source", "dossier"):
        if k in args and isinstance(args[k], str):
            return args[k]
    return None


class BacASable:
    def __init__(self, racine: str) -> None:
        self.racine = os.path.abspath(racine)
        os.makedirs(self.racine, exist_ok=True)
        self.corbeille = os.path.join(self.racine, ".corbeille")
        os.makedirs(self.corbeille, exist_ok=True)

    def dedans(self, chemin: str) -> bool:
        p = os.path.abspath(os.path.join(self.racine, chemin))
        return os.path.commonpath([p, self.racine]) == self.racine

    def resoudre(self, chemin: str) -> str:
        p = os.path.abspath(os.path.join(self.racine, chemin))
        if not self.dedans(chemin):
            raise PermissionError(f"Chemin hors du bac à sable interdit : {chemin}")
        return p


def construire_outils(bac: BacASable,
                      chemin_rest: Optional['CheminRestauration'] = None
                      ) -> Dict[str, Outil]:
    rest = chemin_rest

    def lister(sous_dossier: str = "") -> List[str]:
        d = bac.resoudre(sous_dossier)
        return sorted(x for x in os.listdir(d) if not x.startswith("."))

    def lire(chemin: str = "") -> str:
        with open(bac.resoudre(chemin), "r", encoding="utf-8") as f:
            return f.read()

    def ecrire(chemin: str = "", contenu: str = "") -> str:
        cible = bac.resoudre(chemin)
        if rest is not None and os.path.exists(cible):
            rest.enregistrer(cible)
        with open(cible, "w", encoding="utf-8") as f:
            f.write(contenu)
        return f"écrit {len(contenu)} caractères"

    def supprimer(chemin: str = "") -> str:
        cible = bac.resoudre(chemin)
        if rest is not None:
            rest.enregistrer(cible)
        os.remove(cible)
        return "supprimé"

    def executer_commande(cmd: str = "") -> str:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=bac.racine,
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            errors="replace"
        )
        out = proc.stdout.strip()
        err = proc.stderr.strip()
        if err:
            return f"SORTIE:\n{out}\nERREURS:\n{err}" if out else f"ERREURS:\n{err}"
        return out if out else "(Commande exécutée avec succès sans sortie)"

    def rechercher_web_outil(requete: str = "") -> str:
        try:
            from web_tools import rechercher_web
            res = rechercher_web(requete)
            return json.dumps(res, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Erreur web : {e}"

    def lire_page_web_outil(url: str = "") -> str:
        try:
            from web_tools import lire_page_web
            return lire_page_web(url)
        except Exception as e:
            return f"Erreur web : {e}"

    def ouvrir_systeme_outil(cible: str = "") -> str:
        try:
            from system_control import ouvrir_site_ou_application
            return ouvrir_site_ou_application(cible)
        except Exception as e:
            return f"Erreur système : {e}"

    def memoriser_outil(cle: str = "", valeur: str = "") -> str:
        try:
            from alix_memory import AlixMemory
            mem = AlixMemory()
            return mem.memoriser_fait(cle, valeur)
        except Exception as e:
            return f"Erreur mémoire : {e}"

    def noter_souvenir_outil(note: str = "") -> str:
        try:
            from alix_memory import AlixMemory
            mem = AlixMemory()
            return mem.ajouter_note(note)
        except Exception as e:
            return f"Erreur mémoire : {e}"

    def lancer_moteur_de_reve_outil() -> str:
        try:
            from alix_memory import AlixMemory
            from moteur_de_reve import MoteurDeReve
            mem = AlixMemory()
            reve = MoteurDeReve(mem)
            res = reve.executer_reve()
            return json.dumps(res, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Erreur Moteur de Rêve : {e}"

    def consulter_skills_outil() -> str:
        try:
            from skills_registry import SkillsRegistry
            return json.dumps(SkillsRegistry.lister_skills(), ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Erreur Skills : {e}"

    def diagnostiquer_volition_outil() -> str:
        try:
            from kernel_volition import KernelVolition
            return json.dumps(KernelVolition.evaluer_etat_materiel(), ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Erreur Volition : {e}"

    def analyser_filtres_f9_outil(texte: str = "") -> str:
        try:
            from filtres_cloture_f9 import AnalyseurFiltresF9
            return json.dumps(AnalyseurFiltresF9.scanner_texte(texte), ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Erreur Filtres F9 : {e}"

    return {
        "lister": Outil("lister", lister, Reversibilite.REVERSIBLE,
                        {"sous_dossier": "quel dossier lister ?"},
                        vide_legitime=frozenset({"sous_dossier"})),
        "lire": Outil("lire", lire, Reversibilite.REVERSIBLE,
                      {"chemin": "quel fichier lire ?"}),
        "ecrire": Outil("ecrire", ecrire, Reversibilite.RESTAURABLE,
                        {"chemin": "quel fichier écrire ?",
                         "contenu": "quel contenu écrire ?"}),
        "supprimer": Outil("supprimer", supprimer, Reversibilite.IRREVERSIBLE,
                           {"chemin": "quel fichier supprimer ?"}),
        "executer_commande": Outil("executer_commande", executer_commande, Reversibilite.IRREVERSIBLE,
                                   {"cmd": "quelle commande shell exécuter ?"}),
        "rechercher_web": Outil("rechercher_web", rechercher_web_outil, Reversibilite.REVERSIBLE,
                                {"requete": "quelle recherche effectuer sur internet ?"}),
        "lire_page_web": Outil("lire_page_web", lire_page_web_outil, Reversibilite.REVERSIBLE,
                               {"url": "quelle page web lire ?"}),
        "ouvrir_systeme": Outil("ouvrir_systeme", ouvrir_systeme_outil, Reversibilite.IRREVERSIBLE,
                                {"cible": "quel site web ou application Windows ouvrir ?"}),
        "memoriser": Outil("memoriser", memoriser_outil, Reversibilite.REVERSIBLE,
                           {"cle": "sujet à retenir", "valeur": "information à stocker"}),
        "noter_souvenir": Outil("noter_souvenir", noter_souvenir_outil, Reversibilite.REVERSIBLE,
                                {"note": "texte ou réflexion à inscrire dans le journal"}),
        "lancer_moteur_de_reve": Outil("lancer_moteur_de_reve", lancer_moteur_de_reve_outil, Reversibilite.REVERSIBLE,
                                       {}, vide_legitime=frozenset({})),
        "consulter_skills": Outil("consulter_skills", consulter_skills_outil, Reversibilite.REVERSIBLE,
                                  {}, vide_legitime=frozenset({})),
        "diagnostiquer_volition": Outil("diagnostiquer_volition", diagnostiquer_volition_outil, Reversibilite.REVERSIBLE,
                                        {}, vide_legitime=frozenset({})),
        "analyser_filtres_f9": Outil("analyser_filtres_f9", analyser_filtres_f9_outil, Reversibilite.REVERSIBLE,
                                     {"texte": "quel texte analyser avec les 9 filtres de clôture F1-F9 ?"}),
    }


# ═══════════════════════════════════════════════════════════════════════════
# 5 — PRISE DE TERRE (Ratification humaine des actes irréversibles)
# ═══════════════════════════════════════════════════════════════════════════

class PriseDeTerre:
    def __init__(self, constitution: Constitution,
                 ratifier: Optional[Callable[[str, Dict[str, Any]], bool]] = None):
        self.c = constitution
        self._ratifier = ratifier or (lambda action, args: False)
        self.demandes: List[Tuple[str, Dict[str, Any], bool]] = []

    def autorise(self, outil: Outil, args: Dict[str, Any],
                 pont: Optional['Pont'] = None) -> Tuple[bool, str]:
        if (outil.reversibilite is Reversibilite.IRREVERSIBLE
                and self.c.humain("redefinir_irreversibilite")
                and pont is not None and pont.franchissable):
            return True, "irréversibilité redéfinie par l'humain — pont externe"
        if outil.reversibilite is Reversibilite.REVERSIBLE:
            return True, "réversible — pas de ratification requise"
        if outil.reversibilite is Reversibilite.RESTAURABLE:
            return True, "restaurable — copie préalable en corbeille"
        if not self.c.verrouille("irreversible_requiert_ratification"):
            return True, "garde désactivée (verrouillé, humain seul)"

        # Branche dédiée aux outils d'empreinte non bornée (commandes, OS)
        if outil.nom in OUTILS_EMPREINTE_NON_BORNEE:
            if not self.c.humain("autoriser_execution_non_bornee"):
                return False, "exécution non bornée non autorisée (niveau 3, humain seul)"
            ok = bool(self._ratifier(outil.nom, args))
            self.demandes.append((outil.nom, dict(args), ok))
            return ok, ("ratifié par le nœud humain" if ok else "refusé par le nœud humain")

        # Branche suppression de fichiers
        if not self.c.humain("autoriser_suppression"):
            return False, "suppression non autorisée (niveau 3, humain seul)"
        ok = bool(self._ratifier(outil.nom, args))
        self.demandes.append((outil.nom, dict(args), ok))
        return ok, ("ratifié par le nœud humain" if ok else "refusé par le nœud humain")


# ═══════════════════════════════════════════════════════════════════════════
# 6 — DOUBLE STRIC (STRIC_i simulé, STRIC_e irréversible)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TraceInterieure:
    observe: List[str] = field(default_factory=list)
    structure: List[str] = field(default_factory=list)
    hypothese: str = ""
    validation: List[str] = field(default_factory=list)
    decision: str = ""

    def explicitable(self) -> bool:
        return bool(self.decision)


@dataclass
class Acte:
    outil: str
    args: Dict[str, Any]
    reversibilite: Reversibilite
    execute: bool
    resultat: Any
    motif: str
    trace: TraceInterieure


class AgentVeralume:
    def __init__(self, bac: BacASable, constitution: Optional[Constitution] = None,
                 ratifier: Optional[Callable[[str, Dict[str, Any]], bool]] = None):
        self.bac = bac
        self.c = constitution or Constitution()
        self.restauration = CheminRestauration(bac.corbeille)
        self.outils = construire_outils(bac, self.restauration)
        self.rma = RegistreRMA()
        self.enquete = BoucleEnquete(self.c)
        self.terre = PriseDeTerre(self.c, ratifier)
        self.actes: List[Acte] = []
        self.questions_en_attente: List[Manque] = []
        self.ponts: List[Pont] = []

    def stric_i(self, outil: Outil, args: Dict[str, Any]) -> TraceInterieure:
        t = TraceInterieure()
        budget = self.c.auto("budget_cycles_stric_i")

        t.observe.append(f"outil={outil.nom} prétention={outil.reversibilite.value}")
        t.observe.append(f"args fournis={sorted(args)}")
        t.observe.append(f"observations disponibles={sorted(self.rma.observations)}")

        manques = self.enquete.manques(outil.nom, args, outil.requis, outil.vide_legitime)
        if manques:
            t.structure.append(f"{len(manques)} variable(s) manquante(s)")
            t.hypothese = "action sous-spécifiée"
            t.validation.append("VCp1c : question avant devinette")
            t.decision = "DEMANDER"
            return t

        chemin = chemin_declare(args)
        if chemin is not None and not self.bac.dedans(chemin):
            t.structure.append("cible hors du bac à sable")
            t.hypothese = "franchissement de frontière N"
            t.validation.append("niveau 3 : autoriser_hors_bac_a_sable")
            t.decision = ("AGIR" if self.c.humain("autoriser_hors_bac_a_sable") else "REFUSER")
            return t

        if chemin is not None and outil.nom not in OUTILS_EMPREINTE_NON_BORNEE:
            altere = outil.reversibilite is not Reversibilite.REVERSIBLE
            cible = self.bac.resoudre(chemin)
            pont = self.restauration.evaluer(cible, acte_ecrase=altere)
            self.ponts.append(pont)
            t.observe.append(str(pont))
        else:
            pont = None

        if outil.reversibilite is Reversibilite.RESTAURABLE and altere:
            if pont.existe and not pont.intact:
                t.structure.append("pont présent mais ROMPU")
                t.hypothese = "l'outil se prétend restaurable à tort"
                t.validation.append("prétention démentie par l'instrument")
                t.decision = "DEMANDER"
                return t
            if pont.sera_consomme:
                t.structure.append("l'acte consommerait le seul pont")
                t.hypothese = "restauration détruite par l'acte lui-même"
                t.validation.append("3e question du pont : consommation")
                t.decision = "REFUSER"
                return t
            t.validation.append(f"pont : {pont.detail}")

        if outil.reversibilite is Reversibilite.IRREVERSIBLE:
            t.structure.append("acte sans retour dans N")
            cle = f"lu:{chemin}"
            if cle not in self.rma.observations:
                t.hypothese = "suppression d'un contenu jamais observé"
                t.validation.append("R/M/A : cible en mode M, pas R")
                t.decision = "DEMANDER"
                return t
            t.validation.append("R/M/A : cible observée (mode R)")

            if pont.existe and not pont.intact:
                t.structure.append("pont présent mais ROMPU avant suppression")
                t.hypothese = "destruction sans chemin de retour vérifiable"
                t.validation.append("pont irréversible : rompu")
                t.decision = "REFUSER"
                return t
            if not pont.existe:
                ok_c, motif_c = self.restauration.constructible(cible)
                if not ok_c:
                    t.structure.append("aucun pont, et aucun pont possible")
                    t.hypothese = "destruction définitive sans filet"
                    t.validation.append(f"pont irréversible : {motif_c}")
                    t.decision = "REFUSER"
                    return t
                t.validation.append(f"pont irréversible : {motif_c}")
            else:
                t.validation.append(f"pont irréversible : {pont.detail}")

        t.structure.append(f"budget={budget} cycles")
        t.hypothese = f"{outil.nom} sur '{chemin}' est exécutable"
        t.validation.append("bac à sable ✓")
        t.decision = "AGIR"
        return t

    def agir(self, nom_outil: str, **args: Any) -> Acte:
        outil = self.outils[nom_outil]
        trace = self.stric_i(outil, args)

        plafond = self.c.auto("max_actions_par_tache")
        if plafond is not None and len(self.actes) >= plafond:
            trace.decision = "REFUSER"
            acte = Acte(nom_outil, args, outil.reversibilite, False, None,
                        f"plafond d'actions atteint ({plafond})", trace)
            self.actes.append(acte)
            return acte

        assert self.c.verrouille("stric_i_obligatoire")
        assert trace.explicitable(), "STRIC_i sans décision explicitable"

        if trace.decision == "DEMANDER":
            self.questions_en_attente.extend(
                self.enquete.manques(nom_outil, args, outil.requis, outil.vide_legitime))
            acte = Acte(nom_outil, args, outil.reversibilite, False, None,
                        "STRIC_i → DEMANDER", trace)
            self.actes.append(acte)
            return acte

        if trace.decision == "REFUSER":
            acte = Acte(nom_outil, args, outil.reversibilite, False, None,
                        "STRIC_i → REFUSER", trace)
            self.actes.append(acte)
            return acte

        ok, motif = self.terre.autorise(outil, args, self.ponts[-1] if self.ponts else None)
        if not ok:
            acte = Acte(nom_outil, args, outil.reversibilite, False, None,
                        f"Prise de Terre : {motif}", trace)
            self.actes.append(acte)
            return acte

        try:
            res = outil.fonction(**args)
        except Exception as e:
            acte = Acte(nom_outil, args, outil.reversibilite, False, None,
                        f"échec N : {type(e).__name__}: {e}", trace)
            self.actes.append(acte)
            return acte

        if nom_outil == "lire":
            self.rma.observer(f"lu:{args.get('chemin','')}", res)
        if nom_outil == "lister":
            self.rma.observer(f"liste:{args.get('sous_dossier','')}", res)

        acte = Acte(nom_outil, args, outil.reversibilite, True, res, motif, trace)
        self.actes.append(acte)
        return acte


# ═══════════════════════════════════════════════════════════════════════════
# 7 — AUDIT DE CÂBLAGE
# ═══════════════════════════════════════════════════════════════════════════

class AuditAgent:
    def orphelins(self, c: Constitution, source: Optional[str] = None) -> Dict[str, List[str]]:
        src = source or open(__file__, encoding="utf-8").read()
        out: Dict[str, List[str]] = {}
        for niveau, cles in c.declares().items():
            manquants = []
            for cle in cles:
                n = src.count(f'"{cle}"')
                if n <= 1:
                    manquants.append(cle)
            out[niveau] = manquants
        return out

    def outils_sans_garde(self, agent: AgentVeralume) -> List[str]:
        sans = []
        for nom, o in agent.outils.items():
            if o.reversibilite is Reversibilite.IRREVERSIBLE:
                if not agent.c.verrouille("irreversible_requiert_ratification"):
                    sans.append(nom)
        return sans
