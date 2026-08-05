import pytest

from tools.z_cockpit import DEFAULT_PAGES, page_by_id


def test_default_pages_have_unique_ids_and_german_labels() -> None:
    ids = [page.page_id for page in DEFAULT_PAGES]
    assert len(ids) == len(set(ids))
    assert all(page.label_de for page in DEFAULT_PAGES)
    assert all(page.description_de for page in DEFAULT_PAGES)


def test_start_and_device_pages_are_implemented() -> None:
    assert page_by_id("start").implemented is True
    assert page_by_id("geraete").implemented is True


def test_planned_core_pages_are_registered() -> None:
    assert page_by_id("bibliotheken").label_de == "Bibliotheken"
    assert page_by_id("qualitaet").label_de == "Qualität"
    assert page_by_id("diagnose").label_de == "Diagnose"
    assert page_by_id("sicherheit").label_de == "Sicherheit"


def test_unknown_page_is_rejected() -> None:
    with pytest.raises(KeyError, match="Unbekannte Z_Cockpit-Seite"):
        page_by_id("unbekannt")
