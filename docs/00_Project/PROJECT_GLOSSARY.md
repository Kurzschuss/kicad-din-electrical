# Projektglossar

**Dokument-ID:** REF-0001  
**Titel:** Verbindliches Projektglossar  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Referenz  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Zweck

Dieses Glossar definiert die zentralen Begriffe des Projekts.

Normative Dokumente verwenden die hier festgelegten Begriffe einheitlich. Ein Begriff darf in einem untergeordneten Dokument nur dann abweichend verwendet werden, wenn die Abweichung ausdrücklich beschrieben und begründet ist.

Die Definitionen dieses Glossars konkretisieren die Projektverfassung und die Projektprinzipien. Sie ersetzen keine fachlichen Modelle.

## 2. Architektur

Die dokumentierte Struktur aus Verantwortlichkeiten, Modellen, Beziehungen, Schnittstellen, Regeln und Abhängigkeiten, nach der das System aufgebaut und weiterentwickelt wird.

Architektur ist unabhängig von einer einzelnen technischen Implementierung.

## 3. Artefakt

Ein versionierbarer, referenzierbarer und überprüfbarer Bestandteil des Projekts.

Artefakte können unter anderem Dokumente, Modelle, Spezifikationen, ADRs, Schemata, Quellcode, Tests, Simulationen, Konfigurationen oder generierte Ergebnisse sein.

Eine Datei kann ein Artefakt repräsentieren. Artefakt und Datei sind jedoch nicht grundsätzlich gleichbedeutend.

## 4. Authentifizierung

Der Vorgang, mit dem die behauptete Identität eines Akteurs geprüft wird.

Authentifizierung beantwortet die Frage: „Wer oder was meldet sich an?“

Sie entscheidet nicht automatisch, welche Handlungen erlaubt sind.

## 5. Autorisierung

Der Vorgang, mit dem geprüft wird, ob ein identifizierter Akteur eine bestimmte Handlung in einem bestimmten Geltungsbereich ausführen darf.

Autorisierung beantwortet die Frage: „Darf dieser Akteur diese Handlung hier ausführen?“

## 6. Benutzer

Eine natürliche Person, die mit dem System interagiert oder der fachlich Aktivitäten, Verantwortlichkeiten und Rechte zugeordnet werden.

Ein Benutzer ist nicht mit einem Benutzerkonto gleichzusetzen.

Ein Benutzer kann mehrere Konten oder Identitäten besitzen. Ein Konto kann nur im Rahmen ausdrücklich definierter Regeln mehreren Benutzern zugeordnet werden.

Die vollständige Definition erfolgt in `USER_MANAGEMENT.md`.

## 7. Benutzerkonto

Ein verwalteter Zugangskontext für einen Benutzer oder einen ausdrücklich definierten technischen Akteur.

Ein Benutzerkonto kann Anmeldeinformationen, Status, zugeordnete Identitäten, Sitzungen, Rollen und sicherheitsrelevante Einstellungen besitzen.

Ein Konto ist nicht automatisch die fachliche Identität des Benutzers.

## 8. Berechtigung

Eine ausdrücklich definierte Erlaubnis, eine bestimmte Handlung auf einer bestimmten Ressource oder innerhalb eines bestimmten Geltungsbereichs auszuführen.

Berechtigungen werden durch das Berechtigungsmodell definiert und ausgewertet.

Eine Berechtigung ist nicht dasselbe wie eine Rolle.

## 9. Beziehung

Eine fachlich bedeutsame Verbindung zwischen mindestens zwei Objekten oder Artefakten.

Eine Beziehung besitzt einen Typ und kann Richtung, Geltungsbereich, Eigenschaften, Status, Version und Lebenszyklus besitzen.

## 10. Dienst

Eine klar abgegrenzte fachliche oder technische Fähigkeit mit dokumentierter Verantwortung und Schnittstelle.

Ein Dienst führt definierte Operationen aus, ohne die Verantwortung anderer Domänen zu übernehmen.

## 11. Dokument

Ein menschenlesbares Projektartefakt, das Wissen, Regeln, Entscheidungen, Modelle, Spezifikationen, Anleitungen oder Nachweise beschreibt.

Ein Dokument kann normative oder informative Bedeutung besitzen. Sein Status und seine Autorität müssen erkennbar sein.

## 12. Domäne

Ein fachlich abgegrenzter Verantwortungsbereich mit eigener Sprache, eigenen Modellen und eindeutigem Ownership.

Eine Domäne ist für die maßgebliche Definition der ihr zugeordneten Konzepte verantwortlich.

## 13. Domänenverantwortung

Die eindeutige Zuständigkeit einer Domäne für Definition, Lebenszyklus, Validierung, Änderungsregeln und Kompatibilität eines fachlichen Konzepts.

## 14. Eigentümer

Ein Benutzer, eine Organisationseinheit, ein Systemakteur oder eine ausdrücklich definierte Rolle mit fachlicher Verantwortung für ein Objekt oder Artefakt.

Eigentum ist nicht automatisch mit administrativer Berechtigung gleichzusetzen.

## 15. Ereignis

Eine festgehaltene fachliche Tatsache darüber, dass zu einem bestimmten Zeitpunkt etwas geschehen ist.

Ein Ereignis beschreibt eine eingetretene Veränderung oder Beobachtung und wird nach seiner Veröffentlichung nicht stillschweigend umgedeutet.

Die genaue Modellierung wird in einem zuständigen Ereignis- oder Objektmodell festgelegt.

## 16. Eigenschaft

Ein benannter, definierter und validierbarer Wert, der einen Aspekt eines Objekts, einer Beziehung oder eines Artefakts beschreibt.

Eine Eigenschaft besitzt mindestens Bedeutung, Datentyp oder Wertebereich und gegebenenfalls Gültigkeits- und Versionsregeln.

## 17. Fachmodell

Eine technologieunabhängige Beschreibung fachlicher Begriffe, Regeln, Beziehungen, Zustände und Lebenszyklen einer Domäne.

## 18. Geltungsbereich

Der Kontext, innerhalb dessen eine Regel, Berechtigung, Rolle, Identität oder Entscheidung wirksam ist.

Beispiele sind System, Organisation, Projekt, Domäne, Objektgruppe oder einzelnes Objekt.

## 19. Historie

Die nachvollziehbare Folge relevanter Zustände, Änderungen, Ereignisse und Entscheidungen eines Objekts oder Artefakts.

## 20. Identität

Die dauerhafte fachliche Unterscheidbarkeit eines Objekts, Akteurs oder Artefakts.

Identität bleibt unabhängig von veränderlichen Namen, Pfaden, Darstellungen, Eigentümern und Speicherorten bestehen.

## 21. Implementierung

Die technische Realisierung eines dokumentierten Modells, einer Spezifikation, Schnittstelle oder Entscheidung.

Eine Implementierung ist nicht die maßgebliche Definition der von ihr umgesetzten Fachregel.

## 22. Instanz

Eine konkrete Ausprägung eines durch Modell oder Schema beschriebenen Typs.

Der Begriff wird nur verwendet, wenn zwischen Typdefinition und konkreter Ausprägung unterschieden werden muss.

## 23. Lebenszyklus

Die Menge zulässiger Zustände und Zustandsübergänge eines Objekts, Artefakts, Kontos, Dokuments oder Prozesses.

Ein Lebenszyklus definiert auch Erzeugung, Aktivierung, Änderung, Deaktivierung, Archivierung und gegebenenfalls Löschung.

## 24. Modell

Eine strukturierte und bewusst vereinfachte Beschreibung eines fachlichen oder technischen Sachverhalts.

Ein Modell legt relevante Begriffe, Eigenschaften, Beziehungen, Regeln und Grenzen fest.

## 25. Normativ

Verbindlich für untergeordnete Artefakte, Entscheidungen und Implementierungen.

Normative Aussagen verwenden klare Verpflichtungen und besitzen eine erkennbare Autoritätsebene.

## 26. Objekt

Eine fachliche Einheit mit stabiler Identität.

Ein Objekt kann Eigenschaften, Beziehungen, Status, Version, Historie, Verantwortlichkeit und technische Repräsentationen besitzen.

Ein Objekt ist nicht automatisch eine Klasse, Datei, Tabellenzeile oder Benutzeroberflächenkomponente.

Die vollständige normative Definition erfolgt in `OBJECT_MODEL.md`.

## 27. Offline-First

Das Prinzip, nach dem grundlegende Funktionen und maßgebliche Daten ohne permanente Verbindung zu externen Diensten nutzbar bleiben.

Offline-First bedeutet nicht, dass keine Online-Dienste verwendet werden dürfen.

## 28. Organisationseinheit

Eine strukturierte Gruppe von Benutzern, Rollen oder Verantwortlichkeiten innerhalb eines festgelegten Geltungsbereichs.

Beispiele können Team, Abteilung, Betreiber, Mandant oder Projektgruppe sein.

Die genaue Bedeutung wird im Benutzer- und Rollenmodell festgelegt.

## 29. Projekt

Eine fachliche Einheit mit eigener Identität, Zielsetzung, Verantwortung, Historie und einer Menge zugehöriger Artefakte und Beziehungen.

Ein Projekt ist nicht lediglich ein Ordner oder Repository.

Die vollständige Definition erfolgt in `PROJECT_MODEL.md`.

## 30. Repository

Der versionierte technische Speicherort der verbindlichen Projektartefakte und ihrer Änderungshistorie.

Das Repository ist die maßgebliche Projektquelle, aber nicht mit dem fachlichen Projektobjekt gleichzusetzen.

## 31. Rolle

Eine benannte Zusammenfassung von Verantwortlichkeiten und gegebenenfalls Berechtigungszuweisungen für einen festgelegten Geltungsbereich.

Eine Rolle ist nicht mit einem Benutzer, Konto oder einer einzelnen Berechtigung gleichzusetzen.

Die vollständige Definition erfolgt in `ROLE_MODEL.md`.

## 32. Schema

Eine formale Beschreibung der zulässigen Struktur, Datentypen, Pflichtangaben und Validierungsregeln einer Repräsentation.

Ein Schema beschreibt eine Darstellung. Es ersetzt nicht automatisch das fachliche Modell.

## 33. Servicekonto

Ein Benutzerkonto für einen eindeutig identifizierten technischen Akteur oder automatisierten Prozess.

Servicekonten dürfen nicht als Ersatz für persönliche Benutzerkonten verwendet werden. Verantwortlichkeit, Berechtigungen, Laufzeit und Zweck müssen nachvollziehbar sein.

## 34. Simulation

Eine kontrollierte Ausführung oder Nachbildung von Verhalten ohne die vollständigen realen Auswirkungen der produktiven Ausführung.

Eine Simulation muss bekannte Abweichungen von der Realität dokumentieren.

## 35. Single Source of Truth

Das Prinzip, nach dem es für jedes normative Thema genau eine maßgebliche Definition gibt.

Andere Artefakte verweisen auf diese Definition, statt konkurrierende Wahrheiten zu erzeugen.

## 36. Sitzung

Ein zeitlich und sicherheitstechnisch abgegrenzter Nutzungskontext eines authentifizierten Benutzers oder technischen Akteurs.

Eine Sitzung besitzt einen Lebenszyklus und kann unabhängig vom Benutzerkonto beendet oder widerrufen werden.

## 37. Spezifikation

Eine verbindliche Beschreibung von Anforderungen, Verhalten, Schnittstellen, Einschränkungen und Akzeptanzkriterien.

## 38. Status

Ein definierter Zustand innerhalb eines Lebenszyklus.

Ein Status besitzt nur dann fachliche Bedeutung, wenn zulässige Übergänge und Auswirkungen festgelegt sind.

## 39. Systemakteur

Eine natürliche Person, ein technischer Dienst, ein Gerät oder ein externer Prozess, der innerhalb definierter Vertrauens- und Berechtigungsgrenzen mit dem System interagiert.

## 40. Validierung

Die Prüfung, ob ein Objekt, Artefakt, Wert, Vorgang oder Zustand den zuständigen Regeln, Modellen und Spezifikationen entspricht.

## 41. Version

Eine eindeutig identifizierbare Entwicklungsstufe eines Artefakts, Modells, Schemas, einer Schnittstelle oder Repräsentation.

Verschiedene Versionsebenen dürfen nicht ohne ausdrückliche Regel gleichgesetzt werden.

## 42. Verantwortlichkeit

Die eindeutig zugeordnete Pflicht, eine definierte fachliche oder technische Aufgabe innerhalb eines Geltungsbereichs wahrzunehmen.

Verantwortlichkeit ist nicht automatisch Eigentum und nicht automatisch eine Berechtigung.

## 43. Verweis

Eine auflösbare und möglichst stabile Referenz von einem Artefakt oder Objekt auf ein anderes.

Verweise sollen stabile Identitäten statt ausschließlich veränderlicher Pfade oder Namen verwenden, sobald das zugrunde liegende Modell dies ermöglicht.

## 44. Wissensquelle

Ein Artefakt oder System, das Projektwissen enthält.

Nur ausdrücklich als maßgeblich definierte und versionierte Repository-Artefakte besitzen normative Wirkung.
