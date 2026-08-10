import pytest

from tools.z_cockpit import DEFAULT_PAGES, page_by_id


def test_default_pages_have_unique_ids_and_german_labels() -> None:
    ids = [page.page_id for page in DEFAULT_PAGES]
    assert len(ids) == len(set(ids))
    assert all(page.label_de for page in DEFAULT_PAGES)
    assert all(page.description_de for page in DEFAULT_PAGES)


def test_implemented_core_pages_are_registered() -> None:
    assert page_by_id("start").implemented is True
    assert page_by_id("geraete").implemented is True
    assert page_by_id("bibliotheken").implemented is True
    assert page_by_id("hersteller").implemented is True
    assert page_by_id("qualitaet").implemented is True
    assert page_by_id("diagnose").implemented is True
    assert page_by_id("benutzer").implemented is True
    assert page_by_id("berechtigungen").implemented is True
    assert page_by_id("fehlerbericht").implemented is True
    assert page_by_id("sicherheit").implemented is True
    assert page_by_id("dokumentation").implemented is True
    assert page_by_id("einstellungen").implemented is True


def test_all_registered_core_pages_are_implemented() -> None:
    assert all(page.implemented for page in DEFAULT_PAGES)


def test_unknown_page_is_rejected() -> None:
    with pytest.raises(KeyError, match="Unbekannte Z_Cockpit-Seite"):
        page_by_id("unbekannt")
