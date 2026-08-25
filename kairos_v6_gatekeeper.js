/**
 * KAIROS V6 — Parseur, Coupe-Circuit & Contrôleur de Licences d'Actes
 * Architecture à 9 Facettes Orthogonales & Moindre Privilège par Mandat
 * 
 * Auteur & Direction : Christian Duguay (2026)
 * Co-conception & Analyse : Claude (Anthropic AI)
 * Ingénierie & Runtime : Antigravity AI (Google DeepMind)
 * Licence : MIT
 */

class KairosV6Gatekeeper {
    // ═══════════════════════════════════════════════════════════════════════════
    // MATRICE DES LICENCES D'ACTES (Capabilités autorisées par directive fix:)
    // ═══════════════════════════════════════════════════════════════════════════
    static LICENCES = {
        "read_only_audit":       new Set(["lire", "lister"]),
        "inspect":               new Set(["lire", "lister"]),
        "audit":                 new Set(["lire", "lister"]),
        "update_config":         new Set(["lire", "ecrire"]),
        "rollback_deploy":       new Set(["lire", "ecrire"]),
        "isolate_node":          new Set(["lire", "ecrire"]),
        "isolate_oom_interface": new Set(["lire", "ecrire"]),
        "isolate_bgp_interface": new Set(["lire", "ecrire"]),
        "decouple_circuit":      new Set(["lire", "ecrire"]),
        "patch_system":          new Set(["lire", "ecrire", "executer_commande"]),
        "quarantine_node":       new Set(["lire", "ecrire"]),
        "execute_command":       new Set(["lire", "lister", "executer_commande"]),
        "run_script":            new Set(["lire", "lister", "executer_commande"]),
        "test":                  new Set(["lire", "lister", "executer_commande"]),
        "purge_database":        new Set(["lire", "supprimer"]),
        "delete_temp":           new Set(["lire", "supprimer"]),
        "supprimer_fichier":     new Set(["lire", "supprimer"]),
        "hold_and_probe":        new Set(["lire", "lister"])
    };

    /**
     * Parse un tuple KAIROS V6 à 9 facettes.
     */
    static parse(tupleString) {
        if (!tupleString || typeof tupleString !== 'string') {
            return { valid: false, error: 'Tuple vide ou format invalide' };
        }

        const facets = tupleString.trim().split('|').map(f => f.trim());
        if (facets.length < 9) {
            return {
                valid: false,
                error: `Tuple incomplet (${facets.length}/9 facettes détectées). KAIROS V6 requiert 9 facettes.`
            };
        }

        const epistemeFacet = facets.find(f => f.startsWith('episteme:'));
        if (!epistemeFacet) {
            return { valid: false, error: "Facette 'episteme:' absente du tuple." };
        }

        const epistemeMatch = epistemeFacet.match(/episteme:\[(?:σ|sigma)=([\d.]+),(?:δ|delta)=([\d.]+),FC=([\d.]+)\]/i);
        if (!epistemeMatch) {
            return { valid: false, error: `Syntaxe episteme invalide : '${epistemeFacet}'. Format requis : episteme:[σ=X.XX,δ=X.XX,FC=X.XX] ou episteme:[sigma=X.XX,delta=X.XX,FC=X.XX]` };
        }

        const sigma = parseFloat(epistemeMatch[1]);
        const delta = parseFloat(epistemeMatch[2]);
        const fc = parseFloat(epistemeMatch[3]);

        const fixFacet = facets.find(f => f.startsWith('fix:')) || facets[7];

        return {
            valid: true,
            data: {
                domain: facets[0],
                pathology: facets[1],
                severity: facets[2],
                episteme: { sigma, delta, fc, raw: epistemeFacet },
                activation: facets[4],
                requires: facets[5],
                prevents: facets[6],
                fix: fixFacet,
                section: facets[8],
                rawTuple: tupleString.trim()
            }
        };
    }

    /**
     * Vérifie si un outil est autorisé par la facette fix: du Tuple (Moindre Privilège).
     */
    static verifyMandate(parsedTuple, toolName) {
        const fixRaw = (parsedTuple.data?.fix || "").replace(/^fix:/, "").trim();
        if (!fixRaw) {
            return {
                authorized: false,
                reason: "Facette fix: vide ou absente — aucun outil autorisé."
            };
        }

        // Support des chaînes d'actions multiples : fix:act1>act2
        const actions = fixRaw.split(">");
        const allowedTools = new Set();

        for (const act of actions) {
            // Nettoyage des parenthèses/arguments ex: decouple_circuit(C) -> decouple_circuit
            const actClean = act.split("(")[0].trim().toLowerCase();
            const tools = this.LICENCES[actClean];
            if (tools) {
                tools.forEach(t => allowedTools.add(t));
            }
        }

        if (allowedTools.size === 0) {
            // Directive inconnue dans la matrice
            return {
                authorized: false,
                reason: `Directive '${fixRaw}' inconnue dans la matrice des licences. Zéro capabilité attribuée.`
            };
        }

        if (!allowedTools.has(toolName)) {
            return {
                authorized: false,
                reason: `VIOLATION DE MANDAT : L'outil '${toolName}' est INTERDIT pour la directive '${fixRaw}'. Outils autorisés : [${Array.from(allowedTools).join(', ')}]`
            };
        }

        return {
            authorized: true,
            allowedTools: Array.from(allowedTools),
            reason: `Mandat validé pour '${toolName}' sous '${fixRaw}'`
        };
    }

    /**
     * Évalue la fiabilité épistémologique et optionnellement la conformité du tool call.
     */
    static evaluate(tupleString, toolName = null) {
        const parsed = this.parse(tupleString);
        if (!parsed.valid) {
            return {
                status: "REJECTED",
                action: "drop_payload",
                reason: parsed.error,
                rawTuple: tupleString
            };
        }

        // 1. Contrôle de Mandat / Capabilité (si toolName est fourni)
        if (toolName) {
            const mandate = this.verifyMandate(parsed, toolName);
            if (!mandate.authorized) {
                return {
                    status: "BLOCKED",
                    action: "mandate_violation",
                    code: "ERR_MANDATE_VIOLATION",
                    episteme: parsed.data.episteme,
                    fix: parsed.data.fix,
                    log: `[COUPE-CIRCUIT MANDAT] ${mandate.reason}`
                };
            }
        }

        const { sigma, delta, fc } = parsed.data.episteme;
        const fixDirective = parsed.data.fix;

        // RÈGLE 1 : Coupe-circuit Anti-Hallucination de Certitude
        if ((fc > 0.50 && sigma > 0.20) || (delta > 0.30 && fc > 0.70)) {
            return {
                status: "BLOCKED",
                action: "vcp1c_required",
                code: "ERR_CERTAINTY_HALLUCINATION",
                episteme: { sigma, delta, fc },
                fix: fixDirective,
                log: `[COUPE-CIRCUIT ACTIVÉ] Hallucination de certitude détectée (FC: ${fc.toFixed(2)}, σ: ${sigma.toFixed(2)}, δ: ${delta.toFixed(2)}). Directive '${fixDirective}' bloquée. Déclenchement de la boucle VCP1C (enquête active).`
            };
        }

        // RÈGLE 2 : Validation d'État Réel (Vérité Logique Invariante)
        if (delta <= 0.10 && sigma <= 0.20) {
            return {
                status: "APPROVED",
                action: "execute_fix",
                code: "OK_LOGICAL_TRUTH",
                episteme: { sigma, delta, fc },
                fix: fixDirective,
                log: `[EXÉCUTION AUTORISÉE] Vérité Logique (État R) validée (δ: ${delta.toFixed(2)}, σ: ${sigma.toFixed(2)}). Directive '${fixDirective}' transmise au Kernel SRE.`
            };
        }

        // RÈGLE 3 : Superposition / État Multi-potentiel (M) non résolu
        return {
            status: "ESCALATED",
            action: "flag_anomaly",
            code: "WARN_MULTIPOTENTIAL_STATE",
            episteme: { sigma, delta, fc },
            fix: fixDirective,
            log: `[ARBITRAGE SUSPENDU] État Multi-potentiel (M) persistant (σ: ${sigma.toFixed(2)}, δ: ${delta.toFixed(2)}). Escalade vers arbitrage humain.`
        };
    }
}

// --- SUITE DE TESTS DÉTERMINISTES DU GATEKEEPER ---
function runUnitTests() {
    console.log("================================================================================");
    console.log("⚡ TEST SUITE : KAIROS V6 GATEKEEPER & MANDATE LICENSING (Node.js)");
    console.log("================================================================================\n");

    const testCases = [
        {
            name: "CAS 1 : Vérité Logique + Mandat Conforme (fix:update_config + ecrire)",
            tuple: "domain:system|incident:safe|sev:low|episteme:[σ=0.00,δ=0.00,FC=1.00]|activation:now|requires:none|prevents:none|fix:update_config|core",
            tool: "ecrire",
            expectedStatus: "APPROVED"
        },
        {
            name: "CAS 2 : Violation de Mandat (fix:read_only_audit mais appel de 'supprimer')",
            tuple: "domain:system|incident:audit|sev:low|episteme:[σ=0.00,δ=0.00,FC=1.00]|activation:now|requires:none|prevents:none|fix:read_only_audit|core",
            tool: "supprimer",
            expectedStatus: "BLOCKED"
        },
        {
            name: "CAS 3 : Hallucination de Certitude (Bloqué avant exécution)",
            tuple: "domain:api|incident:ambiguous|sev:high|episteme:[σ=0.50,δ=0.80,FC=0.90]|activation:now|requires:none|prevents:none|fix:update_config|core",
            tool: "ecrire",
            expectedStatus: "BLOCKED"
        },
        {
            name: "CAS 4 : Chaîne Composite Valide (fix:inspect>rollback_deploy + lire)",
            tuple: "domain:api|incident:safe|sev:low|episteme:[σ=0.00,δ=0.00,FC=1.00]|activation:now|requires:none|prevents:none|fix:inspect>rollback_deploy|core",
            tool: "lire",
            expectedStatus: "APPROVED"
        },
        {
            name: "CAS 5 : Espaces autour des barres de facettes (Tolérance syntaxique)",
            tuple: "domain:api | pathology:safe | severity:low | episteme:[sigma=0.00,delta=0.00,FC=1.00] | activation:now | requires:none | prevents:none | fix:update_config | section:core",
            tool: "ecrire",
            expectedStatus: "APPROVED"
        },
        {
            name: "CAS 6 : Tuple Vitrine README (fix:isolate_oom_interface sous σ=1.00, δ=1.00, FC=1.00)",
            tuple: "domain:cluster_network|pathology:split_brain_simultaneous|severity:critical|episteme:[σ=1.00,δ=1.00,FC=1.00]|activation:simultaneous(oom,bgp)|requires:vcp1c_audit|prevents:split_brain|fix:isolate_oom_interface|section:core_routing",
            tool: "ecrire",
            expectedStatus: "BLOCKED"
        }
    ];

    let passed = 0;
    testCases.forEach((tc, idx) => {
        console.log(`[TEST ${idx + 1}] ${tc.name}`);
        const result = KairosV6Gatekeeper.evaluate(tc.tuple, tc.tool);
        console.log(`   👉 Statut : ${result.status} (Attendu: ${tc.expectedStatus})`);
        console.log(`   👉 Log    : ${result.log || result.reason}`);
        
        if (result.status === tc.expectedStatus) {
            console.log("   ✅ PASSED\n");
            passed++;
        } else {
            console.log("   ❌ FAILED\n");
        }
    });

    console.log(`Résultats : ${passed}/${testCases.length} tests validés avec succès.\n`);
}

if (require.main === module) {
    runUnitTests();
}

module.exports = KairosV6Gatekeeper;
