# Rollenmodell

**Dokument-ID:** PLT-0011  
**Titel:** Fachliches Modell von Rollen  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert Rollen als fachliche Bündel von Verantwortungen und Berechtigungen innerhalb von ProjectOS.

Eine Rolle beschreibt, in welcher Funktion ein Akteur in einem bestimmten Gültigkeitsbereich handelt. Sie ist weder die Identität selbst noch eine einzelne Berechtigung noch eine Organisationszugehörigkeit.

## 2. Architekturstellung

Das Rollenmodell gehört zur Plattformebene und baut insbesondere auf `IDENTITY_MODEL.md`, `PROJECT_MODEL.md`, `ORGANIZATION_MODEL.md` (später), `AUTHORIZATION_MODEL.md` und `RELATION_MODEL.md` auf.

Die Autorisierungsplattform wertet Rollen zusammen mit direkten Berechtigungen, Verweigerungen, Delegationen, Richtlinien und Sitzungskontext aus.

## 3. Grundsatz

Für Rollen gilt:

```text
Identität
    ↓ erhält im Gültigkeitsbereich
Rolle
    ↓ bündelt
Berechtigungen
    ↓ werden durch
Autorisierung
    ↓ kontextbezogen ausgewertet
```

Eine Rolle allein garantiert keine erfolgreiche Autorisierungsentscheidung.

## 4. Rollenidentität

Jede definierte Rolle besitzt eine stabile Rollen-ID.

Die Rollen-ID:

- ist unabhängig von Anzeigename und Übersetzung;
- bleibt bei Umbenennung erhalten;
- wird nicht für fachlich andere Rollen wiederverwendet;
- darf nicht aus einer Benutzer-ID oder Projekt-ID abgeleitet werden.

## 5. Rollendefinition und Rollenzuweisung

Rollendefinition und Rollenzuweisung sind getrennt.

Eine **Rollendefinition** beschreibt, was eine Rolle fachlich bedeutet und welche Berechtigungen sie grundsätzlich bündeln kann.

Eine **Rollenzuweisung** verbindet eine Akteursidentität mit einer Rolle innerhalb eines konkreten Gültigkeitsbereichs und einer zeitlichen Gültigkeit.

Damit darf dieselbe Rolle mehreren Akteuren und dieselbe Identität mehreren Rollen zugewiesen werden.

## 6. Rollendefinition

Eine Rollendefinition beschreibt mindestens:

- stabile Rollen-ID;
- fachlichen Namen;
- Beschreibung und Zweck;
- Rollenkategorie;
- zulässige Gültigkeitsbereiche;
- referenzierte Berechtigungen;
- optionale Voraussetzungen;
- optionale Unvereinbarkeitsregeln;
- Lebenszyklusstatus;
- Version;
- Historien- und Auditbezüge.

## 7. Rollenzuweisung

Eine Rollenzuweisung beschreibt mindestens:

- eindeutige Zuweisungs-ID;
- Akteursidentität;
- Rollen-ID;
- Gültigkeitsbereich;
- Zielreferenz des Bereichs, beispielsweise Projekt oder Organisation;
- Beginn;
- optionales Ende;
- Status;
- zuweisende bzw. freigebende Identität;
- Begründung oder Referenz auf den auslösenden Vorgang;
- Auditbezug.

## 8. Gültigkeitsbereiche

Rollen müssen bereichsbezogen vergeben werden können.

Mindestens vorgesehen sind:

- global;
- Organisation;
- Projekt;
- Workspace, sofern fachlich erforderlich;
- Domäne;
- Objektgruppe;
- einzelnes Objekt, wenn ausdrücklich zulässig.

Eine projektbezogene Rolle darf nicht automatisch global wirken.

## 9. Rollenkategorien

Die Plattform soll fachlich mindestens folgende Kategorien unterscheiden können:

- Verantwortungsrolle;
- Arbeitsrolle;
- Reviewrolle;
- Freigaberolle;
- administrative Rolle;
- Sicherheitsrolle;
- technische Rolle.

Die Kategorie dient der Strukturierung und ersetzt keine Berechtigungsprüfung.

## 10. Projektleiter

`Projektleiter` ist eine projektbezogene Verantwortungsrolle bzw. Verantwortungsbeziehung.

Sie kann ein definiertes Bündel projektbezogener Berechtigungen besitzen, ist aber keine globale Administratorrolle.

Die Rollendefinition muss klar festlegen, welche Projektoperationen umfasst sind und welche besonders kritischen Operationen zusätzliche Freigaben benötigen.

## 11. Stellvertretung

`Stellvertretung` wird nicht als normale dauerhafte Rollenidentität modelliert, wenn sie eine konkrete Person für einen anderen Verantwortlichen vertritt.

Stattdessen wird die zugrunde liegende Verantwortungsrolle mit einer kontrollierten Stellvertretungs- bzw. Delegationsbeziehung kombiniert.

So bleibt sichtbar:

- welche Rolle vertreten wird;
- wer originär verantwortlich ist;
- wer tatsächlich handelt;
- in welchem Zeitraum und Umfang die Vertretung gilt.

## 12. Vertrauensperson

`Vertrauensperson` ist zunächst eine fachliche Vertrauens- bzw. Sicherheitsbeziehung und nicht automatisch eine Rolle mit Administrationsrechten.

Falls definierte Aufgaben bestehen, können dafür eigene begrenzte Rollen oder Berechtigungen vorgesehen werden, beispielsweise Beteiligung an Wiederherstellungs- oder Eskalationsprozessen.

## 13. Nachfolger

`Nachfolger` ist grundsätzlich keine aktive Rolle vor Eintritt der Nachfolgebedingung.

Nach Aktivierung kann eine definierte Verantwortungsrolle übernommen oder neu zugewiesen werden.

Der Übergang muss nachvollziehbar und auditierbar sein.

## 14. Reviewer

Eine Reviewer-Rolle beschreibt die fachliche Befugnis, definierte Artefakte oder Vorgänge zu prüfen.

Review und Freigabe sind getrennt zu behandeln.

Ein Reviewer darf nicht allein aufgrund dieser Rolle automatisch final freigeben, sofern dafür eine eigene Freigaberolle vorgesehen ist.

## 15. Freigabeverantwortlicher

Eine Freigaberolle umfasst ausdrücklich definierte Freigabehandlungen.

Für kritische Freigaben können zusätzliche Anforderungen gelten, beispielsweise:

- Vier-Augen-Prinzip;
- Mindest-Authentifizierungsgrad;
- Unvereinbarkeit mit dem Ersteller;
- projektspezifischer oder domänenspezifischer Gültigkeitsbereich.

## 16. Fachlich Verantwortlicher

Eine fachliche Verantwortungsrolle beschreibt Zuständigkeit für einen definierten Sachbereich.

Dies kann beispielsweise eine Domäne, Objektgruppe, Bibliothek, Konfiguration oder Dokumentationsklasse sein.

Verantwortung und technische Administrationsrechte sind getrennt.

## 17. Administrative Rollen

Administrative Rollen sind besonders sensibel und müssen eng begrenzt werden.

Es sollen keine unnötigen universellen Superuser-Rollen entstehen.

Administrative Rollen müssen:

- einen klaren Gültigkeitsbereich besitzen;
- ein minimales notwendiges Berechtigungsbündel verwenden;
- besonders auditierbar sein;
- gegebenenfalls höheren Authentifizierungsgrad erfordern;
- kontrolliert zuweisbar und widerrufbar sein.

## 18. Technische Rollen

Technische Identitäten können eigene Rollen erhalten, beispielsweise für Dienste, Automatisierungen oder API-Clients.

Technische Rollen dürfen nicht allein deshalb mit menschlichen Administratorrollen gleichgesetzt werden.

Sie sollen möglichst zweckgebunden und minimal privilegiert sein.

## 19. Rollen und direkte Berechtigungen

Rollen bündeln reguläre Berechtigungen.

Direkte Berechtigungen können ergänzend verwendet werden, wenn eine individuelle Abweichung fachlich erforderlich ist.

Ein wachsender Bestand direkter Sonderrechte ist jedoch ein Hinweis darauf, dass Rollen oder Berechtigungsschnitt fachlich überprüft werden sollten.

## 20. Rollen und Verweigerungen

Eine Rollenberechtigung kann durch eine einschlägige ausdrückliche Verweigerung oder Blacklist-Regel eingeschränkt werden.

Die Rollenzuweisung selbst ist daher kein Beweis für die effektive Berechtigung.

## 21. Rollen und Ausnahmerechte

Ausnahmerechte sollen nicht durch künstliche Einmal-Rollen ersetzt werden, wenn es sich tatsächlich um eine begrenzte Ausnahme handelt.

Rollen dienen stabilen fachlichen Funktionen. Ausnahmen dienen kontrollierten Abweichungen.

## 22. Rollenhierarchie

Rollenhierarchien können zulässig sein, müssen jedoch ausdrücklich modelliert und begrenzt werden.

Eine Rolle darf Berechtigungen einer anderen Rolle nur dann erben, wenn diese Beziehung klar definiert, zyklusfrei und nachvollziehbar ist.

Tiefe oder schwer nachvollziehbare Rollenvererbung soll vermieden werden.

## 23. Zusammengesetzte Rollen

Eine Rolle kann fachlich aus mehreren kleineren Rollen oder Berechtigungsgruppen zusammengesetzt werden.

Die resultierenden effektiven Berechtigungen müssen weiterhin erklärbar bleiben.

Das Z_Cockpit muss bei zusammengesetzten Rollen die Herkunft einer Berechtigung darstellen können.

## 24. Unvereinbare Rollen

ProjectOS muss Rollenkombinationen als unvereinbar definieren können.

Beispiele können sein:

- Ersteller und unabhängiger Freigeber desselben kritischen Vorgangs;
- Antragsteller und alleiniger Genehmiger;
- bestimmte Sicherheits- und Prüfrollen.

Unvereinbarkeiten können je Gültigkeitsbereich unterschiedlich sein.

## 25. Vier-Augen-Prinzip

Das Vier-Augen-Prinzip wird nicht allein über Rollennamen erreicht.

Es erfordert eine Prüfung der tatsächlich handelnden Identitäten und des konkreten Vorgangs.

Zwei verschiedene Konten derselben Akteursidentität erfüllen kein unabhängiges Vier-Augen-Prinzip.

## 26. Zeitliche Rollen

Rollenzuweisungen können zeitlich begrenzt sein.

Zeitliche Rollen eignen sich beispielsweise für:

- Projektphasen;
- externe Mitarbeit;
- temporäre Vertretungen;
- Wartungsfenster;
- befristete Review- oder Freigabeaufgaben.

Abgelaufene Zuweisungen dürfen keine wirksamen Berechtigungen mehr erzeugen.

## 27. Aktivierung und Deaktivierung

Eine Rollenzuweisung kann vorbereitet, aktiv, pausiert, widerrufen, abgelaufen oder archiviert sein.

Die genaue Zustandsmaschine wird im Rollenschema festgelegt.

Pausierte, widerrufene oder abgelaufene Zuweisungen sind für neue Autorisierungsentscheidungen unwirksam.

## 28. Rollenänderungen

Änderungen an einer Rollendefinition können viele Akteure gleichzeitig betreffen und sind deshalb sicherheitsrelevant.

Eine Änderung muss versioniert, validiert und auditiert werden.

Bei kritischen Rollen soll vor Aktivierung einer geänderten Version eine Auswirkungsanalyse möglich sein.

## 29. Rollenversionierung

Rollendefinitionen sind versionierbar.

Es muss unterscheidbar sein, ob eine bestehende Rollenzuweisung:

- automatisch der aktuellen kompatiblen Rollenversion folgt;
- an eine konkrete Version gebunden ist;
- vor einer Migration überprüft werden muss.

Die Migrationsstrategie wird später im Dienst- und Implementierungsmodell festgelegt.

## 30. Offline-First

Für Offline-Autorisierung müssen die im vorgesehenen lokalen Betriebsumfang benötigten Rollendefinitionen und aktiven Zuweisungen verfügbar sein.

Es muss erkennbar sein, auf welchem Stand eine lokale Rollenauswertung beruht.

Kritische Rollenänderungen können Richtlinien unterliegen, die eine Online-Bestätigung verlangen.

## 31. Z_Cockpit

`Z_Cockpit` soll Rollen transparent darstellen und – bei entsprechender Autorisierung – deren Verwaltung auslösen können.

Mindestens sollen sichtbar sein:

- Rollenname und Rollen-ID;
- Kategorie;
- Gültigkeitsbereich;
- zugeordnete Berechtigungen;
- zugewiesene Akteure;
- Beginn und Ende einer Zuweisung;
- Status;
- Herkunft bzw. zuweisende Instanz;
- Unvereinbarkeiten;
- Delegations- oder Stellvertretungsbezug;
- relevante Auditinformationen.

Für einen Benutzer soll das Cockpit zwischen **zugewiesener Rolle** und **effektivem Recht** unterscheiden.

## 32. Rollen-Read-Model

Für Cockpit und Reporting darf ein nicht-autoritatives Read-Model aufgebaut werden, das beispielsweise zeigt:

- Rollen einer Identität nach Projekt oder Organisation;
- resultierende Berechtigungen;
- geerbte oder zusammengesetzte Rollen;
- Konflikte und Unvereinbarkeiten;
- ablaufende Zuweisungen;
- ungenutzte oder verwaiste Rollen.

Sicherheitskritische Operationen dürfen nicht allein auf diesem Read-Model autorisiert werden.

## 33. Audit

Mindestens folgende Vorgänge sind auditierbar:

- Rollendefinition angelegt oder geändert;
- Berechtigungsbündel einer Rolle geändert;
- Rollenzuweisung angelegt;
- Zuweisung aktiviert, pausiert oder widerrufen;
- zeitliche Gültigkeit geändert;
- Unvereinbarkeitsregel geändert;
- administrative Rolle vergeben oder entzogen.

## 34. Validierung

Eine Rollendefinition ist mindestens darauf zu prüfen, dass:

1. die Rollen-ID eindeutig ist;
2. Name und Zweck definiert sind;
3. alle referenzierten Berechtigungen existieren;
4. Gültigkeitsbereiche zulässig sind;
5. Rollenhierarchien zyklusfrei sind;
6. Unvereinbarkeitsregeln auf gültige Rollen referenzieren;
7. administrative Rollen nicht unbegrenzt wirken, sofern dies nicht ausdrücklich genehmigt ist.

Eine Rollenzuweisung ist mindestens darauf zu prüfen, dass:

1. Identität und Rolle existieren;
2. der Gültigkeitsbereich zur Rolle passt;
3. Beginn und Ende konsistent sind;
4. die zuweisende Instanz autorisiert war;
5. Unvereinbarkeitsregeln eingehalten oder ausdrücklich behandelt wurden.

## 35. Invarianten

1. Rolle und Identität sind getrennt.
2. Rolle und Berechtigung sind getrennt.
3. Rollendefinition und Rollenzuweisung sind getrennt.
4. Eine Rolle wirkt nur in ihrem gültigen Bereich.
5. Eine Rolle garantiert allein kein `ALLOW`.
6. Projektleiter ist keine globale Superuser-Rolle.
7. Stellvertretung wird nicht durch Identitätsverschmelzung modelliert.
8. Vertrauensperson erhält nicht automatisch Administrationsrechte.
9. Nachfolger erhält Rechte erst nach definierter Aktivierung.
10. Reviewer und Freigabeverantwortlicher können getrennte Rollen sein.
11. Zwei Konten derselben Identität erfüllen kein unabhängiges Vier-Augen-Prinzip.
12. Z_Cockpit ist nicht die Source of Truth für Rollen oder effektive Rechte.

## 36. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- den vollständigen Berechtigungskatalog;
- konkrete Benutzerlisten;
- technische Policy-Engine;
- GUI-Layout;
- Organisationshierarchien im Detail;
- vollständige Delegationssemantik;
- technische Datenbankstrukturen.

## 37. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `PLATFORM_MODEL.md`;
- `IDENTITY_MODEL.md`;
- `USER_MODEL.md`;
- `PROJECT_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- `RELATION_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`.

## 38. Ergebnis

ProjectOS besitzt ein fachliches Rollenmodell, das stabile Rollendefinitionen von konkreten Rollenzuweisungen trennt und Rollen konsequent an Gültigkeitsbereiche bindet.

Projektleitung, Review, Freigabe, fachliche Verantwortung, Administration und technische Funktionen können damit nachvollziehbar modelliert werden, ohne Rolle, Identität und effektive Berechtigung miteinander zu vermischen.
