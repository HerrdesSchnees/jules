# IMAP Worker for Rspamd

## Überblick
Dieses Projekt stellt einen Python-basierten IMAP-Worker als Ersatz für `imaprspamd` bereit. Ziel ist ein robuster, transparenter und lokal testbarer Worker, der Mails per IMAP liest, an Rspamd über HTTP übergibt, die JSON-Antwort auswertet und daraus nachvollziehbare Aktionen ableitet.

Der Schwerpunkt liegt auf:
- klarer Architektur
- guter Debugbarkeit
- Docker-basierter Reproduzierbarkeit
- persistenter Zustands- und Log-Verwaltung
- direktem Dry-Run gegen ein echtes IMAP-Konto ohne produktive Mailbewegungen

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

### 1. Real IMAP Dry-Run
Der Standardpfad ist jetzt der direkte Dry-Run gegen ein echtes IMAP-Konto.
Dabei verbindet sich der Worker direkt zum Mailprovider, liest Mails, bewertet sie mit Rspamd und protokolliert nur die Entscheidungen.
Solange `DRY_RUN=true` gesetzt ist, werden keine Mails verschoben oder gelöscht.

### 2. Späterer Echtbetrieb
Der spätere Echtbetrieb ist möglich, sobald der Dry-Run stabil läuft.
Dann kann `DRY_RUN=false` gesetzt werden. Die Zugangsdaten bleiben weiterhin lokal in `.env` und werden niemals committed.

## Architektur
Die Zielarchitektur besteht aus folgenden Komponenten:

- Python Worker
- Rspamd
- optional Redis, falls für Rspamd sinnvoll
- persistente Logs
- persistenter Worker-State

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
- Keine echten Zugangsdaten in `compose.yaml`
- Keine echten Zugangsdaten in `README.md`
- Keine produktiven Mailaktionen ohne klaren Betriebsmodus
- Dry-Run muss möglich sein
- `.env.example` statt echter `.env`

## Lokale Konfiguration
Im Repository liegt nur eine `.env.example`.
Für den echten Betrieb legst du lokal eine `.env` an. Diese Datei wird nicht committed.

Empfohlener Ablauf:
1. `.env.example` nach `.env` kopieren
2. echte A1-IMAP-Werte lokal eintragen
3. `DRY_RUN=true` beibehalten
4. lokale Tests durchführen
5. erst danach über produktive Mailbewegungen nachdenken

Beispiel:
```bash
cp .env.example .env
```

## Entwicklungsprinzipien
- Einfachheit vor Overengineering
- Transparenz vor Magie
- Testbarkeit vor Produktivschaltung
- zuerst Dry-Run, dann Realbetrieb
- lokale Reproduzierbarkeit
- nachvollziehbare Docker-Struktur

## Erwartete Projektbestandteile
Das Projekt soll mindestens enthalten:

- `compose.yaml`
- `Dockerfile.worker`
- Python-Worker-Code
- Konfigurationsdateien
- `.env.example`
- Rspamd-Konfigurationsdateien
- Debugging-Skript
- persistente Log- und State-Pfade
- diese `README.md`
- eine `TASKS.md`
- optional `AGENTS.md`

## Erwarteter Entwicklungsablauf
1. Architekturentscheidung dokumentieren
2. direkten Dry-Run gegen IMAP aufbauen
3. Rspamd-Anbindung testen
4. Worker-State testen
5. Logging testen
6. stabilen Dry-Run durchführen
7. erst danach produktive Aktionen vorbereiten

## Schnellstart
### A1 Dry-Run
```bash
cp .env.example .env
# .env lokal mit echten A1-Zugangsdaten befüllen
docker compose up --build
```

### Debug-Check
```bash
python3 debug.py
```

### Wechsel auf echten Eingriff
- `.env` lokal anpassen
- `DRY_RUN=false` nur bewusst und erst nach erfolgreichem Dry-Run setzen
- zuerst weiter gegen INBOX lesen und Ergebnisse kontrollieren

## Debugging
Das Projekt stellt ein Debugging-Skript bereit, das folgende Punkte testet:

- Konfiguration vorhanden und lesbar
- Rspamd erreichbar
- Worker-Dateien vorhanden
- `.env.example` enthält die erwarteten Dry-Run-Vorgaben
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
