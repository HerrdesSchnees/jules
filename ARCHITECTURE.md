# Architektur-Dokumentation

Dieses Dokument beschreibt die Architekturentscheidungen für den Python-basierten IMAP-Worker.

## Technologie-Entscheidungen

### 1. Python & `imaplib`
Python wurde gewählt, da es eine hervorragende Balance zwischen Lesbarkeit und Mächtigkeit bietet. Die integrierte `imaplib` ermöglicht den direkten Zugriff auf IMAP-Server ohne unnötige Abstraktionsschichten, was die Fehlersuche vereinfacht.

### 2. SQLite für State-Management
Für die Nachverfolgung bereits verarbeiteter Mails wird SQLite verwendet. Da der Worker als Einzelprozess konzipiert ist, bietet SQLite eine performante, dateibasierte Persistenz ohne die Komplexität eines separaten Datenbankservers (wie Redis oder PostgreSQL).

### 3. Rspamd via HTTP
Rspamd bietet eine leistungsfähige REST-API. Durch die direkte Kommunikation über HTTP (mit der `requests`-Bibliothek) entfällt die Notwendigkeit für komplexe Mail-Routing-Setups während der Analysephase.

### 4. Docker-First-Ansatz
Die gesamte Umgebung ist für Docker Compose optimiert, um eine konsistente Entwicklung, Simulation und Produktion zu gewährleisten.

## Geplanter Projektbaum

```text
.
├── docker-compose.yaml      # Orchestrierung von Worker, Rspamd, Redis und Dovecot
├── .env.example             # Vorlage für Umgebungsvariablen
├── ARCHITECTURE.md          # Diese Datei
├── AGENTS.md                # Anweisungen für KI-Agenten
├── README.md                # Allgemeine Projektinfos
├── TASKS.md                 # Aufgabenliste
├── data/                    # Persistente Daten
│   ├── testmails/           # Beispiel-Mails für die Simulation
│   └── state/               # SQLite-Datenbank des Workers
├── logs/                    # Log-Dateien
├── rspamd/                  # Rspamd-Konfiguration
│   └── local.d/             # Lokale Overrides für Rspamd
├── dovecot/                 # Konfiguration für den Simulations-IMAP-Server
├── worker/                  # Quellcode des Workers
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py              # Einstiegspunkt
│   ├── imap_client.py       # IMAP-Interaktion
│   ├── rspamd_client.py     # Rspamd-API-Interaktion
│   └── state_manager.py     # SQLite-Abstraktion
└── scripts/                 # Hilfs- und Debug-Skripte
    └── debug_worker.py      # Connectivity-Test
```

## Simulations-Konzept
Für die Simulation wird ein lokaler **Dovecot** Container verwendet. Dies ermöglicht es, echte IMAP-Befehle gegen einen lokalen Server zu testen, ohne externe Konten zu gefährden. Testmails werden beim Start der Simulation in das Dovecot-Postfach geladen.
