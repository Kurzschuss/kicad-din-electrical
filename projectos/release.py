"""Versionierungs- und Release-Metadaten für ProjectOS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Mapping


class VersionBump(StrEnum):
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


@dataclass(frozen=True, order=True, slots=True)
class SemanticVersion:
    major: int
    minor: int
    patch: int

    def __post_init__(self) -> None:
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in (self.major, self.minor, self.patch)):
            raise ValueError("Versionsbestandteile müssen nichtnegative Ganzzahlen sein.")

    @classmethod
    def parse(cls, value: str) -> "SemanticVersion":
        parts = value.strip().removeprefix("v").split(".")
        if len(parts) != 3 or any(not part.isdigit() for part in parts):
            raise ValueError("Versionen müssen dem Schema MAJOR.MINOR.PATCH entsprechen.")
        return cls(*(int(part) for part in parts))

    def bump(self, kind: VersionBump) -> "SemanticVersion":
        if kind is VersionBump.MAJOR:
            return SemanticVersion(self.major + 1, 0, 0)
        if kind is VersionBump.MINOR:
            return SemanticVersion(self.major, self.minor + 1, 0)
        return SemanticVersion(self.major, self.minor, self.patch + 1)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True, slots=True)
class ReleaseManifest:
    version: SemanticVersion
    created_at: datetime
    commit_sha: str
    artifacts: Mapping[str, str] = field(default_factory=dict)
    manifest_hash: str = ""

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None:
            raise ValueError("Der Release-Zeitpunkt benötigt einen Zeitzonenbezug.")
        commit_sha = self.commit_sha.strip().lower()
        if len(commit_sha) < 7 or any(ch not in "0123456789abcdef" for ch in commit_sha):
            raise ValueError("Die Commit-SHA ist ungültig.")
        artifacts = MappingProxyType(dict(sorted(self.artifacts.items())))
        object.__setattr__(self, "created_at", self.created_at.astimezone(timezone.utc))
        object.__setattr__(self, "commit_sha", commit_sha)
        object.__setattr__(self, "artifacts", artifacts)
        expected = self.calculate_hash()
        if self.manifest_hash and self.manifest_hash != expected:
            raise ValueError("Die Prüfsumme des Release-Manifests ist ungültig.")
        object.__setattr__(self, "manifest_hash", expected)

    def calculate_hash(self) -> str:
        payload = {
            "version": str(self.version),
            "created_at": self.created_at.astimezone(timezone.utc).isoformat(),
            "commit_sha": self.commit_sha.strip().lower(),
            "artifacts": dict(sorted(self.artifacts.items())),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return sha256(encoded).hexdigest()
