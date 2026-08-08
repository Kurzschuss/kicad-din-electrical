# Identitätsmodell

**Dokument-ID:** PLT-0005  
**Titel:** Gemeinsames Modell für Akteursidentitäten  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert Akteursidentitäten der Plattform. Eine Akteursidentität beschreibt eindeutig, wer oder was innerhalb von ProjectOS handeln, Verantwortung tragen, adressiert, autorisiert oder auditiert werden kann.

Sie ist von der universellen Objektidentität des Core zu unterscheiden.

## 2. Architekturstellung

Die Akteursidentität gehört zur Plattformebene.

Der Core kennt stabile Objektidentitäten und darf opake Akteursreferenzen tragen, kennt aber weder Benutzer noch Konten, Rollen oder Authentifizierungsverfahren.

Die Identitätsplattform löst solche Referenzen auf und stellt sie höheren Plattformdiensten und Domänen zur Verfügung.

## 3. Grundsatz

Identität beantwortet die Frage:

> Wer oder was ist der handelnde oder verantwortliche Akteur?

Sie beantwortet ausdrücklich nicht automatisch:

- wie sich der Akteur authentifiziert;
- welche Berechtigungen er besitzt;
- welchem Konto er zugeordnet ist;
- welche Rolle er innehat;
- in welcher Sitzung er arbeitet.

Diese Aspekte werden getrennt modelliert.

## 4. Identitätsarten

Die Plattform muss mindestens folgende Akteursarten abbilden können:

- menschliche Person bzw. Benutzeridentität;
- technische Dienstidentität;
- Geräteidentität;
- API-Client-Identität;
- Automatisierungsidentität;
- externe bzw. föderierte Identität.

Weitere Identitätsarten dürfen ergänzt werden, sofern sie den gemeinsamen Identitätsvertrag erfüllen.

## 5. Gemeinsamer Identitätskern

Eine Akteursidentität beschreibt mindestens:

- stabile Identitäts-ID;
- Identitätsart;
- Anzeigename bzw. technische Bezeichnung;
- Lebenszyklusstatus;
- Herkunft bzw. Identitätsquelle;
- optionale externe Identifikatoren;
- Beziehungen zu Konten, Organisationen, Projekten oder technischen Ressourcen;
- Historien- und Auditbezüge;
- optionale Vertrauens- oder Verifikationsinformationen.

Geheimnisse, Kennwörter oder Authentifizierungsschlüssel gehören nicht in den allgemeinen Identitätskern.

## 6. Stabilität

Eine Identitäts-ID bleibt stabil, auch wenn sich Name, E-Mail-Adresse, Konto, Organisation, Rolle oder Authentifizierungsverfahren ändern.

Identitäts-IDs dürfen nach endgültiger Stilllegung nicht für einen anderen Akteur wiederverwendet werden.

## 7. Menschliche Identität und Benutzer

Eine menschliche Identität ist nicht mit einem Benutzerkonto gleichzusetzen.

Ein Mensch kann beispielsweise:

- mehrere Konten besitzen;
- zeitweise kein aktives Konto besitzen;
- über unterschiedliche Authentifizierungswege verfügen;
- Mitglied mehrerer Organisationen oder Projekte sein;
- verschiedene Rollen je Gültigkeitsbereich innehaben.

Das spätere `USER_MODEL.md` beschreibt die benutzerspezifische Sicht auf menschliche Akteure. Das `ACCOUNT_MODEL.md` beschreibt Zugangskonten.

## 8. Technische Identitäten

Dienste, Geräte, API-Clients und Automatisierungen können eigenständig handeln und müssen deshalb eigenständige Akteursidentitäten besitzen können.

Eine technische Identität darf nicht künstlich als menschlicher Benutzer modelliert werden.

Technische Identitäten müssen im Audit eindeutig von menschlichen Identitäten unterscheidbar sein.

## 9. Externe Identitäten

Externe Identitätsanbieter können externe Kennungen bereitstellen.

Eine externe Kennung ist nicht automatisch die interne stabile Identitäts-ID.

Die Plattform muss eine kontrollierte Zuordnung zwischen interner Identität und externen Identifikatoren ermöglichen, ohne die interne Identität an einen einzelnen Anbieter zu binden.

## 10. Identität und Konto

Identität und Konto sind getrennt.

Ein Konto beschreibt einen Zugang oder eine technische Zugangseinheit.

Eine Identität beschreibt den Akteur.

Je nach Identitätsart und Richtlinie kann eine Identität null, ein oder mehrere Konten besitzen oder referenzieren.

Das Sperren eines Kontos muss nicht zwingend die Identität selbst stilllegen.

## 11. Identität und Authentifizierung

Authentifizierung weist nach, dass ein Nutzungskontext zu einer behaupteten Identität gehört.

Die Identität selbst definiert kein Kennwort-, Token-, Zertifikats- oder Mehrfaktorverfahren.

Offline- und Online-Authentifizierung dürfen unterschiedliche Nachweisverfahren verwenden, müssen aber auf eine eindeutige Akteursidentität abbilden.

## 12. Identität und Autorisierung

Eine Identität besitzt nicht allein durch ihre Existenz Berechtigungen.

Autorisierung bewertet unter anderem:

- Identität;
- Gültigkeitsbereich;
- Rollen;
- direkte Berechtigungen;
- Ausnahmerechte;
- Projekt- und Organisationsbeziehungen;
- Delegationen;
- Sperren und Ausschlüsse;
- Sitzungskontext;
- Richtlinien.

Die Entscheidung gehört in das spätere `AUTHORIZATION_MODEL.md`.

## 13. Rollen und Berechtigungen

Rolle und Berechtigung sind keine Eigenschaften der Identität im engeren Sinn.

Sie werden über Beziehungen und Gültigkeitsbereiche zugeordnet.

Dadurch kann dieselbe Identität beispielsweise in Projekt A Projektleiter, in Projekt B Reviewer und in einer Organisation normales Mitglied sein.

## 14. Gültigkeitsbereiche

Identitätsbezogene Beziehungen können unterschiedliche Gültigkeitsbereiche besitzen, beispielsweise:

- global;
- Organisation;
- Projekt;
- Workspace;
- Domäne;
- Objektgruppe;
- einzelnes Objekt;
- Sitzung.

Die Existenz einer Identität ist jedoch nicht auf einen einzelnen Gültigkeitsbereich reduziert.

## 15. Erweiterte Verantwortungsbeziehungen

Die Identitätsplattform muss Beziehungen unterstützen können, die für die geplante Benutzerverwaltung erforderlich sind, darunter insbesondere:

- Projektleiter;
- Stellvertretung;
- Vertrauensperson;
- Nachfolger;
- fachlich Verantwortlicher;
- Reviewer;
- Freigabeverantwortlicher;
- delegierter Vertreter.

Diese Beziehungen verleihen nicht automatisch identische Berechtigungen. Ihre konkrete Wirkung wird durch Autorisierung und Delegationsregeln festgelegt.

## 16. Whitelist und Blacklist

Whitelist- und Blacklist-Mechanismen dürfen nicht als unveränderliche Eigenschaften einer Identität modelliert werden.

Sie sind Richtlinien- bzw. Autorisierungselemente mit definiertem Gültigkeitsbereich, Priorität, Begründung und gegebenenfalls zeitlicher Gültigkeit.

Eine Blacklist-Regel kann eine grundsätzlich vorhandene Berechtigung ausdrücklich verweigern. Konflikt- und Prioritätsregeln werden im Berechtigungs- und Autorisierungsmodell festgelegt.

## 17. Ausnahmerechte

Ausnahmerechte müssen explizit, begründet, begrenzt und auditierbar sein.

Sie dürfen reguläre Rollen- und Berechtigungsmodelle nicht unsichtbar umgehen.

Mindestens müssen Akteur, gewährende Instanz, Gültigkeitsbereich, Zweck, Beginn und – soweit anwendbar – Ablauf oder Widerruf nachvollziehbar sein.

## 18. Delegation

Eine Identität kann unter kontrollierten Bedingungen Befugnisse oder Verantwortlichkeiten an eine andere Identität delegieren.

Delegation ist keine Identitätsverschmelzung.

Originalakteur, delegierende Identität, ausführende Identität, Umfang und Gültigkeit müssen unterscheidbar bleiben.

Die vollständigen Regeln werden in `DELEGATION_MODEL.md` definiert.

## 19. Lebenszyklus

Eine Akteursidentität besitzt einen Lebenszyklus. Konzeptionell werden mindestens unterschieden:

- angelegt;
- aktiv;
- eingeschränkt;
- gesperrt;
- stillgelegt;
- archiviert.

Die genaue Zustandsmaschine wird über das Identitätsschema festgelegt.

Stilllegung oder Archivierung darf historische Audit- und Verantwortungsreferenzen nicht zerstören.

## 20. Löschen und Datenschutz

Fachliche Nachvollziehbarkeit und Datenschutz müssen getrennt behandelt werden.

Eine Identität kann personenbezogene oder vertrauliche Attribute besitzen, die entfernt, anonymisiert oder eingeschränkt werden müssen, während stabile historische Referenzen erhalten bleiben müssen.

Die konkrete Datenschutz- und Aufbewahrungsstrategie wird nicht in diesem Dokument festgelegt.

## 21. Offline-First

Die Plattform muss für den vorgesehenen Offline-Betrieb die lokal erforderlichen Identitätsreferenzen und Autorisierungskontexte verfügbar halten können.

Offline verfügbare Daten müssen klar von nicht verfügbaren oder möglicherweise veralteten externen Identitätsinformationen unterscheidbar sein.

Eine externe Identitätsquelle darf den lokalen Projektbetrieb nicht unnötig blockieren.

## 22. Audit

Jede sicherheits- oder verantwortungsrelevante Handlung muss auf die tatsächlich handelnde Akteursidentität zurückführbar sein.

Bei Delegation oder Stellvertretung müssen sowohl ausführende als auch relevante vertretene bzw. delegierende Identitäten nachvollziehbar bleiben.

Technische Automatisierungen dürfen nicht unter einer unspezifischen Sammelidentität verschwinden, wenn individuelle Nachvollziehbarkeit erforderlich ist.

## 23. Validierung

Eine Identität ist mindestens darauf zu prüfen, dass:

1. eine stabile Identitäts-ID vorhanden ist;
2. die Identitätsart bekannt ist;
3. der Lebenszyklusstatus gültig ist;
4. externe Identifikatoren eindeutig und ihrer Quelle zugeordnet sind;
5. Konten nicht mit der Identität selbst verwechselt werden;
6. Beziehungen gültige Typen und Gültigkeitsbereiche besitzen;
7. technische und menschliche Identitäten unterscheidbar bleiben;
8. historische Referenzen bei Stilllegung erhalten bleiben;
9. sicherheitsrelevante Ausnahmen und Delegationen auditierbar referenziert sind.

## 24. Invarianten

1. Eine Akteursidentität besitzt genau eine stabile interne Identitäts-ID.
2. Identitäts-ID und Objekt-ID sind konzeptionell unterscheidbar, auch wenn eine Identität als Plattformobjekt gespeichert wird.
3. Identität und Konto sind getrennt.
4. Identität und Authentifizierung sind getrennt.
5. Identität und Autorisierung sind getrennt.
6. Rolle und Berechtigung sind nicht Teil der unveränderlichen Identität.
7. Technische Akteure benötigen keine künstlichen menschlichen Benutzerkonten.
8. Externe Provider-IDs ersetzen nicht die interne Identitäts-ID.
9. Delegation verschmilzt keine Identitäten.
10. Stilllegung zerstört keine erforderlichen historischen Referenzen.

## 25. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- Benutzerprofile im Detail;
- Kontostrukturen;
- Kennwortregeln;
- konkrete MFA-Verfahren;
- Tokenformate;
- Rollenstruktur;
- Berechtigungsauflösung;
- Organisationsmodell;
- Sitzungsformat;
- konkrete Whitelist-/Blacklist-Prioritätsalgorithmen;
- Datenschutzfristen;
- konkrete externe Identity Provider.

## 26. Folgemodelle

Auf diesem Modell bauen insbesondere auf:

- `USER_MODEL.md`;
- `ACCOUNT_MODEL.md`;
- `AUTHENTICATION_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- `ROLE_MODEL.md`;
- `PERMISSION_MODEL.md`;
- `ORGANIZATION_MODEL.md`;
- `SESSION_MODEL.md`;
- `DELEGATION_MODEL.md`;
- `AUDIT_MODEL.md`.

## 27. Abhängigkeiten

Dieses Dokument basiert auf:

- `PLATFORM_MODEL.md`;
- `PROJECT_MODEL.md`;
- `WORKSPACE_MODEL.md`;
- `OBJECT_MODEL.md`;
- `OBJECT_INTERFACE.md`;
- `RELATION_MODEL.md`;
- `ADR-0002-identitaet-als-plattformkonzept.md`;
- `ADR-0003-architekturebenen-und-kernelgrenze.md`;
- `ADR-0004-core-referenzen-und-schema-bootstrap.md`.

## 28. Ergebnis

Akteursidentität ist als eigenständiges Plattformkonzept definiert. Menschen, Dienste, Geräte, API-Clients, Automatisierungen und externe Identitäten können auf derselben Grundlage eindeutig referenziert werden, ohne Benutzer, Konto, Authentifizierung, Autorisierung, Rolle oder Berechtigung miteinander zu vermischen.
