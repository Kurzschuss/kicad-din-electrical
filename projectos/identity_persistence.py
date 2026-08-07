"""Persistente Benutzer-, Rollen- und Berechtigungskonfiguration für SQLite."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import sqlite3

from .authorization import (
    AuthorizationContext,
    AuthorizationService,
    ExceptionRight,
    Role,
)
from .identifiers import BusinessId


@dataclass(frozen=True, slots=True)
class UserAccount:
    """Minimaler persistenter Benutzerstammsatz der ProjectOS-Runtime."""

    user_id: BusinessId
    display_name: str
    active: bool = True

    def __post_init__(self) -> None:
        name = self.display_name.strip()
        if not name:
            raise ValueError("Der Anzeigename eines Benutzers darf nicht leer sein.")
        object.__setattr__(self, "display_name", name)


class SQLiteIdentityRepository:
    """Verwaltet Benutzer und den vollständigen Autorisierungskontext in SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS projectos_users (
                user_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                active INTEGER NOT NULL CHECK (active IN (0, 1))
            );
            CREATE TABLE IF NOT EXISTS projectos_roles (
                role_id TEXT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS projectos_role_permissions (
                role_id TEXT NOT NULL,
                permission_id TEXT NOT NULL,
                PRIMARY KEY(role_id, permission_id),
                FOREIGN KEY(role_id) REFERENCES projectos_roles(role_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS projectos_user_roles (
                user_id TEXT NOT NULL,
                role_id TEXT NOT NULL,
                PRIMARY KEY(user_id, role_id),
                FOREIGN KEY(user_id) REFERENCES projectos_users(user_id) ON DELETE CASCADE,
                FOREIGN KEY(role_id) REFERENCES projectos_roles(role_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS projectos_user_whitelist (
                user_id TEXT NOT NULL,
                permission_id TEXT NOT NULL,
                PRIMARY KEY(user_id, permission_id),
                FOREIGN KEY(user_id) REFERENCES projectos_users(user_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS projectos_user_blacklist (
                user_id TEXT NOT NULL,
                permission_id TEXT NOT NULL,
                PRIMARY KEY(user_id, permission_id),
                FOREIGN KEY(user_id) REFERENCES projectos_users(user_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS projectos_exception_rights (
                exception_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                permission_id TEXT NOT NULL,
                valid_from TEXT NOT NULL,
                valid_until TEXT NOT NULL,
                reason TEXT NOT NULL,
                project_id TEXT,
                FOREIGN KEY(user_id) REFERENCES projectos_users(user_id) ON DELETE CASCADE
            );
            """
        )

    def upsert_user(self, user: UserAccount) -> UserAccount:
        self._connection.execute(
            """
            INSERT INTO projectos_users(user_id, display_name, active)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                display_name = excluded.display_name,
                active = excluded.active
            """,
            (str(user.user_id), user.display_name, int(user.active)),
        )
        return user

    def get_user(self, user_id: BusinessId) -> UserAccount | None:
        row = self._connection.execute(
            "SELECT * FROM projectos_users WHERE user_id = ?", (str(user_id),)
        ).fetchone()
        if row is None:
            return None
        return UserAccount(BusinessId.parse(row["user_id"]), row["display_name"], bool(row["active"]))

    def upsert_role(self, role: Role) -> Role:
        self._connection.execute(
            "INSERT INTO projectos_roles(role_id) VALUES (?) ON CONFLICT(role_id) DO NOTHING",
            (str(role.role_id),),
        )
        self._connection.execute(
            "DELETE FROM projectos_role_permissions WHERE role_id = ?", (str(role.role_id),)
        )
        self._connection.executemany(
            "INSERT INTO projectos_role_permissions(role_id, permission_id) VALUES (?, ?)",
            ((str(role.role_id), str(permission)) for permission in sorted(role.permissions, key=str)),
        )
        return role

    def assign_role(self, user_id: BusinessId, role_id: BusinessId) -> None:
        self._require_active_user(user_id)
        self._require_role(role_id)
        self._connection.execute(
            "INSERT INTO projectos_user_roles(user_id, role_id) VALUES (?, ?) ON CONFLICT DO NOTHING",
            (str(user_id), str(role_id)),
        )

    def set_whitelist(self, user_id: BusinessId, permissions: frozenset[BusinessId]) -> None:
        self._replace_user_permissions("projectos_user_whitelist", user_id, permissions)

    def set_blacklist(self, user_id: BusinessId, permissions: frozenset[BusinessId]) -> None:
        self._replace_user_permissions("projectos_user_blacklist", user_id, permissions)

    def add_exception_right(self, right: ExceptionRight) -> ExceptionRight:
        self._require_active_user(right.user_id)
        self._connection.execute(
            """
            INSERT INTO projectos_exception_rights(
                exception_id, user_id, permission_id, valid_from, valid_until, reason, project_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(exception_id) DO UPDATE SET
                user_id = excluded.user_id,
                permission_id = excluded.permission_id,
                valid_from = excluded.valid_from,
                valid_until = excluded.valid_until,
                reason = excluded.reason,
                project_id = excluded.project_id
            """,
            (
                str(right.exception_id), str(right.user_id), str(right.permission),
                right.valid_from.isoformat(), right.valid_until.isoformat(), right.reason,
                None if right.project_id is None else str(right.project_id),
            ),
        )
        return right

    def create_context(
        self, user_id: BusinessId, *, project_id: BusinessId | None = None
    ) -> AuthorizationContext:
        self._require_active_user(user_id)
        rows = self._connection.execute(
            "SELECT role_id FROM projectos_user_roles WHERE user_id = ? ORDER BY role_id",
            (str(user_id),),
        ).fetchall()
        return AuthorizationContext(
            user_id=user_id,
            role_ids=frozenset(BusinessId.parse(row["role_id"]) for row in rows),
            project_id=project_id,
        )

    def create_authorization_service(self) -> AuthorizationService:
        role_rows = self._connection.execute(
            "SELECT role_id FROM projectos_roles ORDER BY role_id"
        ).fetchall()
        roles: dict[BusinessId, Role] = {}
        for row in role_rows:
            role_id = BusinessId.parse(row["role_id"])
            permissions = self._connection.execute(
                "SELECT permission_id FROM projectos_role_permissions WHERE role_id = ? ORDER BY permission_id",
                (str(role_id),),
            ).fetchall()
            roles[role_id] = Role(
                role_id,
                frozenset(BusinessId.parse(item["permission_id"]) for item in permissions),
            )

        whitelist = self._load_user_permissions("projectos_user_whitelist")
        blacklist = self._load_user_permissions("projectos_user_blacklist")
        exception_rows = self._connection.execute(
            "SELECT * FROM projectos_exception_rights ORDER BY exception_id"
        ).fetchall()
        exception_rights = tuple(
            ExceptionRight(
                exception_id=BusinessId.parse(row["exception_id"]),
                user_id=BusinessId.parse(row["user_id"]),
                permission=BusinessId.parse(row["permission_id"]),
                valid_from=datetime.fromisoformat(row["valid_from"]),
                valid_until=datetime.fromisoformat(row["valid_until"]),
                reason=row["reason"],
                project_id=(None if row["project_id"] is None else BusinessId.parse(row["project_id"])),
            )
            for row in exception_rows
        )
        return AuthorizationService(
            roles=roles,
            whitelist=whitelist,
            blacklist=blacklist,
            exception_rights=exception_rights,
        )

    def _replace_user_permissions(
        self, table: str, user_id: BusinessId, permissions: frozenset[BusinessId]
    ) -> None:
        self._require_active_user(user_id)
        self._connection.execute(f"DELETE FROM {table} WHERE user_id = ?", (str(user_id),))
        self._connection.executemany(
            f"INSERT INTO {table}(user_id, permission_id) VALUES (?, ?)",
            ((str(user_id), str(permission)) for permission in sorted(permissions, key=str)),
        )

    def _load_user_permissions(self, table: str) -> dict[BusinessId, frozenset[BusinessId]]:
        rows = self._connection.execute(
            f"SELECT user_id, permission_id FROM {table} ORDER BY user_id, permission_id"
        ).fetchall()
        values: dict[BusinessId, set[BusinessId]] = {}
        for row in rows:
            values.setdefault(BusinessId.parse(row["user_id"]), set()).add(
                BusinessId.parse(row["permission_id"])
            )
        return {user: frozenset(permissions) for user, permissions in values.items()}

    def _require_active_user(self, user_id: BusinessId) -> None:
        user = self.get_user(user_id)
        if user is None:
            raise LookupError("ERR-IDM-0001: Benutzer wurde nicht gefunden.")
        if not user.active:
            raise PermissionError("ERR-IDM-0002: Benutzer ist deaktiviert.")

    def _require_role(self, role_id: BusinessId) -> None:
        row = self._connection.execute(
            "SELECT 1 FROM projectos_roles WHERE role_id = ?", (str(role_id),)
        ).fetchone()
        if row is None:
            raise LookupError("ERR-IDM-0003: Rolle wurde nicht gefunden.")
