from __future__ import annotations


def user_management_scroll_fix_html() -> str:
    """Ergänzt robuste Scrollregeln für die gewachsene Benutzerverwaltung.

    Die Benutzerseite enthält inzwischen Simulations- und Governance-Bereiche.
    Diese dürfen die Benutzerliste oder den rechten Eigenschaftenbereich nicht
    aus dem sichtbaren Cockpit abschneiden. Die Regeln werden bewusst zuletzt
    eingebunden und betreffen ausschließlich ``#page-benutzer``.
    """
    return """\
<style id="user-management-scroll-fix">
#page-benutzer .user-management-main {
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-gutter: stable;
  overscroll-behavior: contain;
}
#page-benutzer .user-management-table-wrap {
  flex: 1 0 16rem;
  min-height: 16rem;
}
#page-benutzer .user-management-inspector {
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-gutter: stable;
  overscroll-behavior: contain;
}
#page-benutzer #user-management-inspector-content {
  flex: 0 0 auto;
  display: block;
  min-height: 0;
  overflow: visible;
}
#page-benutzer .user-management-lifecycle-section {
  min-height: auto;
  flex: 0 0 auto;
  display: block;
}
#page-benutzer .user-management-lifecycle {
  overflow: visible;
}
@media (max-width: 1050px) {
  #page-benutzer.active {
    overflow-y: auto;
    overflow-x: hidden;
  }
  #page-benutzer .user-management-workspace {
    height: auto;
    min-height: 100%;
    overflow: visible;
  }
  #page-benutzer .user-management-main,
  #page-benutzer .user-management-inspector {
    overflow: visible;
  }
  #page-benutzer .user-management-inspector {
    max-height: none;
  }
  #page-benutzer .user-management-table-wrap {
    min-height: 18rem;
  }
}
</style>
"""
