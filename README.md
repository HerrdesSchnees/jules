# jules

# AGENTS.md

## Projektkontext
Dieses Projekt erstellt einen Python-basierten IMAP-Worker als Ersatz für imaprspamd. Ziel ist ein robuster, transparenter und lokal testbarer Worker, der Mails per IMAP liest, an Rspamd über HTTP übergibt, die Antwort auswertet und daraus nachvollziehbare Aktionen ableitet.

## Hauptziele
- Python statt Java
- imaplib statt isbg
- Rspamd per HTTP/REST ansprechen
- lokale Simulation vor echtem Deploy
- Docker-first
- persistente Logs und State-Dateien
- einfache, nachvollziehbare Architektur

## Verbindliche Arbeitsreihenfolge
1. Zuerst immer Simulationsmodus bauen
2. Erst nach erfolgreichem lokalem Test Real-IMAP-Modus vorbereiten
3. Keine produktiven Zugangsdaten in Dateien eintragen
4. Keine echten Mailbewegungen ohne Dry-Run oder klaren Testmodus
5. Vor großen Umbauten zuerst Plan ausgeben

## Architekturregeln
- Worker in Python
- IMAP mit imaplib
- Worker-State bevorzugt in SQLite
- Redis nur verwenden, wenn für Rspamd sinnvoll
- Rspamd-Kommunikation über HTTP mit JSON-Auswertung
- Logging und State persistent auf Host mounten
- Keine unnötige Komplexität in Version 1

## Docker-Regeln
- Immer vollständige docker-compose.yaml liefern
- Alle nötigen Dockerfiles mitliefern
- Hostpfade klar benennen
- Logs in separatem persistentem Pfad
- State-Dateien in separatem persistentem Pfad
- Projekt lokal ohne echtes externes Mailkonto testbar machen

## Sicherheitsregeln
- Nur .env.example bereitstellen
- Keine echten Zugangsdaten hardcoden
- Keine Tokens oder Passwörter in README, Compose oder Python-Code
- Standardmäßig Dry-Run aktivierbar machen

## Test- und Debugging-Regeln
- Immer Debug-Skript bereitstellen
- Testmails für Ham und Spam mitliefern
- Vor Real-IMAP immer lokalen Testlauf dokumentieren
- Rspamd-Erreichbarkeit explizit prüfbar machen
- Logs klar strukturiert mit Zeitstempeln

## Ausgaberegeln für den Agenten
- Zuerst Projektbaum zeigen
- Dann Dateien erzeugen
- Dann Testablauf erklären
- Dann erwartete Ergebnisse nennen
- Bei Architekturentscheidungen kurz begründen, warum diese gewählt wurden
