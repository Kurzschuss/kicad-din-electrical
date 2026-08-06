"""ProjectOS-Kernpaket für kicad-din-electrical."""

from .identifiers import BusinessId, CorrelationId, ObjectId
from .results import MessageSeverity, Result, ResultMessage
from .runtime import RuntimeInfo, create_runtime_info
from .validation import ValidationProfile, ValidationResult, ValidationRule, Validator

__all__ = [
    "BusinessId",
    "CorrelationId",
    "MessageSeverity",
    "ObjectId",
    "Result",
    "ResultMessage",
    "RuntimeInfo",
    "ValidationProfile",
    "ValidationResult",
    "ValidationRule",
    "Validator",
    "create_runtime_info",
]
__version__ = "0.4.0"
