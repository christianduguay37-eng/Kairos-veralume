/**
 * VERALUME × KAIROS V6 — Frontend Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatHistory = document.getElementById('chatHistory');
    const sendBtn = document.getElementById('sendBtn');
    const modelSelector = document.getElementById('modelSelector');
    
    // Telemetry Elements
    const sigmaVal = document.getElementById('sigmaVal');
    const deltaVal = document.getElementById('deltaVal');
    const fcVal = document.getElementById('fcVal');
    const gatekeeperBadge = document.getElementById('gatekeeperBadge');
    const gatekeeperLog = document.getElementById('gatekeeperLog');
    
    // Performance Elements
    const speedVal = document.getElementById('speedVal');
    const tokensVal = document.getElementById('tokensVal');
    const elapsedVal = document.getElementById('elapsedVal');
    
    // Veralume Sandbox Elements
    const traceBody = document.getElementById('traceBody');
    const filesList = document.getElementById('filesList');
    const backupsList = document.getElementById('backupsList');
    const refreshSandboxBtn = document.getElementById('refreshSandboxBtn');
    
    // Modal Elements
    const vcp1cModal = document.getElementById('vcp1cModal');
    const vcp1cQuestionText = document.getElementById('vcp1cQuestionText');
    const vcp1cAnswerInput = document.getElementById('vcp1cAnswerInput');
    const vcp1cValidateBtn = document.getElementById('vcp1cValidateBtn');
    const vcp1cRefuseBtn = document.getElementById('vcp1cRefuseBtn');

    // 1. Initial Load of Sandbox Files
    loadSandboxStatus();

    refreshSandboxBtn.addEventListener('click', loadSandboxStatus);

    // 2. Model Selector Change
    if (modelSelector) {
        modelSelector.addEventListener('change', async () => {
            const selected = modelSelector.value;
            try {
                const resp = await fetch('/api/set_model', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ model: selected })
                });
                const res = await resp.json();
                if (res.statut === 'OK') {
                    appendMessage('SYSTÈME', `🔄 Modèle actif basculé vers : <strong>${selected}</strong>`, 'system-msg');
                }
            } catch (err) {
                console.error('Erreur changement modèle:', err);
            }
        });
    }

    // 3. Quick Action Buttons
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            userInput.value = btn.getAttribute('data-prompt');
            chatForm.dispatchEvent(new Event('submit'));
        });
    });

    // 4. Chat Form Submit
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        // Append User Message
        appendMessage('UTILISATEUR', text, 'user-msg');
        userInput.value = '';
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<span>ÉVALUATION EN COURS...</span>';

        try {
            const resp = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: text })
            });
            const data = await resp.json();

            // Update UI with Agent response
            handleAgentResponse(data);
        } catch (err) {
            appendMessage('ERREUR SYSTÈME', `Échec de communication : ${err.message}`, 'system-msg');
        } finally {
            sendBtn.disabled = false;
            sendBtn.innerHTML = '<span>ÉVALUER & AGIR</span><span class="btn-icon">➔</span>';
            loadSandboxStatus();
        }
    });

    function handleAgentResponse(data) {
        // 1. Update Hardware Performance & Speed
        if (speedVal && data.speed_tok_s !== undefined) {
            speedVal.textContent = Number(data.speed_tok_s).toFixed(1);
        }
        if (tokensVal && data.tokens !== undefined) {
            tokensVal.textContent = `${data.tokens}`;
        }
        if (elapsedVal && data.elapsed_s !== undefined) {
            elapsedVal.textContent = `${data.elapsed_s}s`;
        }

        // 2. Update Telemetry Gauges (sigma, delta, FC)
        if (data.probe) {
            sigmaVal.textContent = Number(data.probe.sigma).toFixed(2);
            deltaVal.textContent = Number(data.probe.delta).toFixed(2);
            fcVal.textContent = Number(data.probe.fc).toFixed(2);

            // Coloration dynamique
            sigmaVal.style.color = data.probe.sigma > 0.3 ? 'var(--accent-red)' : 'var(--accent-cyan)';
        }

        // 3. Update Gatekeeper Badge & Log
        if (data.gatekeeper) {
            const status = data.gatekeeper.status;
            gatekeeperBadge.textContent = status;
            gatekeeperBadge.className = `gate-badge ${status.toLowerCase()}`;
            gatekeeperLog.textContent = data.gatekeeper.log || data.gatekeeper.reason || 'Prêt.';
        }

        // 4. Update STRIC Trace
        if (data.veralume_acte) {
            const acte = data.veralume_acte;
            traceBody.innerHTML = `
                <div><strong>Outil :</strong> ${acte.outil} (Reversibilité: ${acte.reversibilite})</div>
                <div><strong>Décision STRIC_i :</strong> <span style="color:var(--accent-green)">${acte.trace_stric_i.decision}</span></div>
                <div><strong>Résultat N :</strong> ${escapeHtml(acte.resultat) || 'N/A'} (Motif: ${acte.motif})</div>
            `;
        } else if (data.status === 'BLOCKED') {
            traceBody.innerHTML = `<span style="color:var(--accent-red)">⛔ Action bloquée par le Coupe-Circuit. Zéro modification matérielle.</span>`;
        }

        // 5. Append Message to Chat (avec Thinking Process si présent)
        let agentMsgText = '';
        if (data.thinking && data.thinking.trim().length > 0) {
            agentMsgText += `
                <div class="thinking-accordion">
                    <div class="thinking-header" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                        <span>🧠 Processus de Pensée Interne</span>
                        <span>[cliquer pour masquer/afficher]</span>
                    </div>
                    <div class="thinking-content">${escapeHtml(data.thinking)}</div>
                </div>
            `;
        }

        if (data.agent_reply) {
            agentMsgText += `<div class="llm-reply">${formatMarkdown(data.agent_reply)}</div>`;
            if (data.status === 'APPROVED' && data.veralume_acte) {
                agentMsgText += `<div class="action-footer" style="margin-top:8px;font-size:11px;color:var(--accent-green)">✅ Action '${data.veralume_acte.outil}' exécutée (${data.veralume_acte.motif})</div>`;
            } else if (data.status === 'BLOCKED') {
                agentMsgText += `<div class="action-footer" style="margin-top:8px;font-size:11px;color:var(--accent-red)">⛔ Coupe-circuit actif : ${data.gatekeeper?.log || 'Interception.'}</div>`;
            }
        } else if (data.status === 'APPROVED') {
            agentMsgText += `✅ <strong>Ordre validé (Vérité Logique R)</strong> : L'outil <code>${data.planned_tool?.outil}</code> a été exécuté via Double STRIC.`;
        } else if (data.status === 'BLOCKED') {
            agentMsgText += `⛔ <strong>Coupe-Circuit Activé</strong> : ${data.gatekeeper?.log || 'Action interceptée.'}`;
        } else {
            agentMsgText += `⚠️ <strong>Arbitrage Suspendu (État M)</strong> : Escalade vers opérateur humain.`;
        }

        const statsParts = [];
        if (data.speed_tok_s) statsParts.push(`${data.speed_tok_s} tok/s`);
        if (data.tokens) statsParts.push(`${data.tokens} tokens`);
        if (data.elapsed_s) statsParts.push(`${data.elapsed_s}s`);
        const statsStr = statsParts.length > 0 ? ` [${statsParts.join(' • ')}]` : '';

        appendMessage(`AGENT VERALUME${statsStr}`, agentMsgText, 'agent-msg');

        // 6. Handle VCp1c Modal if questions triggered
        if (data.vcp1c_questions && data.vcp1c_questions.length > 0) {
            vcp1cQuestionText.textContent = data.vcp1c_questions[0];
            vcp1cModal.classList.remove('hidden');
        }
    }

    // Modal Handlers
    vcp1cValidateBtn.addEventListener('click', async () => {
        const answer = vcp1cAnswerInput.value.trim();
        vcp1cModal.classList.add('hidden');
        if (answer) {
            appendMessage('RÉPONSE VCp1c (Humain)', answer, 'user-msg');
            chatForm.querySelector('input').value = `[CONFIRMATION VCp1c] ${answer}`;
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    vcp1cRefuseBtn.addEventListener('click', () => {
        vcp1cModal.classList.add('hidden');
        appendMessage('PRISE DE TERRE', '❌ Action manuellement refusée par le nœud humain.', 'system-msg');
    });

    function appendMessage(author, body, className) {
        const msg = document.createElement('div');
        msg.className = `message ${className}`;
        msg.innerHTML = `
            <div class="msg-author">${author}</div>
            <div class="msg-body">${body}</div>
        `;
        chatHistory.appendChild(msg);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function formatMarkdown(text) {
        if (!text) return '';
        // Formatage basique du code et sauts de ligne
        let formatted = escapeHtml(text);
        // Code blocks ```code```
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        // Inline code `code`
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        // Bold **text**
        formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        // Newlines
        formatted = formatted.replace(/\n/g, '<br>');
        return formatted;
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function formatTuple(tupleStr) {
        const facets = tupleStr.split('|');
        return facets.map(f => {
            const trimmed = f.trim();
            if (trimmed.startsWith('episteme:')) {
                return `<span style="color:#f59e0b;font-weight:bold">${trimmed}</span>`;
            } else if (trimmed.startsWith('fix:')) {
                return `<span style="color:#10b981;font-weight:bold">${trimmed}</span>`;
            } else if (trimmed.startsWith('severity:') || trimmed.startsWith('sev:')) {
                return `<span style="color:#ef4444">${trimmed}</span>`;
            } else {
                return `<span style="color:#38bdf8">${trimmed}</span>`;
            }
        }).join(' <span style="color:#475569">|</span> ');
    }

    async function loadSandboxStatus() {
        try {
            const resp = await fetch('/api/sandbox');
            const data = await resp.json();

            // Files
            filesList.innerHTML = '';
            if (data.fichiers && data.fichiers.length > 0) {
                data.fichiers.forEach(f => {
                    const li = document.createElement('li');
                    li.textContent = `📄 ${f.chemin} (${f.taille_octets} octets)`;
                    filesList.appendChild(li);
                });
            } else {
                filesList.innerHTML = '<li><em>Aucun fichier</em></li>';
            }

            // Backups
            backupsList.innerHTML = '';
            if (data.sauvegardes_versionnees && data.sauvegardes_versionnees.length > 0) {
                data.sauvegardes_versionnees.forEach(b => {
                    const li = document.createElement('li');
                    li.textContent = `💾 ${b.nom} (${b.taille} octets)`;
                    backupsList.appendChild(li);
                });
            } else {
                backupsList.innerHTML = '<li><em>Aucune sauvegarde</em></li>';
            }
        } catch (err) {
            console.error('Erreur sandbox load:', err);
        }
    }
});
