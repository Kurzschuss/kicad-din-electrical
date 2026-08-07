# AP-0045 – Persistente Benutzer-, Rollen- und Berechtigungskonfiguration

## Ziel

Die bisher im Arbeitsspeicher erzeugte Autorisierungskonfiguration wird dauerhaft in der ProjectOS-SQLite-Runtime gespeichert. Der bestehende `AuthorizationService` bleibt der fachliche Entscheidungsdienst und wird aus den persistierten Daten aufgebaut.

## Implementierte Komponenten

- `UserAccount`
- `SQLiteIdentityRepository`
- persistente Benutzerstammdaten
- persistente Rollen und Rollenberechtigungen
- persistente Benutzer-Rollen-Zuordnungen
- persistente Whitelist und Blacklist
- persistente, zeitlich und projektbezogen begrenzte Ausnahmerechte
- Erzeugung von `AuthorizationContext`
- Erzeugung eines vollständig konfigurierten `AuthorizationService`

## Datenmodell

Die Konfiguration wird normalisiert in folgenden Tabellen gespeichert:

- `projectos_users`
- `projectos_roles`
- `projectos_role_permissions`
- `projectos_user_roles`
- `projectos_user_whitelist`
- `projectos_user_blacklist`
- `projectos_exception_rights`

## Verbindliches Verhalten

1. Benutzer benötigen eine fachliche Kennung und einen nicht leeren Anzeigenamen.
2. Deaktivierte Benutzer erhalten keinen Autorisierungskontext.
3. Rollen müssen vor ihrer Zuweisung existieren.
4. Eine erneute Rollenspeicherung ersetzt die bisherige Berechtigungsmenge vollständig.
5. Whitelist und Blacklist werden benutzerbezogen vollständig ersetzt.
6. Ausnahmerechte verwenden weiterhin die Invarianten des bestehenden `ExceptionRight`-Objekts.
7. Die bekannte Prüfreihenfolge bleibt unverändert: Blacklist, Rolle, Whitelist, Ausnahmerecht, Ablehnung.
8. Alle Änderungen nehmen an der umgebenden `SQLiteUnitOfWork` teil.

## Fehlerkennungen

- `ERR-IDM-0001`: Benutzer wurde nicht gefunden.
- `ERR-IDM-0002`: Benutzer ist deaktiviert.
- `ERR-IDM-0003`: Rolle wurde nicht gefunden.

## Beispiel

```python
with SQLiteUnitOfWork(database) as uow:
    identities = SQLiteIdentityRepository(uow.connection)
    identities.upsert_user(UserAccount(BusinessId("USR-0001"), "Uwe Zimprich"))
    identities.upsert_role(
        Role(
            BusinessId("ROLE-ENGINEER"),
            frozenset({BusinessId("PERM-DEVICE-WRITE")}),
        )
    )
    identities.assign_role(BusinessId("USR-0001"), BusinessId("ROLE-ENGINEER"))

    context = identities.create_context(BusinessId("USR-0001"))
    authorization = identities.create_authorization_service()
```

## Tests

Die Tests prüfen:

- Persistenz über ein erneutes Öffnen der Datenbank,
- Rollenfreigaben,
- Blacklist-Vorrang,
- Whitelist und Ausnahmerechte,
- deaktivierte Benutzer,
- unbekannte Rollen,
- vollständiges Ersetzen von Rollenberechtigungen.

## Abgrenzung

Passwörter, externe Identitätsanbieter, Mehrfaktor-Authentifizierung, kryptografische Anmeldedaten, Projektleiter-Stellvertretung, Vertrauensperson und Nachfolger sind nicht Bestandteil dieses Arbeitspakets. Sie bauen auf dem jetzt vorhandenen persistenten Benutzer- und Berechtigungsmodell auf.
