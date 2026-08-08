# Kontomodell

**Dokument-ID:** PLT-0006  
**Titel:** Fachliches Modell eines Zugangskontos  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert das Konto als eigenständige Zugangseinheit der Plattform.

Ein Konto beschreibt, über welchen verwalteten Zugang eine Akteursidentität einen Authentifizierungsprozess beginnen und einen Nutzungskontext erhalten kann.

Ein Konto ist weder die Identität selbst noch ein Benutzerprofil, eine Rolle, eine Berechtigung oder eine Sitzung.

## 2. Architekturstellung

Das Kontomodell gehört zur Plattformebene und baut auf `IDENTITY_MODEL.md` auf.

Die Identität beschreibt den Akteur. Das Konto beschreibt einen Zugang zu diesem Akteur oder für diesen Akteur.

Authentifizierungsverfahren, Autorisierungsentscheidungen und Sitzungsverwaltung werden getrennt modelliert.

## 3. Grundsatz

Für die Plattform gilt:

```text
Akteursidentität
    ↓ kann besitzen oder verwenden
Konto
    ↓ verwendet
Authentifizierungsverfahren
    ↓ erzeugt bei Erfolg
Sitzung
    ↓ wird bewertet durch
Autorisierung
```

Diese Ebenen dürfen nicht stillschweigend zusammengeführt werden.

## 4. Kontoidentität

Jedes Konto besitzt eine eigene stabile Konto-ID.

Die Konto-ID:

- ist nicht identisch mit der Akteursidentitäts-ID;
- ist nicht identisch mit Benutzername oder E-Mail-Adresse;
- bleibt bei Änderung des Anmeldenamens erhalten;
- wird nach endgültiger Stilllegung nicht für ein anderes Konto wiederverwendet;
- ist unabhängig von einem konkreten Authentifizierungsverfahren.

## 5. Beziehung zur Akteursidentität

Ein Konto verweist auf genau eine primär zugeordnete Akteursidentität, sofern nicht ein spezielles Systemkonto-Modell ausdrücklich etwas anderes definiert.

Eine Akteursidentität kann:

- kein aktives Konto besitzen;
- genau ein Konto besitzen;
- mehrere Konten besitzen.

Mehrere Konten derselben Identität dürfen nicht dazu führen, dass im Audit mehrere scheinbar unabhängige Personen entstehen.

## 6. Kontoarten

Die Plattform muss mindestens unterscheiden können zwischen:

- persönlichem Benutzerkonto;
- technischem Dienstkonto;
- Geräte- oder Maschinenkonto, sofern erforderlich;
- API-Zugangskonto;
- Automatisierungskonto;
- extern angebundenem Konto;
- lokalem Offline-Konto.

Nicht jede Akteursidentitätsart benötigt zwingend ein Konto.

## 7. Kontokern

Ein Konto beschreibt mindestens:

- stabile Konto-ID;
- zugeordnete Akteursidentität;
- Kontoart;
- Anmeldename oder andere adressierbare Kennung, sofern erforderlich;
- Lebenszyklusstatus;
- Authentifizierungsquellen bzw. registrierte Authentifizierungswege;
- Zeit- und Gültigkeitsinformationen;
- Sperr- und Einschränkungsstatus;
- Historien- und Auditbezüge;
- optionale Richtlinienreferenzen.

Geheimnisse werden nicht als gewöhnliche Kontoeigenschaften behandelt.

## 8. Anmeldename

Ein Anmeldename ist eine veränderbare Kontokennung und keine stabile Identität.

Er kann beispielsweise sein:

- Benutzername;
- E-Mail-Adresse;
- technische Client-Kennung;
- lokale Kontobezeichnung;
- externe Provider-Kennung.

Änderungen des Anmeldenamens verändern weder Konto-ID noch Akteursidentität.

## 9. Geheimnisse und Zugangsnachweise

Kennwörter, private Schlüssel, Tokens, Zertifikatsgeheimnisse oder vergleichbare Zugangsnachweise gehören nicht als Klartext in das Kontomodell.

Das Kontomodell darf nur kontrollierte Referenzen, Metadaten oder Statusinformationen zu Authentifizierungsnachweisen führen.

Die konkrete sichere Speicherung wird im Authentifizierungs- und Implementierungsmodell festgelegt.

## 10. Konto und Authentifizierung

Ein Konto kann null, ein oder mehrere registrierte Authentifizierungsverfahren besitzen.

Beispiele:

- lokales Kennwort;
- Passkey;
- Hardware-Token;
- Zertifikat;
- externer Identity Provider;
- gerätegebundener Nachweis;
- API-Schlüssel oder Client-Credential-Verfahren.

Das Konto definiert nicht selbst, ob ein konkreter Authentifizierungsversuch erfolgreich ist.

## 11. Mehrfaktor-Authentifizierung

Ein Konto kann Richtlinien verlangen, nach denen mehrere unabhängige Authentifizierungsfaktoren erforderlich sind.

Die konkrete Faktorbewertung gehört in `AUTHENTICATION_MODEL.md`.

Das Kontomodell hält nur die Zuordnung und den erforderlichen Richtlinienkontext.

## 12. Konto und Sitzung

Ein erfolgreich authentifiziertes Konto kann zur Erzeugung einer Sitzung beitragen.

Eine Sitzung ist jedoch ein separates Objekt mit eigenem Lebenszyklus.

Das Sperren oder Stilllegen eines Kontos muss definierte Auswirkungen auf bestehende Sitzungen haben. Die genauen Regeln werden im `SESSION_MODEL.md` festgelegt.

## 13. Konto und Autorisierung

Ein Konto besitzt nicht automatisch Berechtigungen.

Autorisierung basiert primär auf der Akteursidentität und ihrem Kontext, kann aber den Kontostatus und den Authentifizierungsgrad berücksichtigen.

Ein zweites Konto derselben Identität darf nicht automatisch zusätzliche fachliche Rechte erzeugen.

## 14. Lebenszyklus

Ein Konto besitzt mindestens konzeptionell folgende Zustände:

- vorbereitet;
- aktiv;
- eingeschränkt;
- gesperrt;
- deaktiviert;
- stillgelegt;
- archiviert.

Die genaue Zustandsmaschine wird durch das Kontoschema definiert.

## 15. Sperren

Sperren müssen ausdrücklich modelliert werden.

Eine Sperre kann insbesondere entstehen durch:

- administrative Entscheidung;
- Sicherheitsereignis;
- zu viele fehlgeschlagene Authentifizierungsversuche;
- Richtlinienverletzung;
- Ablauf einer zeitlichen Berechtigung;
- Organisations- oder Projektwechsel;
- manuellen Notfallprozess.

Sperrgrund, auslösende Instanz, Zeitpunkt, Gültigkeitsbereich und Aufhebung müssen auditierbar sein.

## 16. Deaktivierung und Stilllegung

Deaktivierung eines Kontos verhindert reguläre neue Nutzung, ohne die Akteursidentität zu löschen.

Stilllegung markiert das Konto dauerhaft als nicht mehr verwendbar.

Historische Referenzen auf Konto und Identität bleiben erhalten.

Ein stillgelegtes Konto darf nicht für einen anderen Akteur wiederverwendet werden.

## 17. Lokales und externes Konto

Die Plattform muss lokale und externe Konten unterscheiden können.

Ein externes Konto wird durch einen externen Anbieter authentifiziert oder verwaltet, erhält jedoch eine interne stabile Konto-ID und eine kontrollierte Zuordnung zur internen Akteursidentität.

Ein Wechsel des externen Providers darf die interne Identität nicht zwangsläufig verändern.

## 18. Offline-First

Für Offline-Betrieb können lokale Konten oder lokal prüfbare Authentifizierungsnachweise erforderlich sein.

Dabei muss erkennbar sein:

- welche Informationen lokal autoritativ sind;
- wann externe Kontoinformationen zuletzt synchronisiert wurden;
- ob ein Konto offline verwendet werden darf;
- welche Einschränkungen im Offline-Modus gelten.

Ein externer Provider darf den vorgesehenen lokalen Betriebsumfang nicht unnötig blockieren.

## 19. Service- und technische Konten

Technische Konten dürfen nicht als menschliche Benutzerkonten getarnt werden.

Sie müssen mindestens:

- einer technischen Akteursidentität zugeordnet sein;
- einen klaren Zweck besitzen;
- einen begrenzten Gültigkeitsbereich besitzen;
- kontrollierbar gesperrt oder rotiert werden können;
- auditierbar sein.

Gemeinsam genutzte unspezifische Sammelkonten sollen vermieden werden, wenn individuelle technische Identitäten möglich sind.

## 20. Notfall- und Wiederherstellungskonten

Notfallzugänge dürfen nur über ausdrücklich definierte Sicherheitsregeln existieren.

Sie müssen:

- besonders geschützt sein;
- nur für klar definierte Ausnahmefälle vorgesehen sein;
- eine starke Auditierung auslösen;
- zeitlich oder organisatorisch begrenzt sein;
- nach Verwendung überprüft werden.

Das Kontomodell legitimiert keinen unkontrollierten Master-Zugang.

## 21. Whitelist, Blacklist und Ausnahmerechte

Whitelist-/Blacklist-Regeln und Ausnahmerechte sind keine normalen Kontoattribute.

Sie können jedoch Konten als Bedingung oder Ziel referenzieren, beispielsweise für:

- gesperrte Anmeldequellen;
- ausdrücklich erlaubte technische Clients;
- Notfallzugänge;
- geräte- oder netzbezogene Einschränkungen.

Die fachliche Priorität und Entscheidung gehören in `AUTHORIZATION_MODEL.md` bzw. Sicherheitsrichtlinien.

## 22. Datenschutz

Konten können personenbezogene oder sicherheitsrelevante Daten enthalten.

Trennung ist erforderlich zwischen:

- fachlicher Identitätsreferenz;
- Kontakt- oder Login-Kennung;
- sicherheitsrelevanten Metadaten;
- Geheimnissen;
- Auditdaten.

Lösch-, Anonymisierungs- und Aufbewahrungsregeln werden gesondert festgelegt.

## 23. Audit

Mindestens folgende Ereignisse müssen nachvollziehbar sein, soweit relevant:

- Konto angelegt;
- Konto aktiviert;
- Anmeldename geändert;
- Authentifizierungsweg registriert oder entfernt;
- Konto gesperrt oder entsperrt;
- Konto deaktiviert oder stillgelegt;
- Zuordnung zur Akteursidentität geändert;
- sicherheitsrelevante Richtlinien geändert;
- Notfallzugang verwendet.

Geheimnisse selbst dürfen nicht im Audit protokolliert werden.

## 24. Validierung

Ein Konto ist mindestens darauf zu prüfen, dass:

1. eine stabile Konto-ID vorhanden ist;
2. genau eine zulässige primäre Akteursidentitätsreferenz vorhanden ist;
3. Kontoart und Lebenszyklusstatus gültig sind;
4. Anmeldekennungen im vorgesehenen Gültigkeitsbereich eindeutig sind;
5. registrierte Authentifizierungswege zulässig sind;
6. Sperren und Einschränkungen nachvollziehbar sind;
7. keine Geheimnisse als ungeschützte normale Attribute gespeichert werden;
8. technische Konten technischen Identitäten zugeordnet sind;
9. externe Konten ihre Quelle eindeutig referenzieren.

## 25. Invarianten

1. Konto-ID und Akteursidentitäts-ID sind getrennt.
2. Benutzername oder E-Mail-Adresse sind keine stabile Kontoidentität.
3. Ein Konto verleiht allein keine Berechtigungen.
4. Authentifizierung und Konto sind getrennte Verantwortlichkeiten.
5. Sitzung und Konto sind getrennte Objekte.
6. Geheimnisse werden nicht als normale Klartextattribute behandelt.
7. Sperrungen müssen auditierbar sein.
8. Stilllegung zerstört keine erforderlichen historischen Referenzen.
9. Ein zweites Konto derselben Identität erzeugt nicht automatisch zusätzliche Rechte.
10. Technische Konten werden nicht als menschliche Konten modelliert.

## 26. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- konkrete Kennwortregeln;
- Hashing-Algorithmen;
- konkrete MFA-Verfahren;
- Tokenformate;
- Session-Cookies;
- Rollen- und Berechtigungsauflösung;
- konkrete Identity-Provider-Protokolle;
- Schlüsselrotation im Detail;
- konkrete Datenbanktabellen.

## 27. Abhängigkeiten

Dieses Dokument basiert auf:

- `IDENTITY_MODEL.md`;
- `USER_MODEL.md`;
- `PLATFORM_MODEL.md`;
- `PROJECT_MODEL.md`;
- `OBJECT_MODEL.md`;
- `RELATION_MODEL.md`;
- `ADR-0002-identitaet-als-plattformkonzept.md`.

## 28. Ergebnis

Das Konto ist als eigenständige Zugangseinheit definiert. Eine Akteursidentität kann unabhängig von Anzahl, Zustand oder Art ihrer Konten fortbestehen. Damit bleiben Identität, Benutzer, Zugang, Authentifizierung, Sitzung und Autorisierung sauber getrennt.
