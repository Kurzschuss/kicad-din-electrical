from datetime import datetime, timezone

import pytest

from projectos.release import ReleaseManifest, SemanticVersion, VersionBump


def test_semantic_version_parse_and_format() -> None:
    assert str(SemanticVersion.parse("v1.2.3")) == "1.2.3"


def test_semantic_version_bumps_reset_lower_parts() -> None:
    version = SemanticVersion(1, 2, 3)
    assert version.bump(VersionBump.PATCH) == SemanticVersion(1, 2, 4)
    assert version.bump(VersionBump.MINOR) == SemanticVersion(1, 3, 0)
    assert version.bump(VersionBump.MAJOR) == SemanticVersion(2, 0, 0)


def test_invalid_semantic_version_is_rejected() -> None:
    with pytest.raises(ValueError):
        SemanticVersion.parse("1.2")


def test_release_manifest_is_deterministic_and_immutable() -> None:
    manifest = ReleaseManifest(
        version=SemanticVersion(0, 15, 0),
        created_at=datetime(2026, 8, 6, 7, 0, tzinfo=timezone.utc),
        commit_sha="abcdef1234567890",
        artifacts={"wheel": "sha256:123", "sdist": "sha256:456"},
    )
    assert manifest.manifest_hash == manifest.calculate_hash()
    with pytest.raises(TypeError):
        manifest.artifacts["other"] = "sha256:789"  # type: ignore[index]


def test_release_manifest_rejects_invalid_hash() -> None:
    with pytest.raises(ValueError):
        ReleaseManifest(
            version=SemanticVersion(0, 15, 0),
            created_at=datetime.now(timezone.utc),
            commit_sha="abcdef1234567890",
            manifest_hash="falsch",
        )
