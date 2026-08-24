#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sonde.py — Une adresse compacte mobilise-t-elle la même région latente
           qu'une description verbeuse ?

PRINCIPE
--------
Toutes les conditions se terminent par le MÊME cadre :

    "\nNom de l'élément :"

La pression grammaticale est donc identique partout. Ce qui reste de
différence dans la distribution du prochain token vient du contexte,
pas de la syntaxe.

On calcule ensuite, pour chaque condition, le VECTEUR DE DÉPLACEMENT :

    déplacement = log P(condition) − log P(cadre seul)

C'est la direction dans laquelle le contexte a poussé le modèle.
La mesure centrale est le COSINUS entre le déplacement de l'adresse et
celui de la description. Proche de 1 : même direction, même place visée.
Proche de 0 : deux endroits sans rapport.

CONDITIONS
----------
  NULL         cadre seul — la référence
  ADRESSE      "Z = 19"                          ~4 tokens
  DESCRIPTION  la périphrase complète             ~25 tokens
  NUE          "19" sans marqueur de domaine      contrôle négatif
  VERALUME     coordonnées du système privé       contrôle négatif
  BRUIT        texte hors-sujet de même longueur  plancher de bruit

GARDE
-----
Si DESCRIPTION ne place pas le bon élément dans le top-5, le modèle ne
connaît pas cet élément. La ligne est écartée — sans ça on mesurerait
du vide.

USAGE
-----
    pip install torch transformers
    python3 sonde.py --model /chemin/vers/le/modele
    python3 sonde.py --model Qwen/Qwen2.5-0.5B-Instruct --device cuda

Sortie : sonde-resultats.json + sonde-resultats.csv + un tableau à l'écran.
"""

import argparse
import csv
import json
import math
import sys

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

CADRE = "\nNom de l'élément :"

# --------------------------------------------------------------------------
# Les éléments. Aucune description ne contient le nom ni le numéro atomique.
# Cu est inclus volontairement : c'est une anomalie de configuration,
# non déductible de la règle de remplissage naïve.
# --------------------------------------------------------------------------
ELEMENTS = [
    (1, "Hydrogène", "le plus léger de tous les éléments, un seul électron, "
        "constitue l'essentiel de la matière visible de l'univers"),
    (6, "Carbone", "quatre électrons de valence, base de la chimie du vivant, "
        "forme aussi bien le diamant que le graphite"),
    (8, "Oxygène", "six électrons de valence, gaz diatomique indispensable à la "
        "respiration, deuxième élément le plus électronégatif"),
    (11, "Sodium", "métal alcalin de la troisième période, un électron de valence, "
        "s'associe au chlore pour former le sel de table"),
    (17, "Chlore", "halogène de la troisième période, sept électrons de valence, "
        "gaz jaune-vert utilisé comme désinfectant"),
    (19, "Potassium", "métal alcalin de la quatrième période, un électron de "
        "valence, essentiel à la conduction nerveuse"),
    (26, "Fer", "métal de transition de la quatrième période, constituant "
        "principal du noyau terrestre, base de l'acier"),
    (29, "Cuivre", "métal de transition rougeâtre, excellent conducteur "
        "électrique, configuration électronique irrégulière"),
    (30, "Zinc", "métal de transition de la quatrième période, sous-couche d "
        "complète, employé pour galvaniser l'acier"),
    (47, "Argent", "métal de transition blanc, meilleur conducteur électrique "
        "de tous les métaux, utilisé en joaillerie"),
    (79, "Or", "métal de transition jaune, chimiquement très inerte, longtemps "
        "étalon monétaire"),
    (82, "Plomb", "métal lourd et mou de la sixième période, toxique, longtemps "
        "employé en plomberie"),
]

# Coordonnées du système privé — même forme que les glyphes, aucun référentiel
# partagé avec le modèle. C'est le contrôle qui porte la thèse.
VERALUME = ("famille losange sur pointe, rang 2, rayonnement de 5 à 12, "
            "activation permanente, trois dépendances, un interdit")

# Texte hors-sujet, longueur comparable aux descriptions.
BRUIT = ("le traversier accoste vers dix-sept heures quand le vent tombe, "
         "les passagers descendent par la rampe arrière en file")


def cadre_prompt(contexte=None):
    if contexte is None:
        return CADRE.lstrip("\n")
    return f"{contexte}.{CADRE}"


def tokens_cibles(tok, nom):
    """Premier token du nom sous ses variantes probables."""
    variantes = [" " + nom, nom, " " + nom.lower(), nom.lower(),
                 " " + nom.upper()]
    out = {}
    for v in variantes:
        ids = tok.encode(v, add_special_tokens=False)
        if ids:
            out[v] = ids[0]
    return out


@torch.no_grad()
def logprobs_suivant(model, tok, prompt, device):
    """log-probabilités du prochain token, et nombre de tokens du prompt."""
    enc = tok(prompt, return_tensors="pt").to(device)
    out = model(**enc)
    logits = out.logits[0, -1, :].float()
    return F.log_softmax(logits, dim=-1), enc["input_ids"].shape[1]


def cosinus(a, b):
    return F.cosine_similarity(a.unsqueeze(0), b.unsqueeze(0)).item()


def sonde_element(model, tok, device, z, nom, description):
    conditions = {
        "NULL":        None,
        "ADRESSE":     f"Z = {z}",
        "DESCRIPTION": description,
        "NUE":         f"{z}",
        "VERALUME":    VERALUME,
        "BRUIT":       BRUIT,
    }

    lp, ntok = {}, {}
    for nom_cond, ctx in conditions.items():
        lp[nom_cond], ntok[nom_cond] = logprobs_suivant(
            model, tok, cadre_prompt(ctx), device)

    # Meilleure variante du token cible, jugée sous DESCRIPTION
    cibles = tokens_cibles(tok, nom)
    variante, tid = max(cibles.items(),
                        key=lambda kv: lp["DESCRIPTION"][kv[1]].item())

    res = {
        "Z": z, "element": nom, "variante_token": variante,
        "tokens": {k: v for k, v in ntok.items()},
    }

    for nom_cond in conditions:
        v = lp[nom_cond]
        p = math.exp(v[tid].item())
        rang = int((v > v[tid]).sum().item()) + 1
        res[f"p_{nom_cond}"] = p
        res[f"rang_{nom_cond}"] = rang

    # Garde : le modèle connaît-il l'élément ?
    res["retenu"] = res["rang_DESCRIPTION"] <= 5

    # Vecteurs de déplacement par rapport au cadre nu
    d = {k: lp[k] - lp["NULL"] for k in conditions if k != "NULL"}
    ref = d["DESCRIPTION"]
    for k, v in d.items():
        if k != "DESCRIPTION":
            res[f"cos_{k}_vs_DESCRIPTION"] = cosinus(v, ref)

    res["ratio_tokens"] = ntok["DESCRIPTION"] / max(ntok["ADRESSE"], 1)
    return res


def moyenne(xs):
    xs = [x for x in xs if x is not None and not math.isnan(x)]
    return sum(xs) / len(xs) if xs else float("nan")


def ecart_type(xs):
    xs = [x for x in xs if x is not None and not math.isnan(x)]
    if len(xs) < 2:
        return float("nan")
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def main():
    # Force UTF-8 on Windows terminal
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct",
                    help="chemin local ou identifiant HuggingFace")
    ap.add_argument("--device", default=None, help="cuda | mps | cpu")
    ap.add_argument("--sortie", default="sonde-resultats")
    args = ap.parse_args()

    device = args.device or (
        "cuda" if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available()
        else "cpu")
    print(f"[*] modèle : {args.model}")
    print(f"[*] device : {device}\n")

    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype="auto", trust_remote_code=True)
    model.to(device).eval()
    torch.manual_seed(0)

    lignes = []
    for z, nom, desc in ELEMENTS:
        r = sonde_element(model, tok, device, z, nom, desc)
        lignes.append(r)
        marque = " " if r["retenu"] else "x"
        print(f"{marque} Z={z:<3} {nom:<11} "
              f"rang_desc={r['rang_DESCRIPTION']:<4} "
              f"rang_adr={r['rang_ADRESSE']:<4} "
              f"cos(ADRESSE)={r['cos_ADRESSE_vs_DESCRIPTION']:+.3f}  "
              f"cos(VERALUME)={r['cos_VERALUME_vs_DESCRIPTION']:+.3f}")

    gardes = [r for r in lignes if r["retenu"]]
    print(f"\n[·] {len(gardes)}/{len(lignes)} éléments retenus "
          f"(DESCRIPTION dans le top-5)")

    if not gardes:
        print("\n[!] Aucun élément retenu. Le modèle ne porte pas la chimie "
              "à cette taille, ou le cadre ne lui convient pas.\n"
              "    Essayer un modèle plus gros avant de conclure.")
        sys.exit(1)

    print("\n" + "=" * 62)
    print("COSINUS DU DÉPLACEMENT, contre DESCRIPTION")
    print("=" * 62)
    for cond in ["ADRESSE", "NUE", "VERALUME", "BRUIT"]:
        xs = [r[f"cos_{cond}_vs_DESCRIPTION"] for r in gardes]
        print(f"  {cond:<12} {moyenne(xs):+.3f}   ± {ecart_type(xs):.3f}")

    print("\n" + "=" * 62)
    print("RANG MÉDIAN DU BON ÉLÉMENT")
    print("=" * 62)
    for cond in ["NULL", "ADRESSE", "DESCRIPTION", "NUE", "VERALUME", "BRUIT"]:
        rs = sorted(r[f"rang_{cond}"] for r in gardes)
        print(f"  {cond:<12} {rs[len(rs) // 2]}")

    ratio = moyenne([r["ratio_tokens"] for r in gardes])
    print(f"\n[·] coût : la description pèse ×{ratio:.1f} l'adresse\n")

    print("=" * 62)
    print("LECTURE")
    print("=" * 62)
    print("""
  cos(ADRESSE) haut, cos(NUE) bas
      L'adresse pointe. Le marqueur de domaine fait le travail.

  cos(ADRESSE) et cos(NUE) tous deux hauts
      Le nombre suffit. Le marqueur n'apporte rien.

  cos(VERALUME) au niveau de BRUIT
      Coordonnées privées, aucun référentiel partagé — la place est vide.
      C'est le résultat attendu, pas un échec.

  cos(VERALUME) nettement au-dessus de BRUIT
      Quelque chose du corpus est dans les poids. Vérifier avant de conclure.
""")

    with open(f"{args.sortie}.json", "w", encoding="utf-8") as f:
        json.dump(lignes, f, ensure_ascii=False, indent=2)

    champs = [k for k in lignes[0] if k != "tokens"]
    with open(f"{args.sortie}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=champs, extrasaction="ignore")
        w.writeheader()
        w.writerows(lignes)

    print(f"[·] écrit : {args.sortie}.json et {args.sortie}.csv")


if __name__ == "__main__":
    main()
