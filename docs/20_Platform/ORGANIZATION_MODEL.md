# Organisationsmodell

**Dokument-ID:** PLT-0014  
**Titel:** Fachliches Modell für Organisationen, Teams, Gruppen und Zugehörigkeiten  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert Organisationen, Organisationseinheiten, Teams, Gruppen und Zugehörigkeiten innerhalb von ProjectOS.

Organisationen bilden dauerhafte organisatorische Bezugsrahmen für Akteursidentitäten, Projekte, Verantwortlichkeiten, Rollen, Berechtigungen und Richtlinien.

Eine Organisationszugehörigkeit ist weder eine Identität noch eine Rolle noch eine Berechtigung noch eine Autorisierungsentscheidung.

## 2. Architekturstellung

Das Organisationsmodell gehört zur Plattformebene und baut insbesondere auf `PLATFORM_MODEL.md`, `IDENTITY_MODEL.md`, `USER_MODEL.md`, `PROJECT_MODEL.md`, `WORKSPACE_MODEL.md`, `AUTHORIZATION_MODEL.md`, `ROLE_MODEL.md`, `PERMISSION_MODEL.md`, `DELEGATION_MODEL.md` und `RELATION_MODEL.md` auf.

Organisationen, Teams, Gruppen und andere organisatorische Einheiten sind Plattformobjekte.

Zugehörigkeiten werden als typisierte Beziehungen mit eigenem Gültigkeitsbereich und Lebenszyklus modelliert.

Die Autorisierungsplattform entscheidet letztlich, welche Wirkung eine Organisationsbeziehung auf eine konkrete Handlung besitzt.

## 3. Grundsatz

Für organisatorische Zugehörigkeiten gilt:

```text
Akteursidentität
      ↓ gehört zu
Organisation / Einheit / Team / Gruppe
      ↓ kann Grundlage sein für
Rollen / Richtlinien / Verantwortungen
      ↓ werden ausgewertet durch
Autorisierung
```

Eine Zugehörigkeit erzeugt niemals allein automatisch ein `ALLOW`.

## 4. Organisationsobjekt

Eine Organisation ist ein dauerhaft identifizierbares Plattformobjekt.

Sie beschreibt einen organisatorischen Bezugsrahmen, in dem unter anderem folgende Elemente zusammengefasst werden können:

- Akteursidentitäten;
- Organisationseinheiten;
- Teams;
- Gruppen;
- Projekte;
- Verantwortungsbeziehungen;
- Rollen und Rollenzuweisungen;
- Richtlinien;
- Delegationen;
- Audit- und Nachweisbezüge.

Die Organisation besitzt keine eigene parallele Autorisierungslogik.

## 5. Organisationsidentität

Jede Organisation besitzt eine stabile Organisations-ID.

Die Organisations-ID:

- ist unabhängig von Anzeigename und Kurzbezeichnung;
- bleibt bei Umbenennung erhalten;
- wird nicht aus Domain, E-Mail-Adresse, Dateipfad oder Repository abgeleitet;
- wird nach endgültiger Stilllegung nicht für eine andere Organisation wiederverwendet;
- ist in Beziehungen, Projekten, Rollen, Berechtigungen, Audit und Z_Cockpit referenzierbar.

## 6. Organisationskern

Eine Organisation beschreibt mindestens:

- Organisations-ID;
- Namen und optionale Kurzbezeichnung;
- Zweck bzw. organisatorischen Kontext;
- Lebenszyklusstatus;
- optionale externe Referenzen;
- optionale übergeordnete organisatorische Beziehung;
- verantwortliche Akteursidentitäten oder Rollenreferenzen;
- Historien- und Auditbezüge;
- verwendete Schema- und Modellversion.

Personenbezogene Daten gehören nicht unnötig in den Organisationskern.

## 7. Organisationseinheiten

Eine Organisation kann untergeordnete Organisationseinheiten besitzen.

Beispiele sind:

- Bereich;
- Abteilung;
- Fachbereich;
- Standort;
- Geschäftseinheit;
- Projektorganisation;
- temporäre Arbeitsorganisation.

Eine Organisationseinheit besitzt eine eigene stabile Objektidentität, wenn sie dauerhaft referenzierbar, versionierbar oder historisierbar sein muss.

## 8. Teams

Ein Team ist eine organisatorische Einheit zur Zusammenarbeit in einem definierten fachlichen oder betrieblichen Kontext.

Ein Team kann:

- dauerhaft oder zeitlich begrenzt bestehen;
- einer Organisation oder Organisationseinheit zugeordnet sein;
- Projekte oder Domänen betreuen;
- Mitglieder besitzen;
- eigene Verantwortungsbeziehungen besitzen;
- Grundlage für Rollen- oder Berechtigungszuweisungen sein.

Teammitgliedschaft allein ist keine Berechtigung.

## 9. Gruppen

Eine Gruppe ist eine organisatorische Zusammenfassung von Akteursidentitäten für einen ausdrücklich definierten Zweck.

Gruppen können beispielsweise verwendet werden für:

- organisatorische Klassifikation;
- Kommunikationsbezug;
- Sichtbarkeitsregeln;
- Richtlinienzuordnung;
- Rollen- oder Berechtigungszuweisung;
- Review- oder Freigabekreise;
- technische Akteursgruppen.

Eine Gruppe darf nicht als versteckte Rolle verwendet werden, wenn tatsächlich eine fachliche Rolle gemeint ist.

## 10. Unterschied Team und Gruppe

Team und Gruppe sind nicht zwingend identisch.

Ein Team besitzt typischerweise eine fachliche Zusammenarbeit, Verantwortlichkeit oder Arbeitsorganisation.

Eine Gruppe kann dagegen lediglich eine administrative oder regelbezogene Zusammenfassung darstellen.

Die konkrete Bedeutung muss durch den jeweiligen Typ und das Schema eindeutig sein.

## 11. Zugehörigkeit

Eine Zugehörigkeit verbindet eine Akteursidentität mit einer Organisation, Organisationseinheit, einem Team oder einer Gruppe.

Sie beschreibt mindestens:

- eindeutige Zugehörigkeits-ID;
- Akteursidentität;
- Zielorganisation oder Zielorganisationseinheit;
- Zugehörigkeitsart;
- Beginn;
- optionales Ende;
- Status;
- Gültigkeitsbereich;
- ausstellende oder bestätigende Identität bzw. Instanz;
- Begründung oder Herkunft;
- Historien- und Auditbezug.

Zugehörigkeiten dürfen nicht als unveränderliche Benutzerattribute implementiert werden.

## 12. Zugehörigkeitsarten

Mindestens sollen konzeptionell unterscheidbar sein:

- Mitglied;
- externes Mitglied;
- Gast;
- Beobachter;
- Verantwortlicher;
- Leiter einer Organisationseinheit;
- Teammitglied;
- Gruppenmitglied;
- technisches Mitglied;
- temporäres Mitglied.

Die Zugehörigkeitsart selbst definiert keine vollständige Berechtigungswirkung.

## 13. Menschliche und technische Akteure

Organisationen können sowohl menschliche als auch technische Akteursidentitäten referenzieren.

Technische Akteure können beispielsweise sein:

- Dienste;
- Automatisierungen;
- API-Clients;
- Geräte;
- definierte Systemprozesse.

Eine technische Identität darf nicht künstlich als menschlicher Benutzer behandelt werden.

## 14. Mehrfachzugehörigkeit

Eine Akteursidentität kann gleichzeitig mehreren Organisationen, Teams oder Gruppen angehören.

Mehrfachzugehörigkeit muss eindeutig und konfliktfrei referenzierbar bleiben.

Eine Zugehörigkeit zu Organisation A darf keine Rechte in Organisation B erzeugen, sofern dies nicht durch eine ausdrücklich definierte organisationsübergreifende Regel vorgesehen ist.

## 15. Organisationshierarchie

Organisationen und Organisationseinheiten können hierarchisch strukturiert sein.

Hierarchien müssen:

- explizit modelliert;
- zyklusfrei;
- nachvollziehbar;
- versionierbar;
- auditierbar

sein.

Eine Hierarchie erzeugt keine automatische Berechtigungsvererbung.

## 16. Bereichsvererbung

Organisationsbeziehungen können als Grundlage für Bereichsvererbung dienen, wenn diese ausdrücklich definiert ist.

Beispiel:

```text
Organisation
  ↓
Bereich Engineering
  ↓
Team Elektro
```

Eine auf `Bereich Engineering` bezogene Rolle darf nur dann auf `Team Elektro` wirken, wenn die Rollen-, Berechtigungs- oder Autorisierungsregeln diese Vererbung ausdrücklich zulassen.

## 17. Organisation und Rollen

Organisation und Rolle sind getrennte Konzepte.

Eine Rollenzuweisung kann einen Organisationskontext besitzen.

Beispiele:

- Organisationsadministrator;
- Bereichsverantwortlicher;
- Teamleiter;
- Reviewer einer Organisationseinheit;
- Sicherheitsverantwortlicher.

Solche Rollen müssen über `ROLE_MODEL.md` definiert und der Akteursidentität ausdrücklich zugewiesen werden.

Eine Mitgliedschaft allein ersetzt keine Rollenzuweisung.

## 18. Organisation und Berechtigungen

Direkte Berechtigungen können organisationsbezogen zugewiesen werden.

Dabei gelten vollständig die Regeln aus `PERMISSION_MODEL.md` und `AUTHORIZATION_MODEL.md`.

Insbesondere bleiben getrennt:

- Zugehörigkeit;
- Rollenquelle;
- direkte `ALLOW`-Zuweisung;
- direkte `DENY`-Zuweisung;
- Whitelist- oder Blacklist-Regel;
- Ausnahmerecht;
- effektive Autorisierungsentscheidung.

## 19. Organisation und Projekte

Ein Projekt kann einer Organisation oder mehreren organisatorischen Bezugsrahmen zugeordnet sein.

Dabei müssen organisatorische Beziehung und Projektidentität getrennt bleiben.

Eine Organisation kann insbesondere zu Projekten Beziehungen besitzen wie:

- Eigentümerorganisation;
- verantwortliche Organisation;
- beteiligte Organisation;
- Auftraggeber;
- Partnerorganisation;
- externe Prüforganisation.

Die konkrete Berechtigungswirkung wird ausschließlich durch die Autorisierungsplattform bestimmt.

## 20. Projektmitgliedschaft und Organisationsmitgliedschaft

Projektmitgliedschaft und Organisationsmitgliedschaft sind getrennte Beziehungen.

Ein Benutzer kann:

- Mitglied einer Organisation, aber nicht eines bestimmten Projekts sein;
- Projektmitglied sein, ohne reguläres Organisationsmitglied zu sein;
- in mehreren Projekten unterschiedliche Rollen besitzen;
- in derselben Organisation verschiedenen Teams angehören.

Es darf keine implizite Gleichsetzung dieser Beziehungen geben.

## 21. Externe Mitglieder und Gäste

Externe Mitglieder und Gäste müssen ausdrücklich als solche erkennbar sein.

Für sie können strengere Richtlinien gelten, beispielsweise:

- begrenzte Gültigkeitsdauer;
- beschränkte Projekte oder Domänen;
- reduzierte Rollenmenge;
- zusätzlicher Authentifizierungsgrad;
- eingeschränkte Offline-Nutzung;
- zusätzliche Auditpflicht;
- besondere Freigabe für sensible Daten.

Die konkrete Wirkung wird durch Autorisierungs- und Richtlinienregeln bestimmt.

## 22. Verantwortliche und Leitung

Organisationen und Organisationseinheiten können fachliche Verantwortungsbeziehungen zu Akteursidentitäten besitzen.

Beispiele sind:

- Organisationsleitung;
- Bereichsleitung;
- Teamleitung;
- fachlich Verantwortlicher;
- Sicherheitsverantwortlicher;
- Freigabeverantwortlicher;
- Eskalationsverantwortlicher.

Verantwortung und Berechtigung bleiben getrennt.

Eine Leitungsbeziehung ist keine universelle Administratorberechtigung.

## 23. Stellvertretung

Organisatorische Verantwortungen können über das `DELEGATION_MODEL.md` kontrolliert vertreten werden.

Eine Stellvertretung muss mindestens weiterhin erkennen lassen:

- originär verantwortliche Identität;
- ausführende Identität;
- vertretene organisatorische Verantwortung;
- Gültigkeitsbereich;
- Beginn und Ende;
- übertragene Befugnisse;
- Ausschlüsse;
- Freigaben.

Organisationen dürfen hierfür keine eigene parallele Delegationslogik einführen.

## 24. Nachfolge

Eine organisatorische Nachfolge kann eine zukünftige Verantwortungsübernahme vorbereiten.

Vor Aktivierung entstehen keine produktiven Rechte allein durch die Nachfolgerbeziehung.

Bei Aktivierung müssen erforderliche Rollen-, Berechtigungs-, Delegations- und Verantwortungsänderungen explizit durchgeführt und auditiert werden.

## 25. Organisationsübergreifende Zusammenarbeit

ProjectOS muss Zusammenarbeit zwischen mehreren Organisationen unterstützen können.

Dabei können beispielsweise bestehen:

- gemeinsame Projekte;
- definierte Partnerbeziehungen;
- externe Review- oder Freigabebeziehungen;
- gemeinsam genutzte technische Dienste;
- begrenzte organisationsübergreifende Rollen.

Organisationsgrenzen dürfen durch Zusammenarbeit nicht stillschweigend aufgehoben werden.

## 26. Föderierte oder externe Organisationen

Eine Organisation kann durch externe Systeme oder Identitätsquellen referenziert werden.

Externe Organisationskennungen ersetzen nicht die interne stabile Organisations-ID.

Es muss unterscheidbar bleiben zwischen:

- interner Organisationsidentität;
- externer Quelle;
- externer Kennung;
- lokal bestätigtem Stand;
- Synchronisationsstatus.

## 27. Lebenszyklus

Eine Organisation bzw. Organisationseinheit besitzt einen kontrollierten Lebenszyklus.

Konzeptionell werden mindestens unterschieden:

- angelegt;
- aktiv;
- eingeschränkt;
- pausiert;
- stillgelegt;
- archiviert.

Eine Zugehörigkeit besitzt mindestens:

- vorbereitet;
- aktiv;
- pausiert;
- beendet;
- widerrufen;
- abgelaufen;
- archiviert.

Nur aktive und gültige Zugehörigkeiten dürfen für neue Autorisierungsentscheidungen berücksichtigt werden.

## 28. Ausscheiden und Stilllegung

Das Ausscheiden eines Benutzers oder die Stilllegung einer Organisation darf historische Verantwortungs-, Projekt- und Auditbezüge nicht zerstören.

Neue produktive Wirkungen müssen jedoch entsprechend dem aktuellen Lebenszyklus verhindert werden.

Abhängige Rollen, Delegationen, Sitzungen und Berechtigungszuweisungen müssen neu bewertet werden können.

## 29. Zeitliche Zugehörigkeit

Zugehörigkeiten können zeitlich begrenzt sein.

Dies ist insbesondere vorgesehen für:

- externe Mitarbeit;
- Projektphasen;
- Praktika oder temporäre Aufgaben;
- befristete Teams;
- Wartungs- oder Übergangsphasen;
- temporäre technische Identitäten.

Abgelaufene Zugehörigkeiten dürfen keine neuen wirksamen Rechte erzeugen.

## 30. Organisationsrichtlinien

Organisationen können Referenz- oder Gültigkeitsbereich für Richtlinien sein.

Beispiele sind:

- Authentifizierungsanforderungen;
- Offline-Zulässigkeit;
- Sichtbarkeitsregeln;
- Freigabeanforderungen;
- Vier-Augen-Regeln;
- maximale Delegationsdauer;
- zulässige externe Mitglieder;
- Sicherheits- oder Compliance-Vorgaben.

Richtlinien müssen über die zuständigen Plattformmodelle ausgewertet werden und dürfen nicht als versteckte Organisationsflags die Autorisierung umgehen.

## 31. Vier-Augen-Prinzip und Trennung von Aufgaben

Organisations- und Teamgrenzen können Teil von Unabhängigkeitsregeln sein.

Das Vier-Augen-Prinzip bleibt jedoch auf tatsächlich unabhängige Akteursidentitäten bezogen.

Zwei Konten derselben Identität oder zwei organisatorische Mitgliedschaften derselben Identität stellen keine zwei unabhängigen Personen dar.

Unvereinbare Rollen oder Berechtigungen bleiben auch innerhalb derselben Organisation unvereinbar.

## 32. Offline-First

Organisationsbeziehungen können offline ausgewertet werden, wenn der notwendige bestätigte Organisations- und Autorisierungsstand lokal verfügbar ist.

Es muss erkennbar sein:

- auf welchem Snapshot die Organisationsdaten beruhen;
- wann dieser zuletzt bestätigt wurde;
- welche Zugehörigkeiten möglicherweise veraltet sind;
- welche externen Informationen fehlen;
- ob dadurch eine Autorisierungsentscheidung eingeschränkt oder `INDETERMINATE` wird.

Kritische organisatorische Änderungen können eine Online-Bestätigung verlangen.

## 33. Synchronisation

Synchronisation von Organisationsdaten ist ein kontrollierter Vorgang.

Konflikte dürfen nicht stillschweigend überschrieben werden.

Insbesondere sind Konflikte sichtbar zu behandeln bei:

- geänderten Zugehörigkeiten;
- abgelaufenen externen Mitgliedschaften;
- geänderter Organisationshierarchie;
- widerrufenen Verantwortungsbeziehungen;
- geänderten Rollen- oder Delegationsbezügen;
- stillgelegten Identitäten oder Organisationseinheiten.

## 34. Z_Cockpit

`Z_Cockpit` soll Organisationen und Zugehörigkeiten transparent darstellen und bei entsprechender Autorisierung deren Verwaltung auslösen können.

Mindestens sichtbar sein sollen:

- Organisations-ID und Name;
- Organisationseinheiten;
- Teams und Gruppen;
- Mitglieder und Zugehörigkeitsarten;
- Beginn und Ende von Zugehörigkeiten;
- Status;
- Verantwortliche;
- projektbezogene Beziehungen;
- organisationsbezogene Rollen;
- Delegationen und Stellvertretungen;
- relevante Richtlinien;
- Auditinformationen;
- Offline- bzw. Synchronisationsstand.

Die UI darf Organisationsmitgliedschaft nicht als automatisch identische effektive Berechtigung darstellen.

## 35. Organisations-Read-Model

Für Cockpit, Reporting und Analyse darf ein nicht-autoritatives Organisations-Read-Model aufgebaut werden.

Es kann insbesondere darstellen:

- Organisationsbaum;
- aktive Mitglieder;
- Team- und Gruppenzuordnungen;
- Verantwortliche;
- Rollen je Organisationseinheit;
- ablaufende Zugehörigkeiten;
- externe Mitglieder;
- verwaiste Organisationseinheiten;
- Konflikte und Warnungen.

Produktive Autorisierungsentscheidungen dürfen nicht allein aus diesem Read-Model erfolgen.

## 36. Rechtesimulation

Organisationsänderungen müssen in der Z_Cockpit-Rechtesimulation berücksichtigt werden können.

Vor Aktivierung oder Änderung soll insbesondere prüfbar sein:

- welche effektiven Rechte durch eine neue Zugehörigkeit entstehen;
- welche Rechte beim Entfernen einer Zugehörigkeit entfallen;
- welche Rollen durch Organisationsbeziehungen wirksam oder unwirksam werden;
- welche Delegationen betroffen sind;
- welche Projekte betroffen sind;
- welche `DENY`-, Whitelist- oder Blacklist-Regeln relevant werden;
- welche Vier-Augen- oder Unvereinbarkeitsregeln verletzt werden;
- ob Konten oder Sitzungen neu bewertet werden müssen.

Die Simulation verwendet dieselben fachlichen Regeln wie die Autorisierungsplattform und besitzt keine produktive Wirkung.

## 37. Suche

Organisationen, Organisationseinheiten, Teams, Gruppen und Zugehörigkeiten sollen – innerhalb der zulässigen Sichtbarkeitsgrenzen – auffindbar sein.

Suchkriterien können insbesondere sein:

- Organisations-ID;
- Name;
- Typ;
- Mitglied;
- Verantwortlicher;
- Projektbezug;
- Rolle;
- Lebenszyklusstatus;
- externe Referenz;
- Gültigkeitszeitraum.

Suche muss Berechtigungs- und Datenschutzgrenzen beachten.

## 38. Audit

Mindestens folgende Vorgänge müssen auditierbar sein:

- Organisation angelegt oder geändert;
- Organisationseinheit angelegt, verschoben oder stillgelegt;
- Team oder Gruppe angelegt oder geändert;
- Zugehörigkeit angelegt;
- Zugehörigkeit aktiviert, pausiert, beendet oder widerrufen;
- Gültigkeitsdauer geändert;
- externe Mitgliedschaft angelegt oder verlängert;
- Verantwortlicher geändert;
- Organisationshierarchie geändert;
- organisationsbezogene Rolle zugewiesen oder entzogen;
- organisationsbezogene Richtlinie geändert;
- organisationsbezogene Delegation aktiviert oder widerrufen.

Audit muss die tatsächlich handelnde Akteursidentität nachvollziehbar halten.

## 39. Datenschutz

Organisationsdaten können personenbezogene oder vertrauliche Informationen enthalten.

Daher gelten mindestens:

- Datenminimierung;
- berechtigungsabhängige Sichtbarkeit;
- Trennung von Profil- und Organisationsdaten;
- Erhalt notwendiger historischer Referenzen;
- kontrollierte Anonymisierung oder Einschränkung personenbezogener Attribute;
- keine Offenlegung von Geheimnissen über Organisationsansichten.

Konkrete Aufbewahrungsfristen werden nicht in diesem Dokument festgelegt.

## 40. Validierung

Eine Organisation ist mindestens darauf zu prüfen, dass:

1. eine eindeutige Organisations-ID vorhanden ist;
2. Name und Lebenszyklusstatus gültig sind;
3. Hierarchiebeziehungen keine Zyklen erzeugen;
4. referenzierte Organisationseinheiten existieren;
5. verantwortliche Akteursidentitäten gültig sind;
6. externe Referenzen eindeutig ihrer Quelle zugeordnet sind;
7. stillgelegte Einheiten keine unkontrollierten neuen produktiven Wirkungen erzeugen;
8. sicherheitsrelevante Änderungen auditierbar sind.

Eine Zugehörigkeit ist mindestens darauf zu prüfen, dass:

1. Zugehörigkeits-ID eindeutig ist;
2. Akteursidentität existiert;
3. Zielorganisation oder Zielorganisationseinheit existiert;
4. Zugehörigkeitsart bekannt ist;
5. Beginn und Ende konsistent sind;
6. Status und Lebenszyklus zulässig sind;
7. die ausstellende oder bestätigende Instanz autorisiert war;
8. Gültigkeitsbereich zulässig ist;
9. organisationsübergreifende Beziehungen ausdrücklich erlaubt sind;
10. sicherheitsrelevante Auswirkungen neu bewertet werden können.

## 41. Invarianten

1. Organisation und Akteursidentität sind getrennte Konzepte.
2. Organisation und Projekt sind getrennte Konzepte.
3. Organisation und Workspace sind getrennte Konzepte.
4. Mitgliedschaft ist keine Rolle.
5. Mitgliedschaft ist keine Berechtigung.
6. Mitgliedschaft garantiert kein `ALLOW`.
7. Rollen- und Berechtigungswirkung wird ausschließlich durch die Autorisierungsplattform entschieden.
8. Organisationshierarchie erzeugt keine implizite Berechtigungsvererbung.
9. Projektmitgliedschaft und Organisationsmitgliedschaft sind getrennte Beziehungen.
10. Menschliche und technische Akteursidentitäten bleiben unterscheidbar.
11. Organisationsübergreifende Zusammenarbeit hebt Organisationsgrenzen nicht stillschweigend auf.
12. Stilllegung zerstört keine erforderlichen historischen Referenzen.
13. Stellvertretung und Delegation verwenden das kanonische Delegationsmodell.
14. Z_Cockpit ist nicht die Source of Truth für Organisations- oder Berechtigungsdaten.
15. Organisations-Read-Models besitzen keine produktive Autorisierungswirkung.
16. Rechtesimulation verändert keine produktiven Organisations- oder Autorisierungsdaten.

## 42. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- konkrete Unternehmensorganigramme;
- konkrete Benutzerlisten;
- vollständige Rollenlisten;
- vollständige Berechtigungskataloge;
- technische Directory- oder LDAP-Strukturen;
- konkrete externe Identity Provider;
- konkrete Datenbanktabellen;
- technische Synchronisationsprotokolle;
- konkrete GUI-Layouts;
- vollständige Workflow-Engine;
- konkrete Datenschutzfristen.

## 43. Folgemodelle

Auf diesem Modell bauen insbesondere auf:

- `AUDIT_MODEL.md`;
- spätere Organisationsdienste;
- Identitäts- und Autorisierungsdienste;
- Z_Cockpit-Organisations-Read-Models;
- organisationsbezogene Rechtesimulation;
- Richtlinien- und Freigabeworkflows.

## 44. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `PLATFORM_MODEL.md`;
- `PROJECT_MODEL.md`;
- `WORKSPACE_MODEL.md`;
- `IDENTITY_MODEL.md`;
- `USER_MODEL.md`;
- `ACCOUNT_MODEL.md`;
- `AUTHENTICATION_MODEL.md`;
- `SESSION_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- `ROLE_MODEL.md`;
- `PERMISSION_MODEL.md`;
- `DELEGATION_MODEL.md`;
- `RELATION_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`;
- `Z_COCKPIT_AUTHORIZATION_SIMULATION.md`.

## 45. Ergebnis

ProjectOS besitzt ein eigenständiges Organisationsmodell für Organisationen, Organisationseinheiten, Teams, Gruppen und Zugehörigkeiten.

Organisatorische Mitgliedschaft, Verantwortlichkeit, Rolle, Berechtigung und Autorisierungsentscheidung bleiben konsequent getrennt. Organisationsbeziehungen können als nachvollziehbare Eingaben für Rollen, Richtlinien, Delegation und Autorisierung dienen, ohne selbst eine parallele Berechtigungslogik zu bilden.

Hierarchien, Mehrfachzugehörigkeiten, externe Mitglieder, technische Akteure, zeitliche Gültigkeit, Offline-Betrieb, Audit und Z_Cockpit-Rechtesimulation sind ausdrücklich berücksichtigt.