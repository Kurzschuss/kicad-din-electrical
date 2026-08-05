from __future__ import annotations


def cockpit_layout_css() -> str:
    """Liefert die ergänzenden Layoutregeln für Navigation und Geräteansicht."""
    return """
aside {
  align-self: start;
  position: sticky;
  top: 0;
  max-height: 100vh;
}
.progress-label {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1.5rem;
  min-width: 0;
}
.progress-label span {
  min-width: 0;
}
.progress-percent {
  flex: 0 0 auto;
  margin-left: auto;
  text-align: right;
}
#page-geraete.active {
  height: calc(100vh - 6.5rem);
  overflow: hidden;
}
.device-layout {
  height: 100%;
  min-height: 0;
  align-items: stretch;
}
.device-main {
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr);
  min-height: 0;
  overflow: hidden;
}
.device-main .table-wrap {
  min-height: 0;
  overflow: auto;
}
.details {
  align-self: start;
  max-height: 100%;
  overflow: hidden;
}
.details h2,
.preview-card h3 {
  margin-top: 0;
  margin-bottom: .45rem;
}
.details dl {
  gap: .25rem .6rem;
  margin: 0 0 .6rem;
  font-size: .88rem;
}
.preview-grid {
  grid-template-columns: 1fr;
  gap: .55rem;
  margin-top: .55rem;
}
.preview-card {
  padding: .55rem;
}
.preview {
  min-height: 0;
  height: clamp(120px, 24vh, 190px);
  padding: .45rem;
}
.preview img {
  max-width: 100%;
  max-height: calc(24vh - 2.5rem);
  object-fit: contain;
}
.preview-note,
.preview-status {
  margin-top: .3rem;
  font-size: .78rem;
}
#devices tbody tr.selected {
  box-shadow: inset 5px 0 0 currentColor;
}
@media (max-width: 1050px) {
  aside {
    position: static;
    max-height: none;
  }
  #page-geraete.active {
    height: auto;
    overflow: visible;
  }
  .device-layout {
    height: auto;
  }
  .device-main,
  .details {
    overflow: visible;
    max-height: none;
  }
  .preview {
    height: auto;
    min-height: 150px;
  }
}
""".strip()
