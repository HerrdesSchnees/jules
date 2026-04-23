# AGENTS.md für jules

# IMAP Worker for Rspamd

## Überblick
Dieses Projekt stellt einen Python-basierten IMAP-Worker als Ersatz für `imaprspamd` bereit. Ziel ist ein robuster, transparenter und lokal testbarer Worker, der Mails per IMAP liest, an Rspamd über HTTP übergibt, die JSON-Antwort auswertet und daraus nachvollziehbare Aktionen ableitet.

Der Schwerpunkt liegt auf:
- klarer Architektur
- guter Debugbarkeit
- Docker-basierter Reproduzierbarkeit
- persistenter Zustands- und Log-Verwaltung
- lokaler Simulation vor produktivem IMAP-Deploy

## Projektziel
Der Worker soll:
- neue Mails aus einer IMAP-Quelle erkennen
- rohe RFC822-Mails abrufen
- an Rspamd zur Bewertung senden
- `score`, `required_score`, `action` und `symbols` auswerten
- darauf basierend Mailaktionen ausführen oder simulieren
- verarbeitete Mails persistent merken
- idempotent und nachvollziehbar arbeiten

## Betriebsmodi
Dieses Projekt unterscheidet zwei klar getrennte Modi.

### 1. Simulation Mode
Der Simulation Mode ist die Standard- und Erstbetriebsart.
Er dient dazu, den kompletten Workflow lokal und ohne echtes externes Mailkonto zu testen.

Im Simulationsmodus soll überprüfbar sein:
- Mail-Erkennung
- Übergabe an Rspamd
- Parsing der Rspamd-Antwort
- Zustandsverwaltung
- Logging
- Entscheidungslogik

### 2. Real IMAP Mode
Der Real IMAP Mode ist für den späteren produktiven oder semi-produktiven Betrieb gedacht.
Er wird erst vorbereitet, nachdem die lokale Simulation stabil funktioniert.

Im Real IMAP Mode werden echte IMAP-Zugangsdaten verwendet, die niemals hart codiert, sondern nur über Umgebungsvariablen oder externe Konfigurationsdateien eingebunden werden.

## Architektur
Die Zielarchitektur besteht aus folgenden Komponenten:

- Python Worker
- Rspamd
- optional Redis, falls für Rspamd sinnvoll
- persistente Logs
- persistenter Worker-State
- lokale Testmails / Simulationsquelle

### Python Worker
Der Worker ist die zentrale Logik dieses Projekts.
Er übernimmt:
- IMAP-Zugriff über `imaplib`
- Deduplizierung
- State-Management
- Kommunikation mit Rspamd
- Auswertung von Aktionen
- Logging
- Debugging

### Rspamd
Rspamd übernimmt:
- Mail-Analyse
- Score-Berechnung
- Symbolbewertung
- Action-Empfehlung

### SQLite oder Redis
Für den Worker-State wird bevorzugt SQLite verwendet, sofern kein zwingender Grund für Redis besteht.
Redis kann weiterhin für Rspamd selbst genutzt werden, insbesondere für Bayes oder History, ist aber nicht automatisch die beste Wahl für den Worker-State.

## Persistenz
Das Projekt muss so aufgebaut sein, dass die folgenden Daten persistent auf Host-Seite gespeichert werden:

- Logs
- Worker-State
- optionale Datenbanken
- optionale Testartefakte

Diese Daten dürfen bei Container-Neustarts nicht verloren gehen.

## Logging
Logging ist ein Kernbestandteil des Projekts.
Erwartet werden:
- persistente Logdateien
- Zeitstempel
- klare Trennung von Info-, Warn- und Fehlerzuständen
- nachvollziehbare Protokollierung der Entscheidungen
- Debug-Modus

## Sicherheitsprinzipien
- Keine echten Zugangsdaten in den Quellcode
- Keine echten Zugangsdaten in `docker-compose.yml`
- Keine echten Zugangsdaten in `README.md`
- Keine produktiven Mailaktionen ohne klaren Betriebsmodus
- Dry-Run muss möglich sein
- `.env.example` statt echter `.env`

## Entwicklungsprinzipien
- Einfachheit vor Overengineering
- Transparenz vor Magie
- Testbarkeit vor Produktivschaltung
- zuerst Simulation, dann Realbetrieb
- lokale Reproduzierbarkeit
- nachvollziehbare Docker-Struktur

## Erwartete Projektbestandteile
Das Projekt soll mindestens enthalten:

- `docker-compose.yaml`
- `Dockerfile` oder mehrere Dockerfiles
- Python-Worker-Code
- Konfigurationsdateien
- `.env.example`
- Rspamd-Konfigurationsdateien
- Testmails
- Debugging-Skript
- persistente Log- und State-Pfade
- diese `README.md`
- eine `TASKS.md`
- optional `AGENTS.md`

## Erwarteter Entwicklungsablauf
1. Architekturentscheidung dokumentieren
2. Simulationsmodus aufbauen
3. lokale Testmails einbinden
4. Rspamd-Anbindung testen
5. Worker-State testen
6. Logging testen
7. End-to-End-Simulation erfolgreich durchführen
8. erst danach Real-IMAP-Modus vorbereiten

## Debugging
Das Projekt soll mindestens ein Debugging-Skript bereitstellen, das folgende Punkte testet:

- Konfiguration vorhanden und lesbar
- Rspamd erreichbar
- Worker startet
- Beispielmail kann verarbeitet werden
- Rspamd-Antwort wird sichtbar ausgegeben
- Logs werden geschrieben
- State wird persistiert

## Abgrenzung
Dieses Projekt ist kein vollständiger Mailserver.
Es ersetzt keinen SMTP-/IMAP-Server-Stack wie Postfix + Dovecot.
Es ist ein Worker-Projekt für kontrollierte Analyse und Weiterverarbeitung von Mails.

## Warum dieses Projekt?
Das Projekt existiert, weil bestehende IMAP-Worker-Lösungen wie `imaprspamd` in bestimmten Setups zu unflexibel, intransparent oder schwer debugbar sein können.
Ein Python-Worker mit `imaplib` und HTTP-Kommunikation zu Rspamd soll:
- besser kontrollierbar
- besser testbar
- leichter anpassbar
- leichter debugbar
sein.

## Nächste Datei
Die konkreten Umsetzungsanforderungen stehen in `TASKS.md`.
