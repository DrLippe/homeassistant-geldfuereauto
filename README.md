# Geld für eAuto – Home Assistant Integration

Inoffizielle HACS-Integration für [Geld für eAuto](https://geld-fuer-eauto.de/).

## Funktionsumfang (v0.1.0)

- Öffentliche THG-Standardprämien für die Fahrzeugklassen M1, N1, N2, N3 und M3
- Garantie- und Expressbetrag in EUR sowie Risikoanteil in Prozent, getrennt nach Quotenjahr
- Tägliche Aktualisierung und manuelle Aktualisierung über Home Assistant
- Einrichtung direkt über den Home-Assistant-Config-Flow, ohne Zugangsdaten
- Deutsche und englische Oberfläche

**Wichtig:** Die öffentlich dokumentierte Website enthält Standardpreise, aber keine bestätigte lesende API für das persönliche Kundenkonto. Deshalb zeigt diese erste Version **keine** eigenen Anträge, Fahrzeuge, Auszahlungen oder Kontostände an. Die angezeigten Standardprämien sind unverbindlich. Maßgeblich ist die Anbieterbestätigung.

## HACS-Installation

1. In HACS **Benutzerdefinierte Repositories** öffnen.
2. `https://github.com/DrLippe/homeassistant-geldfuereauto` hinzufügen, Typ **Integration**.
3. **Geld für eAuto** installieren und Home Assistant neu starten.
4. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach **Geld für eAuto** suchen.

## Datenquelle

Öffentliche Standardpreistabelle: https://geld-fuer-eauto.de/fuer-ai/preise

Die Daten werden einmal täglich eingelesen. Die Implementierung nutzt keine geheimen API-Endpunkte, keine Zugangsdaten und keine Antragserstellung.

## Entwicklung

Domain: `geld_fuereauto`

Der öffentliche Tarifabruf ist bewusst von einer späteren, separat zu implementierenden Kundenkonto-API getrennt. Eine solche API muss vor Einbindung technisch und rechtlich geprüft werden.

Nicht mit der ZusammenStromen GmbH verbunden.
