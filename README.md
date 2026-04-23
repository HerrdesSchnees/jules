# jules

Erstelle mir ein vollständiges, lokal testbares Docker-Projekt für einen IMAP-basierten Spamfilter-Worker als Ersatz für imaprspamd. Ziel ist ein Python-Wrapper auf Basis von imaplib, der Mails per IMAP holt, an Rspamd zur Bewertung übergibt, die JSON-/HTTP-Antwort auswertet und daraus Aktionen ableitet. Bitte keine Java-Lösung und kein isbg. Ich will einen sauberen, transparenten, gut debuggbaren Aufbau.

Rahmenbedingungen:
- Sprache: Python
- IMAP-Zugriff: imaplib
- Rspamd als eigener Container
- Redis optional, aber bitte Architekturentscheidung begründen:
  - wenn Redis sinnvoll ist: für welche Teile?
  - wenn SQLite für den Worker-State besser ist: bitte SQLite verwenden
- Ich möchte eine lauffähige Simulation, ohne echtes externes Mailkonto
- Der Worker soll lokal testbar sein und ein IMAP-Konto simulieren
- Der Fokus liegt auf robuster Worker-Logik, nicht nur auf Bayes-Lernen

Bitte liefere ein vollständiges Paket mit:
1. docker-compose.yaml
2. Dockerfile(s)
3. Python-Worker-Skript
4. Beispiel-Konfigurationsdateien
5. .env.example
6. Rspamd-Konfig-Dateien, soweit nötig
7. Debugging-/Test-Skript
8. persistente Log-Ausgabe in einem separaten Host-Pfad
9. README mit Startreihenfolge, Testablauf und Troubleshooting

Zielarchitektur:
- Ein Python-Worker-Container
- Ein rspamd-Container
- Optional ein redis-Container, wenn fachlich sinnvoll
- Ein lokaler Test-/Mock-IMAP-Ansatz, damit der Worker Mails “wie echt” verarbeiten kann
- Keine Abhängigkeit von einem realen Gmail-/A1-Konto im ersten Schritt

Der Python-Worker soll mindestens können:
- Verbindung zu einem IMAP-Server herstellen
- einen konfigurierbaren Ordner überwachen oder pollen
- neue Mails per UID erkennen
- verarbeitete Mails persistent merken
- rohe RFC822-Mail holen
- Mail an Rspamd über HTTP schicken, möglichst über /checkv2 oder eine geeignete aktuelle Schnittstelle
- Antwort von Rspamd auswerten:
  - score
  - action
  - symbols
  - required_score
- je nach Ergebnis Aktionen simulieren oder ausführen:
  - Inbox belassen
  - in Spam verschieben
  - in Quarantäne verschieben
  - markieren/loggen
- Dry-Run-Modus unterstützen
- sauberes Logging mit Zeitstempel
- Fehler robust behandeln
- idempotent arbeiten, also keine doppelte Verarbeitung
- einen Debug-Modus haben

Bitte simuliere den IMAP-Teil so, dass ich lokal testen kann. Bevorzugt:
- ein kleiner Mock-IMAP-Ansatz oder
- eine lokal gemountete Test-Mailbox mit Beispielmails
Wenn ein echter Mock-IMAP-Server im Container praktikabler ist, dann baue ihn mit ein. Wenn das unnötig komplex ist, dann abstrahiere die IMAP-Schicht sauber, aber so, dass ein echter IMAP-Server später leicht eingesteckt werden kann.

Bitte lege Beispielmails bei:
- mindestens 2-3 Ham-Mails
- mindestens 2-3 Spam-/Phishing-artige Mails
- optional eine grenzwertige Mail
Die Mails sollen in einem Testpfad liegen und vom Worker verarbeitet werden können.

State-Management:
- Bitte begründe, ob für den Worker SQLite oder Redis besser ist
- Wenn Redis nur für Rspamd gebraucht wird, aber nicht für den Worker-State, dann verwende für den Worker lieber SQLite
- Der Worker soll eindeutig speichern:
  - UID
  - Message-ID
  - Verarbeitungsstatus
  - letzter Score
  - letzte Action
  - Zeitstempel

Logging:
- Persistente Logs in einem separaten Host-Pfad
- Zusätzlich ein eigenes Debugging-Skript, z. B.:
  - Test der Rspamd-Erreichbarkeit
  - Test der Worker-Konfiguration
  - Testlauf gegen Beispielmails
  - Ausgabe der Rspamd-Antworten
- Bitte sorge dafür, dass Logs und State-Dateien nach Container-Neustarts erhalten bleiben

Rspamd:
- Verwende eine möglichst einfache, stabile Konfiguration
- Keine unnötig exotische Bayes-/learn_condition-Komplexität im ersten Wurf
- Ziel ist zuerst: funktionierende Erkennung/Scoring im Worker-Flow
- Optional kannst du Bayes und Redis minimal mit vorbereiten, aber die Hauptsache ist der saubere Scan- und Entscheidungsweg

Wichtig:
- Bitte das Projekt so bauen, dass ich es direkt lokal starten kann
- Alle Pfade klar und nachvollziehbar
- Kein Pseudocode, sondern echte Dateien
- Bitte am Ende den kompletten Projektbaum ausgeben
- Danach jede erzeugte Datei mit Inhalt ausgeben
- Dann einen Testablauf beschreiben:
  1. Build
  2. Start
  3. Debug-Test
  4. Beispiel-Scan
  5. Sichtprüfung der Logs
  6. erwartete Ergebnisse

Zusatz:
- Bitte erkläre kurz, warum diese Architektur robuster ist als imaprspamd
- Bitte trenne klar zwischen:
  - produktivem IMAP-Modus
  - lokalem Simulations-/Testmodus

Wenn du Annahmen treffen musst, dann bevorzuge maximale Transparenz, Debugbarkeit und einfache Erweiterbarkeit.
