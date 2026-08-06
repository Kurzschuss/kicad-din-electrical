# ADR-0002: Identität als Plattformkonzept

**Dokument-ID:** ADR-0002  
**Titel:** Identität als eigenständiges Plattformkonzept  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** A  
**Entscheidungsart:** Grundlegende Architekturentscheidung  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Kontext

Die bisherige Bezeichnung „Benutzerverwaltung“ ist für den geplanten Funktionsumfang zu eng.

Das System muss nicht nur natürliche Personen verwalten, sondern auch technische Akteure, Konten, Sitzungen, Rollen, Berechtigungen, Organisationen, Geräte, Dienste, Automatisierungen und API-Clients eindeutig identifizieren und kontrolliert autorisieren.

Das Objektmodell und die Objektschnittstelle verwenden bereits Referenzen wie `created_by`, `modified_by`, Eigentümer und Verantwortliche. Diese Referenzen dürfen nicht ausschließlich an Benutzerkonten gebunden werden, da auch technische Akteure und automatisierte Prozesse Änderungen ausführen können.

## 2. Problemstellung

Eine klassische Benutzerverwaltung vermischt häufig mehrere unterschiedliche Konzepte:

- natürliche Person;
- fachliche Identität;
- Benutzerkonto;
- Anmeldeverfahren;
- Sitzung;
- Rolle;
- Berechtigung;
- Organisation;
- Eigentum und Verantwortung;
- technische Identität.

Diese Vermischung erschwert Offline-Betrieb, Auditierbarkeit, Delegation, Dienstkonten, Geräteidentitäten, API-Zugriffe und eine spätere Erweiterung der Plattform.

## 3. Entscheidung

Identität wird als eigenständiges, domänenübergreifendes Plattformkonzept modelliert.

Die bisher geplante Benutzerverwaltung wird in getrennte, aber zusammengehörige Modelle aufgeteilt:

1. `IDENTITY_MODEL.md` – fachliche Identitäten und Identitätstypen;
2. `USER_MODEL.md` – natürliche Personen als fachliche Akteure;
3. `ACCOUNT_MODEL.md` – verwaltete Zugangskonten;
4. `AUTHENTICATION_MODEL.md` – Nachweis einer behaupteten Identität;
5. `AUTHORIZATION_MODEL.md` – Entscheidung über erlaubte Handlungen;
6. `ROLE_MODEL.md` – Bündelung fachlicher Verantwortlichkeiten;
7. `PERMISSION_MODEL.md` – einzelne Erlaubnisse und Geltungsbereiche;
8. `ORGANIZATION_MODEL.md` – Organisationen, Teams und Zugehörigkeiten;
9. `SESSION_MODEL.md` – authentifizierte Nutzungskontexte;
10. `DELEGATION_MODEL.md` – zeitlich und fachlich begrenzte Übertragung von Rechten;
11. `AUDIT_MODEL.md` – nachvollziehbare sicherheitsrelevante Vorgänge.

Die Bezeichnung `USER_MANAGEMENT.md` wird nicht als maßgebliches Gesamtmodell verwendet. Sie darf später höchstens als Übersichts- oder Navigationsdokument dienen.

## 4. Begriffsabgrenzung

### 4.1 Identität

Eine Identität bezeichnet einen eindeutig referenzierbaren Akteur oder Verantwortungsbezug innerhalb der Plattform.

Eine Identität kann insbesondere repräsentieren:

- einen Benutzer;
- ein Gerät;
- einen Dienst;
- ein Servicekonto;
- einen API-Client;
- eine Automatisierung;
- einen definierten Systemprozess.

### 4.2 Benutzer

Ein Benutzer ist eine natürliche Person mit fachlicher Identität.

Ein Benutzer ist nicht mit einem Konto, einer Rolle oder einer Sitzung gleichzusetzen.

### 4.3 Konto

Ein Konto ist ein verwalteter Zugangskontext, über den sich eine Identität authentifizieren kann.

Eine Identität kann mehrere Konten besitzen. Ein Konto darf nur nach ausdrücklich definierten Regeln mehreren Identitäten zugeordnet werden.

### 4.4 Authentifizierung

Authentifizierung prüft, ob eine behauptete Identität glaubhaft nachgewiesen wurde.

Sie beantwortet nicht, welche Handlung erlaubt ist.

### 4.5 Autorisierung

Autorisierung entscheidet, ob eine Identität eine bestimmte Handlung auf einem bestimmten Objekt oder innerhalb eines bestimmten Geltungsbereichs ausführen darf.

### 4.6 Rolle und Berechtigung

Eine Rolle bündelt fachliche Verantwortlichkeiten oder typische Berechtigungen.

Eine Berechtigung beschreibt eine konkrete erlaubte Handlung in einem definierten Geltungsbereich.

Rolle und Berechtigung sind nicht gleichbedeutend.

## 5. Architekturregeln

1. Sicherheitsrelevante Verweise beziehen sich auf Identitäten, nicht ausschließlich auf Benutzerkonten.
2. Authentifizierung und Autorisierung bleiben getrennte Verantwortungsbereiche.
3. Kontostatus und fachlicher Identitätsstatus werden getrennt modelliert.
4. Rollen ersetzen keine ausdrücklichen Berechtigungsentscheidungen.
5. Berechtigungen besitzen einen klaren Geltungsbereich.
6. Eigentum, Verantwortung, Rolle und Berechtigung werden nicht gleichgesetzt.
7. Technische Akteure verwenden dieselben grundlegenden Audit- und Identitätsregeln wie menschliche Akteure.
8. Offline-Betrieb muss für lokale Identitäten und Berechtigungsentscheidungen grundsätzlich möglich bleiben.
9. Sicherheitsrelevante Änderungen müssen einer nachverfolgbaren Identität oder einem ausdrücklich definierten Systemprozess zugeordnet sein.
10. Anonyme Vorgänge sind nur erlaubt, wenn sie ausdrücklich spezifiziert und sicherheitlich begründet sind.

## 6. Identitätstypen

Das Identitätsmodell muss mindestens folgende Kategorien unterstützen können:

- menschliche Identität;
- Geräteidentität;
- Dienstidentität;
- API-Client-Identität;
- Automatisierungsidentität;
- Systemidentität.

Die genaue Typstruktur wird in `IDENTITY_MODEL.md` festgelegt.

## 7. Organisation und Zugehörigkeit

Organisationen, Teams, Gruppen und Projekte sind keine Rollen.

Zugehörigkeit beschreibt eine Beziehung zwischen Identität und Organisationseinheit.

Aus einer Zugehörigkeit können über dokumentierte Regeln Rollen oder Berechtigungen abgeleitet werden. Die Zugehörigkeit selbst ist jedoch keine Berechtigungsentscheidung.

## 8. Delegation

Die Plattform muss delegierte Rechte unterstützen können.

Eine Delegation besitzt mindestens:

- delegierende Identität;
- empfangende Identität;
- delegierten Umfang;
- Geltungsbereich;
- Beginn und Ende;
- Status;
- Widerrufsmöglichkeit;
- Audit-Nachweis.

Eine Delegation darf keine Rechte übertragen, die die delegierende Identität nicht selbst übertragen darf.

## 9. Sitzungen

Eine Sitzung ist ein zeitlich begrenzter, authentifizierter Nutzungskontext.

Sie besitzt eine eigene Identität oder stabile Referenz und ist mindestens einer authentifizierten Identität, einem Konto, einem Authentifizierungsverfahren und einem Gültigkeitszeitraum zugeordnet.

Das Beenden oder Sperren einer Sitzung verändert nicht automatisch die fachliche Identität des Benutzers.

## 10. Offline-First

Lokale Identitäten, Konten und Berechtigungsentscheidungen müssen ohne permanente Verbindung zu einem externen Identitätsanbieter funktionieren können, sofern der konkrete Betriebsmodus dies erfordert.

Externe Identitätsanbieter dürfen angebunden werden, werden aber nicht automatisch zur einzigen maßgeblichen Quelle aller Identitäts- und Berechtigungsdaten.

Konflikte zwischen lokalen und externen Identitäten müssen ausdrücklich auflösbar sein.

## 11. Audit und Nachvollziehbarkeit

Sicherheitsrelevante Vorgänge müssen nachvollziehbar sein.

Dazu gehören insbesondere:

- Anmeldung und Abmeldung;
- fehlgeschlagene Authentifizierungen;
- Kontoaktivierung und Kontosperrung;
- Rollen- und Berechtigungsänderungen;
- Delegationen und Widerrufe;
- Sitzungsbeendigung;
- Änderungen an Identitätszuordnungen;
- Notfall- und Wiederherstellungszugriffe.

Audit-Daten sind von normalen Fachobjekthistorien zu unterscheiden, können aber auf dieselben Identitäten und Objekte verweisen.

## 12. Betrachtete Alternativen

### 12.1 Einfache Benutzerverwaltung

Benutzer, Konto, Rolle und Berechtigungen werden in einem gemeinsamen Modell zusammengefasst.

Diese Alternative wurde verworfen, da sie menschliche und technische Akteure vermischt und langfristig zu unklaren Verantwortlichkeiten führt.

### 12.2 Kontozentriertes Modell

Das Benutzerkonto wird zur primären Identität des Systems.

Diese Alternative wurde verworfen, weil Konten austauschbar, sperrbar oder mehrfach vorhanden sein können, während die fachliche Identität fortbesteht.

### 12.3 Externer Identitätsanbieter als alleinige Quelle

Alle Identitäten werden ausschließlich durch einen Cloud- oder Verzeichnisdienst verwaltet.

Diese Alternative wurde als allgemeine Plattformregel verworfen, da sie Offline-First, Portabilität und lokale Kontrollierbarkeit einschränkt.

### 12.4 Rollen als alleiniger Autorisierungsmechanismus

Alle Zugriffe werden ausschließlich über Rollen entschieden.

Diese Alternative wurde verworfen, da objektbezogene, zeitlich begrenzte, delegierte und kontextabhängige Rechte damit nicht ausreichend präzise abbildbar sind.

## 13. Konsequenzen

### Positive Konsequenzen

- klare Trennung fachlicher und technischer Identitäten;
- Unterstützung menschlicher und technischer Akteure;
- bessere Auditierbarkeit;
- kontrollierte Delegation;
- mehrere Konten pro Identität;
- Offline- und externe Authentifizierung können koexistieren;
- Rollen und Berechtigungen bleiben erweiterbar;
- Objektänderungen können einheitlich Akteuren zugeordnet werden.

### Negative Konsequenzen

- höhere Modellierungs- und Implementierungskomplexität;
- mehr getrennte Dokumente und Dienste;
- Migration einfacher Kontomodelle wird aufwendiger;
- Berechtigungsentscheidungen benötigen klar definierte Geltungsbereiche;
- Synchronisation externer und lokaler Identitäten erfordert Konfliktregeln.

Diese Nachteile werden bewusst akzeptiert.

## 14. Nicht festgelegt

Dieses ADR legt noch nicht fest:

- konkrete Authentifizierungsverfahren;
- Passwortregeln;
- Mehrfaktorverfahren;
- Token- oder Sitzungsformate;
- konkrete Rollen;
- konkrete Berechtigungen;
- Datenbank- oder API-Strukturen;
- externen Identitätsanbieter;
- UUID- oder Kennungsformate;
- genaue Vererbungs- und Konfliktregeln.

Diese Punkte werden in den jeweiligen Modellen, Spezifikationen oder weiteren ADRs festgelegt.

## 15. Auswirkungen auf bestehende Dokumente

- `OBJECT_INTERFACE.md` verwendet für Akteursangaben Identitätsreferenzen.
- `OBJECT_SERVICE.md` fordert eine handelnde Identität und getrennte Berechtigungsprüfung.
- `PROJECT_GLOSSARY.md` bleibt für die Begriffe Benutzer, Konto, Authentifizierung, Autorisierung, Rolle und Berechtigung maßgeblich.
- Die bisher geplante Datei `USER_MANAGEMENT.md` wird durch die in diesem ADR beschlossene Modellgruppe ersetzt oder zu einem nicht normativen Übersichtsartefakt reduziert.

## 16. Akzeptanzkriterien

Dieses ADR gilt als umgesetzt, wenn:

- `IDENTITY_MODEL.md` angelegt ist;
- Benutzer und Konto getrennt modelliert sind;
- Authentifizierung und Autorisierung getrennte Modelle besitzen;
- Rollen und Berechtigungen nicht gleichgesetzt werden;
- menschliche und technische Identitäten unterstützt werden;
- Objektänderungen auf Identitäten verweisen;
- Sitzungen, Organisationen und Delegationen eigene Verantwortlichkeiten besitzen;
- Offline-Betrieb im Identitätsmodell berücksichtigt ist.

## 17. Entscheidungsergebnis

Die Plattform verwendet keine monolithische Benutzerverwaltung.

Identität wird als eigenständiges Plattformkonzept behandelt. Benutzer, Konten, Authentifizierung, Autorisierung, Rollen, Berechtigungen, Organisationen, Sitzungen, Delegationen und Audit werden als getrennte, aufeinander abgestimmte Modelle entwickelt.
