# AgentForge — TODO (Handoff Ufficiale)

Aggiornamento: 2025-12-09

---

## PRIORITÀ 1 — Riparare Outbox
- Correggere outbox_handler.py
- Verificare path:
  /opt/agentforge_relay/mailbox/outbox/chatgpt
- Aggiungere logging che confermi la scrittura
- Verificare serializzazione JSON

---

## PRIORITÀ 2 — Policy Engine
Implementare policy minima in policy_engine.py:

validate(action, data) → True
validate_agent(agent) → True
validate_project(project) → True

---

## PRIORITÀ 3 — Heartbeat
Aggiungere heartbeat automatici:

if cycle % 20 == 0:
    bus.push("chatgpt", {"event": "heartbeat", "cycle": cycle})

---

## PRIORITÀ 4 — Hardening Supervisor Loop
Aggiungere:
try:
    self.step()
except Exception as e:
    print("[SupervisorLoop] Error:", e)

---

## PRIORITÀ 5 — Pulizia Mailbox
Svuotare periodicamente:
- inbox/supervisor
- outbox/chatgpt

---

## PRIORITÀ 6 — Normalizzazione Messaggi GPT
Creare wrapper unico che:
- chunkizza payload
- applica Base64 se richiesto
- produce formato compatibile con relay

---

## PRIORITÀ 7 — Documentazione
- Finalizzare state.md
- Finalizzare config.yaml come unica fonte di verità GPT


