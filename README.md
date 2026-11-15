# Geld für eAuto – Home Assistant Integration

Inoffizielle HACS-Integration für https://geld-fuer-eauto.de/.

## Funktionsumfang – experimentelle Version 0.2.0

Die Integration kann auf zwei Arten eingerichtet werden:

- **Ohne Zugangsdaten:** Öffentliche Standardprämien für die Fahrzeugklassen M1, N1, N2, N3, M3 je Quotenjahr. Aktualisierung alle 24 Stunden.
- **Mit E-Mail und Passwort:** Experimenteller read-only Kundenkontoabruf. Erstellt Sensoren für Anzahl registrierter Fahrzeuge, bezahlte und ausstehende THG-Prämien sowie Prämien, Zahlungsstatus und Auszahlungskennzeichen pro Fahrzeug und Quotenjahr. Aktualisierung alle sechs Stunden.

**Authentifizierung ist noch nicht live bestätigt.** Die HAR-Datei zeigt den Login per `POST /api/login`, aber keine Cookies bzw. Sitzungsheader. Der persönliche Abruf verifiziert daher nach dem Login die Accountdaten; wenn das nicht gelingt, wird eine Aktualisierungsfehlermeldung ausgegeben. Keine Gewähr, dass der Login in der aktuellen Version funktioniert.

## HACS-Installation

1. In HACS **Benutzerdefinierte Repositories** öffnen.
2. `https://github.com/DrLippe/homeassistant-geldfuereauto` hinzufügen, Typ **Integration**.
3. **Geld für eAuto** installieren und Home Assistant neu starten.
4. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach **Geld für eAuto** suchen.
5. Für persönliche Daten E-Mail und Passwort eingeben; beide Felder leer lassen für öffentliche Standardprämien.

## Datenschutz und Sicherheit

- Zugangsdaten werden ausschließlich in Home Assistants Config Entry abgelegt. Es gibt keine hartcodierten Tokens, Kontodaten oder HAR-Dateien im Repository.
- E-Mail, IBAN und Anschrift werden nicht als Sensorattribute ausgegeben.
- Keine schreibenden oder zahlungsbezogenen Aktionen.
- Da die zugrunde liegenden Webseiten-Endpunkte undokumentiert sind, können sie sich ändern.
- Für eine Änderung bestehender Zugangsdaten muss die Konfiguration derzeit entfernt und erneut eingerichtet werden.

## Entwicklerhinweise

- Domain: `geld_fuereauto`
- Kunden-Endpunkte und Schema: [docs/api-endpoints.md](docs/api-endpoints.md)
- Derzeit werden Fahrzeuge nach erstmaligem Setup als Entitäten angelegt. Werden später weitere Fahrzeuge hinzugefügt, ist eine erneute Einrichtung erforderlich, bis dynamische Discovery ergänzt wird.

Nicht mit der ZusammenStromen GmbH verbunden.
