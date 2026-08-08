# Benutzermodell

**Dokument-ID:** PLT-0006  
**Titel:** Fachliches Modell eines menschlichen Benutzers  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert den menschlichen Benutzer als fachliche Sicht auf eine Akteursidentität.

Ein Benutzer ist kein Konto, keine Rolle und keine Berechtigung. Er repräsentiert einen menschlichen Akteur innerhalb der Plattform.

## 2. Architekturstellung

Das Benutzermodell baut auf `IDENTITY_MODEL.md` auf.

Es gehört zur Plattformebene und darf weder Authentifizierung noch Autorisierung in sich aufnehmen.

## 3. Definition

Ein Benutzer ist eine menschliche Akteursidentität mit benutzerspezifischen fachlichen Eigenschaften und Beziehungen.

Dazu können gehören:

- Name und Anzeigename;
- Kontaktinformationen;
- bevorzugte Sprache und Zeitzone;
- organisatorische Zugehörigkeiten;
- Projektmitgliedschaften;
- Verantwortungsbeziehungen;
- optionale Profilinformationen;
- Status und Verfügbarkeit.

## 4. Benutzer und Konto

Ein Benutzer kann null, ein oder mehrere Konten besitzen oder referenzieren.

Ein Konto ermöglicht Zugang. Der Benutzer repräsentiert die Person.

Das Sperren oder Löschen eines Kontos darf die fachliche Benutzeridentität und historische Verantwortungsbezüge nicht automatisch vernichten.

## 5. Benutzer und Rollen

Rollen werden dem Benutzer nicht als unveränderliche Eigenschaften einprogrammiert.

Sie werden über typisierte Beziehungen und einen Gültigkeitsbereich zugeordnet.

Ein Benutzer kann gleichzeitig unterschiedliche Rollen in verschiedenen Projekten, Organisationen oder Domänen besitzen.

## 6. Benutzer und Berechtigungen

Berechtigungen sind getrennte Autorisierungselemente.

Ein Benutzer kann Berechtigungen erhalten durch:

- Rollen;
- direkte Zuweisungen;
- Gruppen- oder Organisationszugehörigkeit;
- Projektbeziehungen;
- Delegationen;
- zeitlich begrenzte Ausnahmen.

Die Auswertung erfolgt nicht im Benutzermodell.

## 7. Projektbezogene Verantwortungen

Ein Benutzer kann im Projektkontext insbesondere folgende Beziehungen besitzen:

- Projektleiter;
- Stellvertretung;
- Vertrauensperson;
- Nachfolger;
- fachlich Verantwortlicher;
- Reviewer;
- Freigabeverantwortlicher;
- Mitglied;
- Beobachter.

Diese Beziehungen sind fachlich getrennt und erzeugen nicht automatisch identische Berechtigungen.

## 8. Stellvertretung

Eine Stellvertretung beschreibt, dass ein Benutzer innerhalb eines definierten Gültigkeitsbereichs Aufgaben oder Befugnisse eines anderen Benutzers wahrnehmen kann.

Sie muss mindestens definieren:

- vertretene Identität;
- stellvertretende Identität;
- Gültigkeitsbereich;
- Beginn;
- optionales Ende;
- zulässige Befugnisse;
- Ausschlüsse;
- Begründung;
- Freigabe bzw. gewährende Instanz.

Die technische und autorisierungsseitige Wirkung wird im `DELEGATION_MODEL.md` und `AUTHORIZATION_MODEL.md` festgelegt.

## 9. Vertrauensperson

Eine Vertrauensperson ist eine ausdrücklich benannte Beziehung für sensible, eskalierende oder wiederherstellungsbezogene Prozesse.

Die Beziehung darf nicht automatisch administrative Vollrechte verleihen.

Ihre konkrete Wirkung muss je Anwendungsfall ausdrücklich definiert und auditierbar sein.

## 10. Nachfolger

Eine Nachfolgerbeziehung kann festlegen, welche Identität bei Ausscheiden, Stilllegung oder langfristiger Nichtverfügbarkeit Verantwortung übernehmen soll.

Eine Nachfolgerbeziehung bewirkt nicht automatisch sofortige Berechtigungsübertragung.

Aktivierung, Umfang und Zeitpunkt müssen ausdrücklich geregelt werden.

## 11. Whitelist und Blacklist

Whitelist- und Blacklist-Regeln gehören nicht als einfache Flags in das Benutzerprofil.

Sie sind autorisierungsrelevante Regeln mit mindestens:

- Regelkennung;
- Gültigkeitsbereich;
- erlaubender oder verweigernder Wirkung;
- Begründung;
- Priorität;
- optionaler zeitlicher Gültigkeit;
- ausstellender Identität oder Instanz;
- Auditbezug.

## 12. Ausnahmerechte

Ausnahmerechte müssen explizit, zeitlich und fachlich begrenzt sowie vollständig nachvollziehbar sein.

Eine Ausnahme muss mindestens enthalten:

- begünstigten Benutzer;
- gewährende Instanz;
- betroffene Berechtigung oder Operation;
- Gültigkeitsbereich;
- Zweck;
- Beginn;
- Ablauf oder Widerrufsregel;
- Begründung;
- Auditnachweis.

## 13. Benutzerstatus

Ein Benutzer kann konzeptionell mindestens folgende Zustände besitzen:

- eingeladen;
- aktiv;
- eingeschränkt;
- gesperrt;
- inaktiv;
- ausgeschieden;
- archiviert.

Der genaue Lebenszyklus wird durch Schema und Identitätsregeln festgelegt.

## 14. Organisation und Teams

Benutzer können Organisationen, Teams und anderen organisatorischen Einheiten angehören.

Mitgliedschaft ist keine Rolle und keine Berechtigung.

Mitgliedschaften können jedoch als Eingabe für Autorisierungsregeln verwendet werden.

## 15. Datenschutz und Profildaten

Personenbezogene Profildaten sind von stabilen Identitäts- und Auditbezügen zu trennen.

Löschung, Anonymisierung oder Einschränkung personenbezogener Daten darf erforderliche historische Nachvollziehbarkeit nicht unkontrolliert zerstören.

## 16. Offline-First

Für Offline-Betrieb dürfen notwendige Benutzer- und Verantwortungsreferenzen lokal verfügbar sein.

Es muss erkennbar bleiben, ob Profildaten aktuell, veraltet oder nicht verfügbar sind.

Externe Verzeichnisdienste dürfen den lokalen Kernbetrieb nicht unnötig blockieren.

## 17. Audit

Änderungen an projektkritischen Benutzerbeziehungen müssen auditierbar sein, insbesondere:

- Projektleiterwechsel;
- Stellvertretungen;
- Vertrauenspersonen;
- Nachfolger;
- Ausnahmerechte;
- Whitelist-/Blacklist-Regeln;
- Sperrungen und Reaktivierungen.

## 18. Validierung

Ein Benutzer ist mindestens darauf zu prüfen, dass:

1. eine gültige menschliche Akteursidentität zugrunde liegt;
2. benutzerspezifische Eigenschaften dem Schema entsprechen;
3. Rollen und Berechtigungen nicht als unveränderliche Benutzerattribute missbraucht werden;
4. Verantwortungsbeziehungen eindeutige Typen und Gültigkeitsbereiche besitzen;
5. Stellvertretungen, Nachfolger und Ausnahmen nachvollziehbar sind;
6. Konten getrennt referenziert werden;
7. historische Bezüge bei Statusänderungen erhalten bleiben.

## 19. Invarianten

1. Ein Benutzer repräsentiert genau einen menschlichen Akteur.
2. Benutzer und Konto sind getrennt.
3. Benutzer und Rolle sind getrennt.
4. Benutzer und Berechtigung sind getrennt.
5. Organisationsmitgliedschaft ist keine automatische Berechtigung.
6. Stellvertretung verschmilzt keine Identitäten.
7. Nachfolger werden nicht automatisch ohne Aktivierungsregel berechtigt.
8. Whitelist-/Blacklist-Regeln sind keine einfachen Profilflags.
9. Ausnahmerechte sind explizit und auditierbar.
10. Historische Verantwortungsreferenzen bleiben bei Ausscheiden nachvollziehbar.

## 20. Abgrenzung

Dieses Dokument definiert nicht:

- Kontostrukturen;
- Passwort- oder MFA-Regeln;
- konkrete Rollen;
- Berechtigungsauflösung;
- Organisationshierarchien;
- Sitzungsverwaltung;
- Delegationsalgorithmus;
- Prioritätsregeln für Allow/Deny;
- konkrete Datenschutzfristen.

## 21. Folgemodelle

Insbesondere folgen:

- `ACCOUNT_MODEL.md`;
- `AUTHENTICATION_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- `ROLE_MODEL.md`;
- `PERMISSION_MODEL.md`;
- `ORGANIZATION_MODEL.md`;
- `SESSION_MODEL.md`;
- `DELEGATION_MODEL.md`;
- `AUDIT_MODEL.md`.

## 22. Abhängigkeiten

- `PLATFORM_MODEL.md`
- `IDENTITY_MODEL.md`
- `PROJECT_MODEL.md`
- `WORKSPACE_MODEL.md`
- `RELATION_MODEL.md`
- `ADR-0002-identitaet-als-plattformkonzept.md`

## 23. Ergebnis

Der menschliche Benutzer ist als eigenständige fachliche Sicht auf eine Akteursidentität definiert. Benutzerkonten, Rollen, Berechtigungen und Authentifizierung bleiben getrennte Modelle; projektbezogene Verantwortungen wie Projektleitung, Stellvertretung, Vertrauensperson und Nachfolger sind ausdrücklich modellierbare Beziehungen.
