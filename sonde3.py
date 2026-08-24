#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sonde3.py — Le canal fermé.

Défaut des sondes 1 et 2 : l'encodage était symbolique, mais le CADRE
et la CIBLE restaient en français. On mesurait une notation branchée
sur une question humaine, pas un canal sans langue.

Ici le croisement est explicite. Deux axes indépendants :

  ENTRÉE   langue  = périphrase française
           symbole = notation spdf (aucun mot)

  SORTIE   langue  = « Nom de l'élément : »  → cible « Potassium »
           symbole = « → »                    → cible « K »

Quatre cellules :

           sortie langue    sortie symbole
  entrée
  langue      L→L               L→S
  symbole     S→L               S→S      ← le canal fermé

L→L est la référence. Si S→S tient au même niveau, aucun mot n'est
nécessaire dans le trajet.

Les colonnes NUE et ADRESSE sont conservées comme témoins : elles
mesurent le poids d'un seul caractère de convention.

    python3 sonde3.py --model /chemin/modele
"""

import argparse, csv, json, math, sys, statistics as st
import torch, torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

# ---- les deux cadres de sortie -------------------------------------------
CADRE_LANGUE  = "\nNom de l'élément :"
CADRE_SYMBOLE = " →"

# ---- Z, nom, symbole, périphrase, spdf -----------------------------------
ELEMENTS = [
    (1,  "Hydrogène", "H",  "le plus léger de tous les éléments, un seul électron",
         "1s1"),
    (6,  "Carbone",   "C",  "quatre électrons de valence, base de la chimie du vivant",
         "1s2 2s2 2p2"),
    (8,  "Oxygène",   "O",  "six électrons de valence, gaz diatomique indispensable à la respiration",
         "1s2 2s2 2p4"),
    (11, "Sodium",    "Na", "métal alcalin de la troisième période, un électron de valence",
         "1s2 2s2 2p6 3s1"),
    (17, "Chlore",    "Cl", "halogène de la troisième période, sept électrons de valence",
         "1s2 2s2 2p6 3s2 3p5"),
    (19, "Potassium", "K",  "métal alcalin de la quatrième période, un électron de valence",
         "1s2 2s2 2p6 3s2 3p6 4s1"),
    (26, "Fer",       "Fe", "métal de transition de la quatrième période, constituant du noyau terrestre",
         "1s2 2s2 2p6 3s2 3p6 3d6 4s2"),
    (29, "Cuivre",    "Cu", "métal de transition rougeâtre, excellent conducteur électrique",
         "1s2 2s2 2p6 3s2 3p6 3d10 4s1"),
    (30, "Zinc",      "Zn", "métal de transition, sous-couche d complète, sert à galvaniser l'acier",
         "1s2 2s2 2p6 3s2 3p6 3d10 4s2"),
    (17_000 + 47, "Argent", "Ag", "métal blanc, meilleur conducteur électrique de tous les métaux",
         "[Kr] 4d10 5s1"),          # Z corrigé plus bas
    (79, "Or",        "Au", "métal jaune, chimiquement très inerte, longtemps étalon monétaire",
         "[Xe] 4f14 5d10 6s1"),
    (82, "Plomb",     "Pb", "métal lourd et mou de la sixième période, toxique",
         "[Xe] 4f14 5d10 6s2 6p2"),
]
ELEMENTS[9] = (47,) + ELEMENTS[9][1:]

# Le français « or » est une conjonction très fréquente : sous cadre langue
# la cible serait le mot-outil, pas le métal. On force le symbole.
FORCER_SYMBOLE = {"Or"}


@torch.no_grad()
def sonder(model, tok, prompt, device):
    enc = tok(prompt, return_tensors="pt").to(device)
    lp = F.log_softmax(model(**enc).logits[0, -1, :].float(), dim=-1)
    return lp, enc["input_ids"].shape[1]


def premier_token(tok, s):
    ids = tok.encode(s, add_special_tokens=False)
    return ids[0] if ids else None


def cible_langue(tok, lp_ref, nom):
    """Meilleure variante du NOM, jugée sous la condition de référence."""
    cands = {}
    for v in (" " + nom, nom, " " + nom.lower(), nom.lower()):
        t = premier_token(tok, v)
        if t is not None:
            cands[v] = t
    return max(cands.items(), key=lambda kv: lp_ref[kv[1]].item())


def cible_symbole(tok, lp_ref, symbole):
    """Meilleure variante du SYMBOLE chimique. Aucun mot."""
    cands = {}
    for v in (" " + symbole, symbole):
        t = premier_token(tok, v)
        if t is not None:
            cands[v] = t
    return max(cands.items(), key=lambda kv: lp_ref[kv[1]].item())


def rang(lp, tid):
    return int((lp > lp[tid]).sum().item()) + 1


def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    ap.add_argument("--device", default=None)
    ap.add_argument("--sortie", default="sonde3-resultats")
    a = ap.parse_args()

    dev = a.device or ("cuda" if torch.cuda.is_available()
                       else "mps" if torch.backends.mps.is_available() else "cpu")
    print(f"[*] {a.model} sur {dev}\n")

    tok = AutoTokenizer.from_pretrained(a.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype="auto", trust_remote_code=True).to(dev).eval()
    torch.manual_seed(0)

    # entrée : (nom_condition, fonction -> texte)
    ENTREES = {
        "L": lambda z, per, spdf: per,          # langue
        "S": lambda z, per, spdf: spdf,         # symbole, aucun mot
        "ADRESSE": lambda z, per, spdf: f"Z = {z}",
        "NUE": lambda z, per, spdf: f"{z}",
    }
    SORTIES = {"L": CADRE_LANGUE, "S": CADRE_SYMBOLE}

    lignes = []
    for z, nom, sym, per, spdf in ELEMENTS:
        r = {"Z": z, "element": nom}

        # cadre nu, pour chaque sortie
        lp_nu = {}
        n_nu = {}
        for s, cadre in SORTIES.items():
            lp_nu[s], n_nu[s] = sonder(model, tok, cadre.lstrip("\n").lstrip(), dev)

        # référence pour choisir les cibles : L→L et L→S
        lp_LL, _ = sonder(model, tok, f"{per}.{CADRE_LANGUE}", dev)
        lp_LS, _ = sonder(model, tok, f"{per}{CADRE_SYMBOLE}", dev)

        if nom in FORCER_SYMBOLE:
            var_L, tid_L = cible_symbole(tok, lp_LL, sym)
        else:
            var_L, tid_L = cible_langue(tok, lp_LL, nom)
        var_S, tid_S = cible_symbole(tok, lp_LS, sym)
        r["cible_L"], r["cible_S"] = var_L, var_S

        for s in SORTIES:
            tid = tid_L if s == "L" else tid_S
            r[f"rang_NULL_{s}"] = rang(lp_nu[s], tid)

        for e, fab in ENTREES.items():
            ctx = fab(z, per, spdf)
            for s, cadre in SORTIES.items():
                sep = "." if s == "L" else ""
                lp, n = sonder(model, tok, f"{ctx}{sep}{cadre}", dev)
                tid = tid_L if s == "L" else tid_S
                cle = f"{e}->{s}"
                r[f"rang_{cle}"] = rang(lp, tid)
                r[f"tok_{cle}"] = n - n_nu[s]
                r[f"p_{cle}"] = math.exp(lp[tid].item())

        # garde : la référence humaine doit fonctionner
        r["retenu"] = r["rang_L->L"] <= 5
        lignes.append(r)

        m = " " if r["retenu"] else "x"
        print(f"{m} Z={z:<3} {nom:<10} "
              f"L->L={r['rang_L->L']:>5}  L->S={r['rang_L->S']:>5}  "
              f"S->L={r['rang_S->L']:>5}  S->S={r['rang_S->S']:>5}   "
              f"[cibles {r['cible_L']!r} / {r['cible_S']!r}]")

    g = [x for x in lignes if x["retenu"]]
    print(f"\n[*] {len(g)}/{len(lignes)} retenus (L->L dans le top-5)")
    if not g:
        print("[!] la référence humaine ne tient pas — rien à lire")
        return

    def med(k):
        return int(st.median([x[k] for x in g]))

    print("\n" + "=" * 60)
    print("RANG MÉDIAN — croisement entrée × sortie")
    print("=" * 60)
    print(f"{'':<14}{'sortie langue':>16}{'sortie symbole':>17}")
    print(f"{'cadre nu':<14}{med('rang_NULL_L'):>16}{med('rang_NULL_S'):>17}")
    print(f"{'entrée langue':<14}{med('rang_L->L'):>16}{med('rang_L->S'):>17}")
    print(f"{'entrée symbole':<14}{med('rang_S->L'):>16}{med('rang_S->S'):>17}")
    print(f"\n{'témoin Z =':<14}{med('rang_ADRESSE->L'):>16}{med('rang_ADRESSE->S'):>17}")
    print(f"{'témoin nu':<14}{med('rang_NUE->L'):>16}{med('rang_NUE->S'):>17}")

    print("\n" + "=" * 60)
    print("COÛT MÉDIAN EN TOKENS")
    print("=" * 60)
    for e in ENTREES:
        print(f"  {e:<10} ->L {med(f'tok_{e}->L'):>3}   ->S {med(f'tok_{e}->S'):>3}")

    print("""
LECTURE
  S->S au niveau de L->L
      le trajet complet se fait sans un mot. C'est la démonstration.
  S->S nettement pire que L->L
      quelque chose dans le cadre humain porte du travail — reste à voir
      si c'est le cadre d'entrée ou celui de sortie, et les deux cellules
      croisées (L->S et S->L) le disent.
  L->S ≈ S->S mais tous deux mauvais
      c'est le cadre de SORTIE qui casse : « → » n'est pas une convention
      assez forte pour appeler un symbole chimique. Essayer un autre.
""")

    json.dump(lignes, open(f"{a.sortie}.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    with open(f"{a.sortie}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(lignes[0]))
        w.writeheader(); w.writerows(lignes)
    print(f"[*] écrit : {a.sortie}.json / .csv")


if __name__ == "__main__":
    main()
