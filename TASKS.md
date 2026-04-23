# TASKS.md

## Zweck
Diese Datei definiert die konkreten Aufgaben, Deliverables und Abnahmekriterien für den Agenten. Sie ist verbindlich für die Umsetzung des Projekts.

## Hauptauftrag
Erstelle ein vollständiges, lokal testbares Docker-Projekt für einen Python-basierten IMAP-Worker als Ersatz für `imaprspamd`.

Der Worker soll:
- `imaplib` verwenden
- Rspamd per HTTP ansprechen
- JSON-Antworten auswerten
- daraus robuste und nachvollziehbare Entscheidungen ableiten
- lokal im Simulationsmodus testbar sein
- erst danach für echten IMAP-Betrieb vorbereitet werden

## Verbindliche Arbeitsreihenfolge
1. Zuerst Architekturentscheidung treffen und kurz begründen
2. Danach Projektbaum festlegen
3. Danach alle Dateien für den Simulationsmodus erzeugen
4. Danach Testlauf im Simulationsmodus vorbereiten
5. Danach erwartete Ergebnisse dokumentieren
6. Erst ganz am Ende Dateien und Struktur für Real-IMAP-Modus ergänzen
7. Kein direkter produktiver Deploy ohne funktionierende Simulation

## Phase 1: Simulation Mode
### Ziel
Eine vollständige lokale Testumgebung bauen, in der der Worker ohne echtes externes Mailkonto funktional geprüft werden kann.

### Muss-Anforderungen
- Docker-basiertes Setup
- Python-Worker
- Rspamd-Container
- optional Redis, wenn sinnvoll begründet
- persistente Logs
- persistenter Worker-State
- Testmails für Ham und Spam
- Debugging-Skript
- End-to-End-Testpfad

### Der Worker muss in Phase 1 mindestens können
- Mails aus einer simulierten Quelle erkennen
- eindeutige IDs verarbeiten
- Rohmail lesen
- Mail an Rspamd senden
- Rspamd-Antwort parsen
- `score`, `required_score`, `action`, `symbols` auswerten
- Ergebnis loggen
- Status persistent speichern
- Dry-Run unterstützen
- Debug-Modus unterstützen

### Phase 1 Ergebnis
Am Ende von Phase 1 muss ein lokaler Testlauf möglich sein, der den kompletten Workflow sichtbar demonstriert.

## Phase 2: Real IMAP Mode
### Ziel
Vorbereitung der Projektstruktur für den späteren echten IMAP-Betrieb.

### Muss-Anforderungen
- klare Trennung zum Simulationsmodus
- Beispielkonfigurationsdateien für echtes IMAP
- keine echten Zugangsdaten
- `.env.example`
- klare Dokumentation der Umschaltung
- Realmodus darf vorbereitet, aber nicht blind aktiviert werden

## Technische Vorgaben
### Sprache
- Python

### IMAP
- `imaplib`

### HTTP-Client zu Rspamd
- `requests` oder `httpx`

### State-Management
- standardmäßig SQLite bevorzugen
- Redis nur für Worker-State verwenden, wenn es klar fachlich begründet ist
- Redis darf für Rspamd separat genutzt werden

### Logging
- persistente Logdateien
- eigene Hostpfade
- klare Zeitstempel
- Debug-Ausgabe aktivierbar

### Docker
- vollständige `docker-compose.yaml`
- alle nötigen Dockerfiles
- keine unnötige Komplexität
- lokal reproduzierbar

## Zu erzeugende Dateien
Mindestens diese Dateien oder funktional gleichwertige Strukturen müssen erstellt werden:

- `docker-compose.yaml`
- `Dockerfile` für den Worker
- Python-Worker-Dateien
- Konfigurationsdateien
- `.env.example`
- Rspamd-Konfigurationsdateien
- Beispiel-Testmails
- Debugging-Skript
- README
- persistente Verzeichnisstruktur für:
  - logs
  - state
  - testdata
  - optional output

## Erforderliche Hostpfade
Das Projekt muss Hostpfade oder klar definierte Volumes für folgende Bereiche haben:
- Worker-Logs
- Worker-State
- Testmails
- optionale Debug-/Output-Dateien

Diese Pfade müssen über Neustarts erhalten bleiben.

## Debugging-Anforderungen
Ein separates Debugging-Skript muss mindestens Folgendes prüfen:
- Konfigurationsdateien vorhanden
- Rspamd erreichbar
- Worker-Konfiguration lesbar
- Testmail verarbeitbar
- Rspamd-Antwort sichtbar
- Logausgabe vorhanden
- State-Datei vorhanden oder erzeugbar

## Testmails
Das Projekt muss Testmails bereitstellen:
- mindestens 2 Ham-Mails
- mindestens 2 Spam-/Phishing-artige Mails
- optional 1 grenzwertige Mail

Die Testmails sollen so eingebunden sein, dass sie im Simulationsmodus verarbeitet werden können.

## Abnahmekriterien
Die Aufgabe gilt erst dann als erfüllt, wenn:

1. der Projektbaum vollständig dargestellt wurde
2. alle notwendigen Dateien erzeugt wurden
3. die Dateien vollständigen Inhalt haben
4. der Simulationsmodus lokal startbar ist
5. ein nachvollziehbarer Testablauf beschrieben ist
6. Logs persistent geschrieben werden
7. State persistent gespeichert wird
8. eine Beispielverarbeitung mit Rspamd dokumentiert ist
9. die Umschaltung auf echten IMAP-Betrieb vorbereitet ist

## Ausgabereihenfolge für den Agenten
Die Ausgabe soll in dieser Reihenfolge erfolgen:

1. Architekturentscheidung
2. Projektbaum
3. Datei für Datei mit vollständigem Inhalt
4. Simulations-Testablauf
5. erwartete Ergebnisse
6. Vorbereitung für Real-IMAP-Modus
7. kurze Begründung, warum die Architektur robuster ist als `imaprspamd`

## Verbotene Abkürzungen
- kein isbg
- keine Java-Lösung
- keine echten Zugangsdaten
- kein produktiver Mailzugriff als erster Schritt
- keine unnötig komplizierte Bayes-/Autolearn-Konfiguration in Version 1
- kein Overengineering

## Bevorzugte Eigenschaften
- Klarheit
- Nachvollziehbarkeit
- Debugbarkeit
- robuste Minimalarchitektur
- saubere Trennung von Simulation und Realbetrieb
- Docker-first
