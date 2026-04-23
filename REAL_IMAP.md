# Real IMAP Mode Vorbereitung

Dieses Dokument beschreibt, wie der Worker vom Simulationsmodus in den Real-IMAP-Modus umgeschaltet wird.

## Voraussetzungen

1. **Simulationsmodus erfolgreich**: Der Worker wurde lokal gegen den Dovecot-Container getestet.
2. **Zugangsdaten**: Ein gültiges IMAP-Konto (z.B. bei einem Provider) mit Benutzername und Passwort (oder App-Passwort).

## Umschaltung

Die Steuerung erfolgt primär über die `.env`-Datei.

### 1. Umgebungsvariablen anpassen

Erstellen Sie eine `.env`-Datei (basierend auf `.env.example`) und passen Sie folgende Werte an:

```env
# Modus auf 'production' oder 'real' setzen (optional, dient der Log-Klarheit)
WORKER_MODE=real
LOG_LEVEL=INFO

# Echte IMAP-Daten
IMAP_SERVER=imap.ihrprovider.de
IMAP_PORT=993
IMAP_USER=ihr-benutzer@provider.de
IMAP_PASSWORD=ihr-geheimes-passwort
IMAP_MAILBOX=INBOX
IMAP_USE_SSL=True

# Rspamd (falls extern oder in anderem Container)
RSPAMD_URL=http://rspamd:11333/checkv2
RSPAMD_PASSWORD=ihr-rspamd-passwort
```

### 2. Docker Compose Anpassung

Im Realbetrieb kann der `dovecot`-Service aus der `docker-compose.yaml` entfernt oder kommentiert werden, da er nicht mehr benötigt wird.

```yaml
# services:
#   dovecot:
#     ... (auskommentieren)
```

Stellen Sie sicher, dass der `worker` weiterhin Zugriff auf `rspamd` hat.

### 3. Sicherheitshinweise

- Verwenden Sie **immer SSL/TLS** (`IMAP_USE_SSL=True`) für echte Mailkonten.
- Nutzen Sie App-Passwörter, falls Ihr Provider dies unterstützt (z.B. Gmail, iCloud).
- Die `.env`-Datei darf **niemals** in das Git-Repository eingecheckt werden (sie steht bereits in `.gitignore`).

## Testlauf im Realmodus (Dry-Run)

Bevor Sie den Worker dauerhaft laufen lassen, empfiehlt es sich:
1. Den Worker manuell zu starten.
2. Die Logs zu beobachten (`tail -f logs/worker.log`).
3. Zu prüfen, ob die Verbindung erfolgreich hergestellt wird und Mails erkannt werden.
