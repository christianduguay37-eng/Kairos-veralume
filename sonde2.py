#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sonde2.py — Six formes d'encodage, une seule destination.
            Combien de tokens pour arriver au même endroit ?

Le cadre est identique partout : "\nNom de l'élément :"
Ce qui change, c'est seulement la FORME de l'adresse.

  PERIPHRASE   description en langue naturelle
  ADRESSE      Z = 19                         ← le numéro nommé
  NUE          19                             ← le nombre seul, sans système
  TUPLE        (2, 8, 8, 1)                   ← couches, notre notation
  SPDF         1s2 2s2 2p6 3s2 3p6 4s1        ← notation standard
  ARBRE        la grammaire géométrique en texte

Mesure : rang du bon token, et tokens consommés.
Le rapport rang/token dit quelle forme travaille le plus fort.

    python3 sonde2.py --model /chemin/modele
"""

import argparse, csv, json, math, sys
import torch, torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

CADRE = "\nNom de l'élément :"

# Z, nom, symbole, périphrase, couches, notation spdf
ELEMENTS = [
    (1, "Hydrogène", "H", "le plus léger de tous les éléments, un seul électron",
     (1,), "1s1"),
    (6, "Carbone", "C", "quatre électrons de valence, base de la chimie du vivant",
     (2, 4), "1s2 2s2 2p2"),
    (8, "Oxygène", "O", "six électrons de valence, gaz diatomique indispensable à la respiration",
     (2, 6), "1s2 2s2 2p4"),
    (11, "Sodium", "Na", "métal alcalin de la troisième période, un électron de valence",
     (2, 8, 1), "1s2 2s2 2p6 3s1"),
    (17, "Chlore", "Cl", "halogène de la troisième période, sept électrons de valence",
     (2, 8, 7), "1s2 2s2 2p6 3s2 3p5"),
    (19, "Potassium", "K", "métal alcalin de la quatrième période, un électron de valence",
     (2, 8, 8, 1), "1s2 2s2 2p6 3s2 3p6 4s1"),
    (26, "Fer", "Fe", "métal de transition de la quatrième période, constituant du noyau terrestre",
     (2, 8, 14, 2), "1s2 2s2 2p6 3s2 3p6 3d6 4s2"),
    (29, "Cuivre", "Cu", "métal de transition rougeâtre, excellent conducteur électrique",
     (2, 8, 18, 1), "1s2 2s2 2p6 3s2 3p6 3d10 4s1"),
    (30, "Zinc", "Zn", "métal de transition, sous-couche d complète, sert à galvaniser l'acier",
     (2, 8, 18, 2), "1s2 2s2 2p6 3s2 3p6 3d10 4s2"),
    (47, "Argent", "Ag", "métal blanc, meilleur conducteur électrique de tous les métaux",
     (2, 8, 18, 18, 1), "[Kr] 4d10 5s1"),
    (79, "Or", "Au", "métal jaune, chimiquement très inerte, longtemps étalon monétaire",
     (2, 8, 18, 32, 18, 1), "[Xe] 4f14 5d10 6s1"),
    (82, "Plomb", "Pb", "métal lourd et mou de la sixième période, toxique",
     (2, 8, 18, 32, 18, 4), "[Xe] 4f14 5d10 6s2 6p2"),
]

CAPS = [2, 6, 10, 14]  # s p d f


def arbre_texte(couches):
    """La grammaire géométrique, rendue en texte.
    Un niveau par couche, capacités déclarées, remplissages donnés."""
    lignes = []
    for i, n in enumerate(couches, 1):
        reste, parts = n, []
        for c in CAPS:
            if reste <= 0:
                break
            parts.append(f"{min(reste, c)}/{c}")
            reste -= min(reste, c)
        lignes.append(f"niveau {i} : " + " + ".join(parts))
    return "arbre à " + str(len(couches)) + " niveaux ; " + " ; ".join(lignes)


def encodages(z, periphrase, couches, spdf):
    return {
        "PERIPHRASE": periphrase,
        "ADRESSE":    f"Z = {z}",
        "NUE":        f"{z}",
        "TUPLE":      f"couches {tuple(couches)}",
        "SPDF":       spdf,
        "ARBRE":      arbre_texte(couches),
    }


@torch.no_grad()
def sonder(model, tok, prompt, device):
    enc = tok(prompt, return_tensors="pt").to(device)
    lp = F.log_softmax(model(**enc).logits[0, -1, :].float(), dim=-1)
    return lp, enc["input_ids"].shape[1]


def cibles(tok, nom, symbole):
    """Nom ET symbole — le cadre peut appeler l'un ou l'autre."""
    out = {}
    for v in (" " + nom, nom, " " + nom.lower(), nom.lower(),
              " " + symbole, symbole):
        ids = tok.encode(v, add_special_tokens=False)
        if ids:
            out[v] = ids[0]
    return out


def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
    ap.add_argument("--device", default=None)
    ap.add_argument("--sortie", default="sonde2-resultats")
    a = ap.parse_args()

    dev = a.device or ("cuda" if torch.cuda.is_available()
                       else "mps" if torch.backends.mps.is_available() else "cpu")
    print(f"[*] {a.model} sur {dev}\n")

    tok = AutoTokenizer.from_pretrained(a.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype="auto", trust_remote_code=True).to(dev).eval()
    torch.manual_seed(0)

    FORMES = ["PERIPHRASE", "ADRESSE", "NUE", "TUPLE", "SPDF", "ARBRE"]
    lignes = []

    for z, nom, sym, per, couches, spdf in ELEMENTS:
        lp_null, n_null = sonder(model, tok, CADRE.lstrip("\n"), dev)

        # cible : meilleure variante jugée sous PERIPHRASE
        lp_per, _ = sonder(model, tok, f"{per}.{CADRE}", dev)
        variante, tid = max(cibles(tok, nom, sym).items(),
                            key=lambda kv: lp_per[kv[1]].item())

        r = {"Z": z, "element": nom, "variante": variante,
             "rang_NULL": int((lp_null > lp_null[tid]).sum()) + 1}

        for f, ctx in encodages(z, per, couches, spdf).items():
            lp, n = sonder(model, tok, f"{ctx}.{CADRE}", dev)
            r[f"rang_{f}"] = int((lp > lp[tid]).sum()) + 1
            r[f"tok_{f}"] = n - n_null          # coût net de l'encodage
            r[f"p_{f}"] = math.exp(lp[tid].item())

        r["retenu"] = r["rang_PERIPHRASE"] <= 5
        lignes.append(r)

        m = " " if r["retenu"] else "x"
        print(f"{m} Z={z:<3} {nom:<10} " +
              "  ".join(f"{f[:4]}={r[f'rang_{f}']:>5}/{r[f'tok_{f}']:>2}t"
                        for f in FORMES))

    g = [r for r in lignes if r["retenu"]]
    print(f"\n[*] {len(g)}/{len(lignes)} retenus (PERIPHRASE dans le top-5)")
    if not g:
        print("[!] le modèle ne porte pas la chimie — rien à lire")
        return

    def med(xs):
        xs = sorted(xs)
        return xs[len(xs) // 2]

    print("\n" + "=" * 58)
    print(f"{'forme':<12}{'rang méd.':>11}{'tokens méd.':>13}{'rang/token':>12}")
    print("=" * 58)
    print(f"{'(cadre nu)':<12}{med([r['rang_NULL'] for r in g]):>11}"
          f"{0:>13}{'—':>12}")
    for f in FORMES:
        rm = med([r[f"rang_{f}"] for r in g])
        tm = med([r[f"tok_{f}"] for r in g])
        print(f"{f:<12}{rm:>11}{tm:>13}{rm / max(tm, 1):>12.1f}")

    print("""
LECTURE
  NUE proche du cadre nu     un nombre sans système de coordonnées
                             ne pointe pas — le seuil n'est pas atteint
  ADRESSE ≪ NUE              les trois tokens « Z = » font tout le travail
  SPDF au niveau d'ADRESSE   plusieurs sous-chemins vers la même place
  TUPLE et ARBRE plus chers  ils portent la contrainte, pas juste l'adresse
""")

    json.dump(lignes, open(f"{a.sortie}.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    with open(f"{a.sortie}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(lignes[0]))
        w.writeheader(); w.writerows(lignes)
    print(f"[*] écrit : {a.sortie}.json / .csv")


if __name__ == "__main__":
    main()
