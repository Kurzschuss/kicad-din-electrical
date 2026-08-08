# Z_Cockpit – Integration der Identitätsplattform

**Dokument-ID:** INT-0001  
**Titel:** Integrationsregeln für Identität und Benutzerverwaltung im Z_Cockpit  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Integrationsvertrag  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert, wie Identitäten, Benutzer, Konten, Rollen, Berechtigungen, Organisationen, Sitzungen, Delegationen und Auditinformationen im `Z_Cockpit` dargestellt und bedient werden.

Das `Z_Cockpit` ist Bedien- und Sichtoberfläche der Plattform. Es ist keine zweite fachliche Quelle der Wahrheit.

## 2. Bestehendes Z_Cockpit-Muster

Für Z_Cockpit-Funktionen gilt weiterhin das bereits etablierte Entwicklungsprinzip:

```text
maßgebliches Plattformmodell / Engine
        ↓
getestetes, darstellungsunabhängiges View-/Abfragemodell
        ↓
getesteter Renderer bzw. Seitenbaustein
        ↓
kleine Integration in den Cockpit-Generator
```

Fachlogik wird nicht in HTML, Navigation oder Renderer dupliziert.

## 3. Single Source of Truth

Maßgeblich bleiben die Plattformmodelle und Plattformdienste.

Das Z_Cockpit darf:

- Daten lesen und aufbereiten;
- berechtigungsabhängige Sichten anzeigen;
- zulässige Aktionen anbieten;
- Befehle an Plattformdienste auslösen;
- Ergebnisse und Fehler darstellen.

Das Z_Cockpit darf nicht:

- eigene Benutzer- oder Rollenwahrheiten führen;
- Berechtigungen ausschließlich im UI entscheiden;
- fachliche Zustände nur in HTML speichern;
- Sicherheitsregeln durch ausgeblendete Bedienelemente ersetzen;
- Konten oder Identitäten außerhalb der Plattformdienste verändern.

## 4. Geplante Cockpit-Bereiche

Die Identitätsplattform soll im Z_Cockpit mindestens folgende Bereiche erhalten können:

- Identitäten;
- Benutzer;
- Konten;
- Rollen;
- Berechtigungen;
- Organisationen und Teams;
- Projektverantwortung;
- Stellvertretungen und Delegationen;
- Sitzungen;
- Sicherheits- und Kontostatus;
- Audit und sicherheitsrelevante Ereignisse.

Die konkrete Seitenteilung kann später verändert werden, ohne die fachlichen Modelle zu verändern.

## 5. Benutzerübersicht

Eine Benutzeransicht darf unter anderem darstellen:

- stabile Identitätsreferenz;
- Anzeigename;
- Benutzerstatus;
- Organisations- und Projektzugehörigkeiten;
- Verantwortungsbeziehungen;
- zugeordnete Konten;
- effektive Rollen je Gültigkeitsbereich;
- relevante Einschränkungen oder Delegationen.

Geheimnisse oder Authentifizierungsnachweise werden nicht angezeigt.

## 6. Erweiterte Verantwortungsbeziehungen

Das Z_Cockpit muss die geplanten Beziehungen getrennt darstellen können:

- Projektleiter;
- Stellvertretung;
- Vertrauensperson;
- Nachfolger;
- fachlich Verantwortlicher;
- Reviewer;
- Freigabeverantwortlicher;
- delegierter Vertreter.

Eine sichtbare Beziehung darf nicht fälschlich als automatisch identische Berechtigung dargestellt werden.

Bei Stellvertretung oder Delegation müssen mindestens Originalverantwortung, ausführende Identität, Gültigkeitsbereich und zeitliche Gültigkeit erkennbar sein.

## 7. Rollen und Berechtigungen

Das Cockpit darf Rollen und Berechtigungen anzeigen und – bei entsprechender Autorisierung – deren Verwaltung auslösen.

Die effektive Berechtigung wird jedoch ausschließlich durch die Autorisierungsplattform ermittelt.

Die UI darf keine eigene vereinfachte Berechnungslogik führen.

Soweit möglich soll das Cockpit unterscheiden zwischen:

- durch Rolle gewährten Rechten;
- direkt gewährten Rechten;
- delegierten Rechten;
- Ausnahmerechten;
- ausdrücklich verweigerten Rechten;
- geerbten oder aus Beziehungen abgeleiteten Rechten.

## 8. Whitelist und Blacklist

Whitelist- und Blacklist-Regeln werden nicht als einfache Benutzer-Schalter dargestellt.

Eine Cockpit-Ansicht soll – soweit der Benutzer dies sehen darf – mindestens darstellen können:

- Regelart;
- Ziel bzw. betroffene Identität oder Ressource;
- Gültigkeitsbereich;
- Begründung;
- erteilende oder sperrende Instanz;
- Beginn;
- Ablauf oder Widerruf;
- aktuellen Wirksamkeitsstatus.

Eine Blacklist oder ausdrückliche Verweigerung muss klar von einer fehlenden Berechtigung unterscheidbar sein.

## 9. Ausnahmerechte

Ausnahmerechte sind besonders sichtbar und auditierbar zu behandeln.

Das Z_Cockpit darf ein Ausnahmerecht nur dann als aktiv darstellen, wenn die Plattform dessen Wirksamkeit bestätigt.

Darzustellen sind mindestens:

- Begünstigter;
- gewährende Instanz;
- Zweck;
- Gültigkeitsbereich;
- Beginn;
- Ablauf bzw. Widerruf;
- Auditbezug.

## 10. Konto- und Authentifizierungsstatus

Das Cockpit kann Kontostatus und registrierte Authentifizierungsarten darstellen, beispielsweise:

- aktiv;
- eingeschränkt;
- gesperrt;
- deaktiviert;
- externer Provider;
- MFA erforderlich bzw. registriert;
- Offline-Nutzung zulässig oder nicht zulässig.

Nicht dargestellt oder übertragen werden dürfen Klartextkennwörter, private Schlüssel, ungeschützte Tokens oder vergleichbare Geheimnisse.

## 11. Aktionen

Ändernde Cockpit-Aktionen werden als explizite Plattformbefehle ausgeführt.

Beispiele:

- Benutzerbeziehung zuweisen;
- Konto sperren;
- Rolle zuweisen oder entziehen;
- Berechtigung ändern;
- Stellvertretung aktivieren;
- Delegation widerrufen;
- Sitzung beenden.

Die Oberfläche darf vorab Bedienbarkeit prüfen, aber die Plattform muss jede Operation server- bzw. dienstseitig nochmals vollständig autorisieren und validieren.

## 12. Berechtigungsabhängige Sichtbarkeit

Das Z_Cockpit darf nur Informationen anzeigen, deren Offenlegung für die aktuelle Identität zulässig ist.

Dazu gehören insbesondere Einschränkungen für:

- personenbezogene Daten;
- Kontostatus anderer Benutzer;
- sicherheitsrelevante Rollen;
- Ausnahmerechte;
- Auditinformationen;
- aktive Sitzungen;
- technische Identitäten.

Das Verbergen einer Information in der UI ersetzt keine Zugriffskontrolle am Dienst.

## 13. Aktiver Nutzungskontext

Das Cockpit soll den aktuellen Nutzungskontext eindeutig sichtbar machen, insbesondere:

- angemeldete Identität;
- verwendetes Konto, soweit relevant;
- aktives Projekt;
- aktiver Workspace;
- aktive Organisation;
- aktive Stellvertretung oder Delegation;
- Offline-/Online-Status.

Handelt ein Benutzer stellvertretend oder delegiert, darf die Oberfläche dies nicht so darstellen, als handle er unter einer fremden Identität.

## 14. Offline-First

Im Offline-Betrieb muss das Z_Cockpit unterscheiden können zwischen:

- lokal autoritativ verfügbaren Informationen;
- lokal zwischengespeicherten Informationen;
- möglicherweise veralteten externen Informationen;
- nicht verfügbaren Informationen.

Ein nicht erreichbarer externer Identity Provider darf nicht als Kontosperre oder Identitätslöschung fehlinterpretiert werden.

## 15. Audit und Sicherheitsereignisse

Das Cockpit erfindet kein eigenes Auditmodell.

Audit- und Sicherheitsanzeigen verwenden die kanonischen Plattformdaten und das bestehende Sicherheitsereignismodell.

Sicherheitsrelevante Aktionen aus dem Cockpit müssen denselben Audit- und Ereignisweg verwenden wie Aktionen aus CLI, API oder anderen Oberflächen.

## 16. Fehlerdarstellung

Das Z_Cockpit zeigt fachliche Fehler ausdrücklich an.

Mindestens zu unterscheiden sind:

- nicht autorisiert;
- Identität oder Referenz nicht auflösbar;
- Konto gesperrt;
- Konflikt oder veralteter Zustand;
- Validierungsfehler;
- externe Quelle nicht verfügbar;
- Operation technisch fehlgeschlagen.

Ein fehlgeschlagener Änderungsvorgang darf nicht als lokal erfolgreicher Cockpit-Zustand fortgeführt werden.

## 17. View-Modelle und Projektionen

Für komplexe Cockpit-Seiten dürfen spezielle Read Models bzw. Projektionen aufgebaut werden.

Diese sind abgeleitete Sichten und keine neue normative Quelle.

Sie müssen aus den maßgeblichen Plattformdaten reproduzierbar sein und dürfen keine eigenständige Berechtigungswahrheit erzeugen.

## 18. Tests

Jede Identitätsfunktion im Z_Cockpit soll mindestens auf drei Ebenen getestet werden:

1. fachliches Modell bzw. Dienst;
2. darstellungsunabhängiges Cockpit-View-Modell oder Adapter;
3. Renderer und sichtbare Integration.

Zusätzlich sind insbesondere zu testen:

- HTML-Escaping und sichere Ausgabe;
- berechtigungsabhängige Sichtbarkeit;
- keine Ausgabe von Geheimnissen;
- korrekte Darstellung von Delegation und Stellvertretung;
- Fehler- und Offline-Zustände;
- keine doppelte fachliche Berechtigungslogik im Renderer.

## 19. Geplanter Umsetzungsweg

Die Cockpit-Integration erfolgt nicht gleichzeitig mit der Definition jedes Plattformdokuments.

Reihenfolge:

```text
Identitäts- und Autorisierungsmodelle abschließen
        ↓
Plattformdienste und Read Models stabilisieren
        ↓
Z_Cockpit-Identitätsadapter entwickeln
        ↓
getestete Seitenbausteine entwickeln
        ↓
Navigation und Generator integrieren
```

Damit bleibt das Z_Cockpit früh mitgedacht, ohne unfertige Sicherheitslogik vorzeitig in die Oberfläche einzubauen.

## 20. Invarianten

1. Das Z_Cockpit ist nicht die Single Source of Truth für Identitäten oder Berechtigungen.
2. Keine Autorisierungsentscheidung darf ausschließlich im UI getroffen werden.
3. Keine sicherheitsrelevante Änderung umgeht den zuständigen Plattformdienst.
4. Geheimnisse werden nicht in statisch generierte Cockpit-Seiten geschrieben.
5. Delegierte oder stellvertretende Handlungen bleiben als solche erkennbar.
6. View-Modelle sind reproduzierbare Ableitungen.
7. Audit und Sicherheitsereignisse verwenden die kanonischen Plattformmodelle.
8. Offline- und veraltete Datenzustände werden sichtbar unterschieden.
9. Renderer enthalten keine konkurrierende fachliche Rollen- oder Berechtigungslogik.
10. Die bestehende modulare Z_Cockpit-Architektur wird erweitert und nicht durch eine zweite Oberfläche ersetzt.

## 21. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `PLATFORM_MODEL.md`;
- `PROJECT_MODEL.md`;
- `WORKSPACE_MODEL.md`;
- `IDENTITY_MODEL.md`;
- `USER_MODEL.md`;
- `ACCOUNT_MODEL.md`;
- `ADR-0002-identitaet-als-plattformkonzept.md`.

Spätere Versionen werden zusätzlich auf `AUTHENTICATION_MODEL.md`, `AUTHORIZATION_MODEL.md`, `ROLE_MODEL.md`, `PERMISSION_MODEL.md`, `SESSION_MODEL.md`, `DELEGATION_MODEL.md` und `AUDIT_MODEL.md` verweisen.

## 22. Ergebnis

Große Teile der Benutzer- und Identitätsverwaltung sind ausdrücklich für die Bedienung und transparente Darstellung im Z_Cockpit vorgesehen. Die fachliche Autorität verbleibt jedoch vollständig bei ProjectOS und seinen Plattformmodellen und -diensten.
