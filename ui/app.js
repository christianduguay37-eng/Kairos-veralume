/**
 * VERALUME × KAIROS V6 — Frontend Controller
 * Recherche Web, Mot-Clé de Réveil "Alix" (Wake-Word), Voice STT & TTS
 */

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatHistory = document.getElementById('chatHistory');
    const sendBtn = document.getElementById('sendBtn');
    const modelSelector = document.getElementById('modelSelector');
    
    // Voice Elements
    const micBtn = document.getElementById('micBtn');
    const toggleTtsBtn = document.getElementById('toggleTtsBtn');
    const ttsIcon = document.getElementById('ttsIcon');
    const ttsStatusText = document.getElementById('ttsStatusText');
    const toggleWakeWordBtn = document.getElementById('toggleWakeWordBtn');
    const wakeWordIcon = document.getElementById('wakeWordIcon');
    const wakeWordStatusText = document.getElementById('wakeWordStatusText');

    let ttsEnabled = true;
    let wakeWordEnabled = true;
    const WAKE_WORDS = ["alix", "alex", "alice", "veralume", "alyx", "élix", "felix"];

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

    // Audio Feedback Beep
    function playWakeBeep() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(587.33, ctx.currentTime); // Ré5
            osc.frequency.setValueAtTime(880, ctx.currentTime + 0.08); // La5
            gain.gain.setValueAtTime(0.2, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.25);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.25);
        } catch (e) {}
    }

    // 2. Voice Recognition & Wake-Word Engine
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isExplicitRecording = false;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = 'fr-FR';
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onstart = () => {
            if (isExplicitRecording) {
                micBtn.classList.add('listening');
                userInput.placeholder = '🎙️ Écoute en cours... Parlez maintenant !';
            }
        };

        recognition.onresult = (event) => {
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                const transcript = event.results[i][0].transcript.trim().toLowerCase();
                const isFinal = event.results[i].isFinal;

                // Cas 1 : Enregistrement manuel via clic sur le micro
                if (isExplicitRecording && isFinal) {
                    userInput.value = transcript;
                    micBtn.classList.remove('listening');
                    isExplicitRecording = false;
                    userInput.placeholder = 'Écrivez ou dites "Alix..." pour parler...';
                    chatForm.dispatchEvent(new Event('submit'));
                    return;
                }

                // Cas 2 : Détection du mot-clé Wake-Word "Alix"
                if (wakeWordEnabled && isFinal) {
                    for (const ww of WAKE_WORDS) {
                        const index = transcript.indexOf(ww);
                        if (index !== -1) {
                            // Mot de réveil trouvé ! Extraire la commande qui suit
                            const command = transcript.substring(index + ww.length).replace(/^[,:.\s]+/, '').trim();
                            if (command.length >= 2) {
                                playWakeBeep();
                                userInput.value = command;
                                appendMessage('VOIX (Mot-Clé Alix)', `🗣️ <em>"${transcript}"</em>`, 'user-msg');
                                chatForm.querySelector('input').value = command;
                                chatForm.dispatchEvent(new Event('submit'));
                                return;
                            }
                        }
                    }
                }
            }
        };

        recognition.onerror = (event) => {
            if (event.error !== 'no-speech') {
                console.warn('SpeechRecognition error:', event.error);
            }
        };

        recognition.onend = () => {
            // Redémarrage automatique si le mot-clé de réveil est actif
            if (wakeWordEnabled) {
                try {
                    recognition.start();
                } catch (e) {}
            } else if (isExplicitRecording) {
                micBtn.classList.remove('listening');
                isExplicitRecording = false;
                userInput.placeholder = 'Écrivez ou dites "Alix..." pour parler...';
            }
        };

        // Démarrage initial de l'écoute passive du mot de réveil
        try {
            recognition.start();
        } catch (e) {}

        if (micBtn) {
            micBtn.addEventListener('click', () => {
                window.speechSynthesis.cancel();
                isExplicitRecording = true;
                micBtn.classList.add('listening');
                userInput.placeholder = '🎙️ Parlez maintenant...';
                try {
                    recognition.start();
                } catch (e) {}
            });
        }
    } else if (micBtn) {
        micBtn.style.display = 'none';
    }

    // 3. Wake-Word Toggle Button
    if (toggleWakeWordBtn) {
        toggleWakeWordBtn.addEventListener('click', () => {
            wakeWordEnabled = !wakeWordEnabled;
            if (wakeWordEnabled) {
                toggleWakeWordBtn.classList.add('active');
                wakeWordIcon.textContent = '👂';
                wakeWordStatusText.textContent = 'Mot-clé "Alix" : ON';
                try { recognition.start(); } catch (e) {}
            } else {
                toggleWakeWordBtn.classList.remove('active');
                wakeWordIcon.textContent = '💤';
                wakeWordStatusText.textContent = 'Mot-clé "Alix" : OFF';
                try { recognition.stop(); } catch (e) {}
            }
        });
    }

    // 4. Voice Synthesis Toggle (Text-to-Speech)
    if (toggleTtsBtn) {
        toggleTtsBtn.addEventListener('click', () => {
            ttsEnabled = !ttsEnabled;
            if (ttsEnabled) {
                toggleTtsBtn.classList.add('active');
                ttsIcon.textContent = '🔊';
                ttsStatusText.textContent = 'Voix : ON';
            } else {
                toggleTtsBtn.classList.remove('active');
                ttsIcon.textContent = '🔇';
                ttsStatusText.textContent = 'Voix : OFF';
                window.speechSynthesis.cancel();
            }
        });
    }

    function speakText(text) {
        if (!ttsEnabled || !('speechSynthesis' in window)) return;

        window.speechSynthesis.cancel();
        
        let cleanText = text.replace(/```[\s\S]*?```/g, "Voir le code affiché à l'écran.");
        cleanText = cleanText.replace(/`([^`]+)`/g, '$1');
        cleanText = cleanText.replace(/https?:\/\/[^\s]+/g, 'lien web');
        cleanText = cleanText.replace(/[*_#|]/g, ' ');

        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'fr-FR';
        utterance.rate = 1.05;
        utterance.pitch = 1.0;

        const voices = window.speechSynthesis.getVoices();
        const frenchVoice = voices.find(v => v.lang.startsWith('fr') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Denise') || v.name.includes('Paul') || v.name.includes('Julie')));
        if (frenchVoice) {
            utterance.voice = frenchVoice;
        }

        window.speechSynthesis.speak(utterance);
    }

    // 5. Model Selector Change
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

    // 6. Quick Action Buttons
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            userInput.value = btn.getAttribute('data-prompt');
            chatForm.dispatchEvent(new Event('submit'));
        });
    });

    // 7. Chat Form Submit
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

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

        // 2. Update Telemetry Gauges
        if (data.probe) {
            sigmaVal.textContent = Number(data.probe.sigma).toFixed(2);
            deltaVal.textContent = Number(data.probe.delta).toFixed(2);
            fcVal.textContent = Number(data.probe.fc).toFixed(2);
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
            speakText(data.agent_reply);
        } else if (data.status === 'APPROVED') {
            agentMsgText += `✅ <strong>Ordre validé (Vérité Logique R)</strong> : L'outil <code>${data.planned_tool?.outil}</code> a été exécuté via Double STRIC.`;
        } else if (data.status === 'BLOCKED') {
            agentMsgText += `⛔ <strong>Coupe-Circuit Activé</strong> : ${data.gatekeeper?.log || 'Action interceptée.'}`;
            speakText("Coupe-circuit activé. Action bloquée.");
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
            speakText(data.vcp1c_questions[0]);
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
        speakText("Action refusée par le nœud humain.");
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
        let formatted = escapeHtml(text);
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
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
