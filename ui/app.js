/**
 * VERALUME × KAIROS V6 — Frontend Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatHistory = document.getElementById('chatHistory');
    const sendBtn = document.getElementById('sendBtn');
    
    // Telemetry Elements
    const sigmaVal = document.getElementById('sigmaVal');
    const deltaVal = document.getElementById('deltaVal');
    const fcVal = document.getElementById('fcVal');
    const gatekeeperBadge = document.getElementById('gatekeeperBadge');
    const gatekeeperLog = document.getElementById('gatekeeperLog');
    const tupleDisplay = document.getElementById('tupleDisplay');
    
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

    // 2. Chat Form Submit
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        // Append User Message
        appendMessage('UTILISATEUR', text, 'user-msg');
        userInput.value = '';
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<span>SONDAGE EN COURS...</span>';

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
        // 1. Update Telemetry Gauges
        if (data.probe) {
            sigmaVal.textContent = Number(data.probe.sigma).toFixed(2);
            deltaVal.textContent = Number(data.probe.delta).toFixed(2);
            fcVal.textContent = Number(data.probe.fc).toFixed(2);

            // Coloration dynamique
            sigmaVal.style.color = data.probe.sigma > 0.3 ? 'var(--accent-red)' : 'var(--accent-cyan)';
        }

        // 2. Update Gatekeeper Badge & Log
        if (data.gatekeeper) {
            const status = data.gatekeeper.status;
            gatekeeperBadge.textContent = status;
            gatekeeperBadge.className = `gate-badge ${status.toLowerCase()}`;
            gatekeeperLog.textContent = data.gatekeeper.log || data.gatekeeper.reason || 'Aucun log';
        }

        // 3. Highlighted KAIROS V6 Tuple
        if (data.tuple_v6) {
            tupleDisplay.innerHTML = formatTuple(data.tuple_v6);
        }

        // 4. Update STRIC Trace
        if (data.veralume_acte) {
            const acte = data.veralume_acte;
            traceBody.innerHTML = `
                <div><strong>Outil :</strong> ${acte.outil} (Reversibilité: ${acte.reversibilite})</div>
                <div><strong>Décision STRIC_i :</strong> <span style="color:var(--accent-green)">${acte.trace_stric_i.decision}</span></div>
                <div><strong>Résultat N :</strong> ${acte.resultat || 'N/A'} (Motif: ${acte.motif})</div>
            `;
        } else if (data.status === 'BLOCKED') {
            traceBody.innerHTML = `<span style="color:var(--accent-red)">⛔ Action bloquée par le Coupe-Circuit. Zéro modification matérielle.</span>`;
        }

        // 5. Append Message to Chat
        let agentMsgText = '';
        if (data.status === 'APPROVED') {
            agentMsgText = `✅ <strong>Ordre validé (Vérité Logique R)</strong> : L'outil <code>${data.planned_tool.outil}</code> a été exécuté via Double STRIC. (${data.veralume_acte?.motif || ''})`;
        } else if (data.status === 'BLOCKED') {
            agentMsgText = `⛔ <strong>Coupe-Circuit Activé</strong> : ${data.gatekeeper?.log || 'Action interceptée.'}`;
        } else {
            agentMsgText = `⚠️ <strong>Arbitrage Suspendu (État M)</strong> : Escalade vers opérateur humain.`;
        }

        appendMessage('AGENT VERALUME (Qwen 14B)', agentMsgText, 'agent-msg');

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
            // Re-submit with clarified answer
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
