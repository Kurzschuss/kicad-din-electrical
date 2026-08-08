# Authentifizierungsmodell

**Dokument-ID:** PLT-0008  
**Titel:** Fachliches Modell der Authentifizierung  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert die Authentifizierung innerhalb von ProjectOS.

Authentifizierung beantwortet die Frage, ob ein vorgelegter Nachweis hinreichend belegt, dass ein bestimmter Akteur beziehungsweise ein bestimmtes Konto tatsächlich verwendet wird.

Authentifizierung entscheidet ausdrücklich nicht, welche fachlichen Rechte der Akteur besitzt. Diese Entscheidung gehört zur Autorisierung.

## 2. Architekturstellung

Das Authentifizierungsmodell gehört zur Plattformebene und baut auf `IDENTITY_MODEL.md`, `USER_MODEL.md` und `ACCOUNT_MODEL.md` auf.

Die wesentliche Trennung lautet:

```text
Identität
    ↓ beschreibt den Akteur
Konto
    ↓ beschreibt den Zugang
Authentifizierung
    ↓ prüft Nachweise
Sitzung
    ↓ hält einen bestätigten Nutzungskontext
Autorisierung
    ↓ entscheidet über erlaubte Handlungen
```

Keine dieser Ebenen darf stillschweigend durch eine andere ersetzt werden.

## 3. Grundsatz

Für jede Authentifizierungsentscheidung muss nachvollziehbar sein:

- welches Konto oder welche Akteursidentität betroffen ist;
- welcher Authentifizierungsweg verwendet wurde;
- welche Faktoren erfolgreich geprüft wurden;
- welcher Vertrauens- beziehungsweise Sicherheitsgrad erreicht wurde;
- wann und in welchem Kontext die Prüfung stattfand;
- ob zusätzliche Einschränkungen gelten;
- ob das Ergebnis zur Erzeugung oder Fortführung einer Sitzung verwendet werden darf.

Ein erfolgreiches Login bedeutet nicht automatisch, dass jede Aktion erlaubt ist.

## 4. Authentifizierungsgegenstand

Authentifiziert werden kann abhängig vom Verfahren insbesondere:

- ein persönliches Benutzerkonto;
- ein technisches Dienstkonto;
- ein Geräte- oder Maschinenkonto;
- ein API-Client;
- ein Automatisierungskonto;
- ein extern angebundenes Konto;
- ein lokal verwendbares Offline-Konto.

Die Authentifizierung muss auf eine interne stabile Konto- oder Identitätsreferenz zurückgeführt werden können.

## 5. Authentifizierungsverfahren

Die Plattform muss mehrere Verfahren unterstützen können, ohne ein einzelnes Verfahren in das fachliche Kontomodell einzubauen.

Mögliche Verfahren sind insbesondere:

- lokales Kennwort;
- Passkey bzw. FIDO-basierter Nachweis;
- Hardware-Token;
- Zertifikat;
- externer Identity Provider;
- gerätegebundener Nachweis;
- API-Schlüssel;
- Client-Credential-Verfahren;
- kurzlebiges Token;
- Wiederherstellungs- oder Notfallverfahren.

Die konkrete technische Umsetzung wird später durch Implementierungs- und Sicherheitsrichtlinien festgelegt.

## 6. Faktoren

Authentifizierungsfaktoren sind getrennt von Authentifizierungsverfahren zu betrachten.

Mindestens konzeptionell unterscheidbar sein sollen:

- Wissen: etwas, das der Akteur kennt;
- Besitz: etwas, das der Akteur besitzt;
- Inhärenz: etwas, das den Akteur physisch kennzeichnet, sofern später unterstützt;
- Gerätebindung: ein vertrauenswürdiges registriertes Gerät;
- externe Vertrauensbestätigung durch einen Identity Provider.

Mehrere Schritte desselben Faktortyps gelten nicht automatisch als unabhängige Mehrfaktor-Authentifizierung.

## 7. Mehrfaktor-Authentifizierung

Die Plattform muss Richtlinien unterstützen können, nach denen für bestimmte Konten, Rollen, Aktionen oder Risikoklassen mehrere unabhängige Faktoren erforderlich sind.

MFA darf nicht als statisches Ja/Nein-Attribut am Benutzer modelliert werden.

Erforderlicher und tatsächlich erreichter Authentifizierungsgrad müssen getrennt betrachtet werden.

## 8. Authentifizierungsgrad

Das Ergebnis einer Authentifizierung muss einen fachlich auswertbaren Authentifizierungsgrad beziehungsweise Vertrauenskontext liefern können.

Dieser kann unter anderem abhängen von:

- verwendeten Faktoren;
- Aktualität der letzten Prüfung;
- Vertrauensstatus des Geräts;
- verwendeter Identitätsquelle;
- Online- oder Offline-Modus;
- besonderem Notfall- oder Wiederherstellungsverfahren.

Die Autorisierung kann diesen Grad später als Bedingung verwenden.

## 9. Step-up-Authentifizierung

Eine bereits aktive Sitzung kann für besonders kritische Aktionen eine erneute oder stärkere Authentifizierung verlangen.

Beispiele:

- Änderung von Rollen oder Berechtigungen;
- Aktivierung von Ausnahmerechten;
- sicherheitskritische Freigaben;
- Änderung von Authentifizierungsverfahren;
- Zugriff auf besonders geschützte Administrationsfunktionen;
- Verwendung von Notfallmechanismen.

Step-up-Authentifizierung verändert nicht automatisch die Identität oder das Konto, sondern erhöht für einen begrenzten Kontext den bestätigten Authentifizierungsgrad.

## 10. Authentifizierungsergebnis

Ein Authentifizierungsversuch liefert mindestens konzeptionell ein Ergebnis mit:

- Ergebnis-ID;
- Zeitstempel;
- Konto- oder Identitätsreferenz;
- verwendetem Verfahren;
- geprüften Faktorarten;
- Erfolg oder Misserfolg;
- erreichtem Authentifizierungsgrad;
- relevanten Richtlinienreferenzen;
- Fehler- oder Ablehnungsgrund, soweit sicher offenlegbar;
- Kontextinformationen wie Gerät, Client oder Offline-Zustand;
- Auditreferenz.

Geheimnisse oder vollständige Zugangsnachweise sind niemals Bestandteil des Ergebnisses.

## 11. Fehlgeschlagene Authentifizierung

Fehlgeschlagene Authentifizierungsversuche müssen kontrolliert behandelt werden.

Die Plattform muss insbesondere ermöglichen:

- Zählung und Bewertung wiederholter Fehlversuche;
- zeitweilige Sperren oder Verzögerungen;
- risikobasierte Eskalation;
- SecurityEvent-Erzeugung;
- Auditierung;
- Schutz vor Benutzer- oder Kontenermittlung durch übermäßig detaillierte Fehlermeldungen.

Ein fehlgeschlagener Authentifizierungsversuch darf keine fachliche Sitzung mit regulären Rechten erzeugen.

## 12. Kontosperren

Das Authentifizierungsmodell respektiert Sperr-, Deaktivierungs- und Stilllegungszustände des Kontomodells.

Eine technisch korrekte Kennwort- oder Tokenprüfung darf ein gesperrtes oder stillgelegtes Konto nicht automatisch wieder freischalten.

Entsperrung ist ein eigener autorisierter Prozess.

## 13. Identitätsquelle

Die Plattform kann mehrere Identitäts- und Authentifizierungsquellen anbinden.

Dazu können gehören:

- lokale ProjectOS-Konten;
- Betriebssystem- oder Unternehmensverzeichnisse;
- föderierte Identity Provider;
- Zertifikatsinfrastrukturen;
- technische Client-Verzeichnisse.

Externe Anbieter liefern Nachweise, sind aber nicht automatisch die interne Single Source of Truth für Rollen, Berechtigungen oder Projektverantwortung.

## 14. Externe Authentifizierung

Bei externer Authentifizierung muss eindeutig bleiben:

- welcher Provider den Nachweis geliefert hat;
- welche externe Kennung verwendet wurde;
- welcher internen Konto- oder Akteursidentität sie zugeordnet ist;
- wann diese Zuordnung geprüft oder synchronisiert wurde;
- ob lokale Einschränkungen oder Sperren den externen Erfolg übersteuern.

Ein externer Erfolg darf eine interne Sperre nicht stillschweigend umgehen.

## 15. Offline-First

ProjectOS muss einen definierten Offline-Betrieb unterstützen können.

Für Authentifizierung bedeutet dies, dass abhängig von Richtlinie lokal prüfbare Verfahren erlaubt sein können.

Dabei muss erkennbar sein:

- ob Offline-Authentifizierung für das Konto erlaubt ist;
- wann die zugrunde liegenden Informationen zuletzt synchronisiert wurden;
- welcher Authentifizierungsgrad offline maximal erreicht werden kann;
- welche Aktionen offline zusätzlich beschränkt sind;
- wie Widerrufe und Sperren nach Wiederverbindung übernommen werden.

Offline-Betrieb darf Sicherheitszustände nicht dauerhaft von der zentralen Plattform entkoppeln.

## 16. Lokale Geheimnisse

Lokale Kennwörter oder andere Geheimnisse dürfen niemals im Klartext gespeichert werden.

Das fachliche Modell legt keine konkrete Hashing- oder Schlüsseltechnologie fest, verlangt aber:

- sichere, zweckgebundene Speicherung;
- Trennung von normalen Kontodaten;
- kontrollierte Rotation;
- keine Ausgabe über Z_Cockpit, Logs oder Audit;
- kein Zurücklesen eines ursprünglichen Kennworts aus der Plattform.

Konkrete Kryptografie gehört in die Sicherheits- und Implementierungsrichtlinien.

## 17. Tokens

Tokens sind keine Identitäten und keine dauerhaften Berechtigungen.

Sie müssen mindestens hinsichtlich folgender Aspekte kontrollierbar sein:

- Aussteller;
- Zielgruppe bzw. Verwendungszweck;
- zugeordnete Konto- oder Identitätsreferenz;
- Gültigkeitsbeginn und Ablauf;
- Widerrufbarkeit, sofern vorgesehen;
- zulässiger Kontext;
- erforderlicher Authentifizierungsgrad.

Langfristige fachliche Rechte dürfen nicht ausschließlich in unkontrollierten Tokeninhalten als zweite Wahrheit geführt werden.

## 18. API- und technische Authentifizierung

Technische Akteure benötigen eigene Authentifizierungsverfahren.

Für technische Konten gilt insbesondere:

- keine Verwendung persönlicher Benutzerkennwörter;
- eindeutige technische Identität;
- begrenzter Zweck und Gültigkeitsbereich;
- rotierbare Nachweise;
- auditierbare Verwendung;
- Möglichkeit zur gezielten Sperrung ohne Deaktivierung anderer Akteure.

## 19. Gerätebindung

Ein registriertes Gerät kann als zusätzlicher Vertrauensfaktor berücksichtigt werden.

Gerätebindung darf jedoch nicht automatisch mit menschlicher Identität gleichgesetzt werden.

Ein kompromittiertes oder verlorenes Gerät muss gezielt entzogen werden können, ohne die menschliche Identität zu löschen.

## 20. Notfall- und Wiederherstellungsverfahren

Notfall- und Wiederherstellungsauthentifizierung ist ausdrücklich als Ausnahmeweg zu behandeln.

Sie muss:

- besonders geschützt sein;
- einen klaren Auslösegrund besitzen;
- einen begrenzten Gültigkeitsbereich haben;
- starke Auditierung erzeugen;
- nach Verwendung überprüfbar sein;
- nach Möglichkeit einen niedrigeren oder gesondert markierten Vertrauensstatus liefern, bis reguläre Nachweise wiederhergestellt sind.

Ein universeller und nicht auditierter Master-Schlüssel ist nicht Teil des Plattformmodells.

## 21. Sitzungserzeugung

Erfolgreiche Authentifizierung kann die Erzeugung einer Sitzung erlauben.

Die Sitzung ist ein eigenes Objekt und übernimmt mindestens kontrollierte Informationen über:

- Akteursidentität;
- verwendetes Konto;
- Authentifizierungszeitpunkt;
- erreichten Authentifizierungsgrad;
- relevante Einschränkungen;
- Ablauf- und Erneuerungsregeln.

Die genaue Lebenszykluslogik gehört in `SESSION_MODEL.md`.

## 22. Re-Authentifizierung

Eine Sitzung darf nicht unbegrenzt von einem einmaligen Authentifizierungserfolg zehren.

Richtlinien können erneute Authentifizierung verlangen abhängig von:

- Zeitablauf;
- Inaktivität;
- Sicherheitsereignis;
- Kontostatusänderung;
- Gerätewechsel;
- besonders kritischer Aktion;
- Erhöhung des erforderlichen Authentifizierungsgrads.

## 23. Abmeldung und Widerruf

Abmeldung beendet oder entwertet die zugehörige Sitzung nach den Regeln des Sitzungsmodells.

Zusätzlich muss die Plattform gezielten Widerruf ermöglichen können, etwa für:

- einzelne Sitzung;
- alle Sitzungen eines Kontos;
- bestimmte Geräte;
- bestimmte Tokenklassen;
- kompromittierte Authentifizierungsverfahren.

Widerruf eines Nachweises ist nicht automatisch identisch mit Stilllegung der Identität.

## 24. Sicherheitsereignisse

Sicherheitsrelevante Authentifizierungsereignisse müssen in das kanonische `SecurityEvent`-Modell von ProjectOS überführbar sein.

Dazu gehören insbesondere:

- auffällige Fehlversuche;
- Nutzung gesperrter Konten;
- unerwartete MFA-Änderungen;
- Verwendung eines Notfallverfahrens;
- verdächtige Tokenverwendung;
- fehlgeschlagene Provider-Zuordnung;
- sicherheitskritische Step-up-Vorgänge.

Es darf keine neue parallele Sicherheitsereigniskette entstehen.

## 25. Audit

Mindestens folgende Ereignisse müssen auditierbar sein, soweit relevant:

- Authentifizierungsverfahren registriert;
- Authentifizierungsverfahren entfernt oder rotiert;
- erfolgreicher Authentifizierungsversuch;
- sicherheitsrelevanter fehlgeschlagener Versuch;
- MFA-Konfiguration geändert;
- Step-up-Authentifizierung durchgeführt;
- Wiederherstellungs- oder Notfallverfahren verwendet;
- Token oder Nachweis widerrufen;
- externe Provider-Zuordnung verändert.

Kennwörter, private Schlüssel, vollständige Tokens oder vergleichbare Geheimnisse dürfen nicht im Audit erscheinen.

## 26. Datenschutz

Authentifizierungsdaten können personenbezogene und sicherheitskritische Informationen enthalten.

Deshalb sind insbesondere zu trennen:

- fachliche Identitätsreferenz;
- Authentifizierungsmetadaten;
- technische Sicherheitsinformationen;
- Geheimnisse;
- Auditdaten.

Oberflächen und Berichte dürfen nur die Informationen anzeigen, die für den jeweiligen Zweck erforderlich sind.

## 27. Z_Cockpit

Das Z_Cockpit darf Authentifizierungszustände darstellen und autorisierte Verwaltungsaktionen auslösen, ist aber nicht die Authentifizierungsengine.

Darstellbar sind beispielsweise:

- registrierte Authentifizierungsverfahren ohne Geheimnisse;
- MFA-Status;
- Kontosperrstatus;
- letzte erfolgreiche Authentifizierung, soweit datenschutzrechtlich zulässig;
- aktive oder widerrufbare Sitzungen;
- notwendige Step-up-Anforderungen;
- relevante Sicherheitswarnungen.

Das Cockpit darf keine Kennwörter, privaten Schlüssel oder vollständigen Tokens ausgeben oder als zweite Quelle speichern.

Die allgemeinen Integrationsregeln stehen in `Z_COCKPIT_IDENTITY_INTEGRATION.md`.

## 28. Validierung

Ein Authentifizierungsprozess ist mindestens darauf zu prüfen, dass:

1. Konto- oder Identitätsreferenz eindeutig auflösbar ist;
2. das verwendete Verfahren für den Akteur zulässig ist;
3. Konto und Verfahren nicht gesperrt oder stillgelegt sind;
4. erforderliche Faktoren vollständig erfüllt sind;
5. das Ergebnis einen nachvollziehbaren Authentifizierungsgrad besitzt;
6. keine Geheimnisse in Ergebnis, Audit oder Oberfläche gelangen;
7. externe Nachweise korrekt der internen Identität zugeordnet werden;
8. Offline-Verwendung den dafür geltenden Richtlinien entspricht;
9. sicherheitsrelevante Ereignisse kanonisch protokolliert werden.

## 29. Invarianten

1. Authentifizierung ist nicht Autorisierung.
2. Ein Konto ist nicht die Identität.
3. Ein erfolgreicher Login verleiht allein keine fachlichen Rechte.
4. Geheimnisse sind keine normalen Kontoeigenschaften.
5. Externe Provider ersetzen nicht automatisch die interne Identität.
6. Interne Kontosperren dürfen durch externe Authentifizierung nicht umgangen werden.
7. MFA wird als Richtlinie und Ergebnisgrad modelliert, nicht nur als einzelnes Benutzerflag.
8. Step-up-Authentifizierung ist zeitlich und kontextuell begrenzt.
9. Technische Akteure verwenden eigene technische Identitäten und Nachweise.
10. Sicherheitsrelevante Authentifizierungsereignisse verwenden das kanonische SecurityEvent-Modell.
11. Offline-Authentifizierung darf nur innerhalb ausdrücklich definierter Grenzen erfolgen.
12. Z_Cockpit ist keine zweite Authentifizierungsquelle.

## 30. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- konkrete Hashing-Algorithmen;
- konkrete FIDO-, OAuth-, OIDC-, SAML- oder LDAP-Implementierungen;
- konkrete Tokenformate;
- konkrete Cookie-Attribute;
- konkrete Datenbanktabellen;
- konkrete kryptografische Schlüsselgrößen;
- Rollen- und Berechtigungsauflösung;
- Sitzungslebenszyklus im Detail;
- Benutzeroberflächenlayout.

## 31. Abhängigkeiten

Dieses Dokument basiert auf:

- `IDENTITY_MODEL.md`;
- `USER_MODEL.md`;
- `ACCOUNT_MODEL.md`;
- `PLATFORM_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`;
- dem kanonischen `projectos.security_events`-Modell.

Folgende Modelle bauen darauf auf oder verwenden seine Ergebnisse:

- `SESSION_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- Rollen- und Berechtigungsmodelle;
- Sicherheitsrichtlinien.

## 32. Ergebnis

Authentifizierung ist als eigenständige Plattformverantwortung definiert. Sie prüft Nachweise, liefert einen nachvollziehbaren Authentifizierungsgrad und kann eine Sitzung begründen, verleiht aber selbst keine fachlichen Rechte. Damit bleiben Identität, Zugang, Nachweisprüfung, Sitzung und Autorisierung sauber getrennt und können konsistent in ProjectOS und Z_Cockpit verwendet werden.
