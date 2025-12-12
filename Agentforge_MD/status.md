# AgentForge — Architettura e Stato del Sistema (Handoff Ufficiale)

Aggiornamento: 2025-12-09
Ambiente: nativeserver (Tailscale IP: 100.111.236.92)
Componente GPT: Jarvis Supervisor (nuovo GPT)

---

## 1. Architettura Generale

AgentForge è composto da tre livelli:

### A. Relay HTTP (Server: nativeserver)
Path: /opt/agentforge_relay
Funzione: Gestione inbox/outbox per messaggi tra GPT Supervisor e Server Supervisor.

Componenti:
- app.py (Flask)
- relay_router.py
- audit_logger.py
- mailbox/
  - inbox/supervisor
  - outbox/chatgpt

Endpoint:
- POST /agentforge/inbox/<target>
- GET  /agentforge/outbox/<target>
- GET  /healthz

Stato: FUNZIONANTE.

---

## 2. Supervisor Core (Server: nativeserver)
Path: /opt/agentforge/supervisor_core

Funzioni:
- loop di esecuzione
- parsing messaggi
- stato persistente in runtime/state.json
- azioni: analyze_project, plan_next_steps, execute_agent, run_diagnostics

Componenti:
- supervisor_loop.py
- supervisor.py
- dispatcher.py
- state_manager.py
- message_bus.py
- inbox_handler.py
- outbox_handler.py
- handlers/
- policy_engine.py

Stato: FUNZIONANTE con eccezione dell’outbox.

---

## 3. Runtime interno
Path: /opt/agentforge/runtime

Contiene:
- state.json → stato persistente del supervisore
- (in arrivo) config.yaml → configurazione del GPT Supervisor

---

## 4. Problemi Attivi
- Outbox non scrive nel relay
- PolicyEngine minimo da completare
- Mancanza heartbeat periodico
- Hardening del loop
- Normalizzazione dei messaggi GPT→Relay

---

## 5. Target Finali
1. Supervisore pienamente autonomo
2. GPT Supervisor unico allineato solo con AgentForge
3. Eliminazione di ogni riferimento al vecchio sistema su behemoth
4. Stabilità e prevedibilità tra sessioni tramite config.yaml


