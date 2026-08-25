#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server.py — Serveur Web & API REST pour l'Agent VERALUME × KAIROS V6
Interface de Mission Control & Console Interactive SRE
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from veralume_agent_core import VeralumeAutonomousAgent

PORT = 7860
UI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")
SANDBOX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace_sandbox")

# Initialisation de l'Agent Veralume
agent = VeralumeAutonomousAgent(SANDBOX_DIR, model_name="qwen2.5:14b")

# Initialisation d'un fichier de test dans le bac à sable
initial_file = os.path.join(SANDBOX_DIR, "cluster_nodes.cfg")
if not os.path.exists(initial_file):
    with open(initial_file, "w", encoding="utf-8") as f:
        f.write("NODE_PRIMARY=worker-01 STATUS=ACTIVE\nNODE_SECONDARY=worker-02 STATUS=STANDBY\n")

class VeralumeHttpHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Silence standard request logging for cleaner console
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ["/", "/index.html"]:
            self.serve_file(os.path.join(UI_DIR, "index.html"), "text/html; charset=utf-8")
        elif path == "/style.css":
            self.serve_file(os.path.join(UI_DIR, "style.css"), "text/css; charset=utf-8")
        elif path == "/app.js":
            self.serve_file(os.path.join(UI_DIR, "app.js"), "application/javascript; charset=utf-8")
        elif path == "/api/sandbox":
            data = agent.list_sandbox_files()
            self.send_json(data)
        else:
            self.send_error(404, "Page non trouvée")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/chat":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len).decode("utf-8")
            try:
                payload = json.loads(body)
                prompt = payload.get("prompt", "").strip()
                if not prompt:
                    self.send_json({"error": "Prompt vide"}, status=400)
                    return
                
                print(f"\n[MISSION CONTROL] 📥 Requête reçue : '{prompt}'")
                result = agent.process_task(prompt)
                print(f"[MISSION CONTROL] 📤 Statut : {result.get('status')} | Elapsed: {result.get('elapsed_s')}s")
                self.send_json(result)
            except Exception as e:
                self.send_json({"error": str(e)}, status=500)
        else:
            self.send_error(404, "Endpoint API inconnu")

    def serve_file(self, filepath: str, content_type: str):
        if not os.path.exists(filepath):
            self.send_error(404, "Fichier non trouvé")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data: dict, status: int = 200):
        content = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main():
    server = HTTPServer(("127.0.0.1", PORT), VeralumeHttpHandler)
    print("="*80)
    print(f"🚀 VERALUME × KAIROS V6 — MISSION CONTROL INTERFACE")
    print(f"📍 Serveur local actif sur : http://localhost:{PORT}")
    print(f"🧠 Modèle connecté         : {agent.model_name} (Ollama)")
    print(f"🛡️  Bac à Sable Matériel    : {SANDBOX_DIR}")
    print("="*80)
    print("Ouvrez votre navigateur sur http://localhost:7860 pour communiquer avec l'agent.")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
        server.server_close()

if __name__ == "__main__":
    main()
