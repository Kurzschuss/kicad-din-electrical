"""UI-neutraler Breadcrumb- und Rücksprungkontext für Z_Cockpit-Navigation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .z_cockpit_navigation import ZCockpitNavigationTarget


@dataclass(frozen=True)
class ZCockpitBreadcrumb:
    """Beschrifteter, validierter Navigationsschritt ohne UI-Routingdetails."""

    label: str
    target: ZCockpitNavigationTarget

    def __post_init__(self) -> None:
        label = str(self.label).strip()
        if not label:
            raise ValueError("breadcrumb label must not be empty")
        object.__setattr__(self, "label", label)

    def as_dict(self) -> dict[str, Any]:
        return {"label": self.label, "target": self.target.as_dict()}


@dataclass(frozen=True)
class ZCockpitNavigationContext:
    """Hält aktuellen Zielpunkt, Herkunft und Rücksprungpfad für tiefe Z_Cockpit-Navigation."""

    current: ZCockpitNavigationTarget
    breadcrumbs: tuple[ZCockpitBreadcrumb, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        project_id = self.current.project_id
        for crumb in self.breadcrumbs:
            if crumb.target.project_id != project_id:
                raise ValueError("breadcrumb target belongs to another project")

    @property
    def return_target(self) -> ZCockpitNavigationTarget | None:
        return self.breadcrumbs[-1].target if self.breadcrumbs else None

    def push(
        self,
        target: ZCockpitNavigationTarget,
        *,
        current_label: str,
    ) -> "ZCockpitNavigationContext":
        if target.project_id != self.current.project_id:
            raise ValueError("navigation target belongs to another project")
        return ZCockpitNavigationContext(
            current=target,
            breadcrumbs=self.breadcrumbs + (ZCockpitBreadcrumb(current_label, self.current),),
        )

    def back(self) -> "ZCockpitNavigationContext":
        if not self.breadcrumbs:
            return self
        return ZCockpitNavigationContext(
            current=self.breadcrumbs[-1].target,
            breadcrumbs=self.breadcrumbs[:-1],
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "current": self.current.as_dict(),
            "breadcrumbs": [crumb.as_dict() for crumb in self.breadcrumbs],
            "return_target": self.return_target.as_dict() if self.return_target else None,
            "depth": len(self.breadcrumbs),
        }
