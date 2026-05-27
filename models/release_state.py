from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class ReleaseState:
    pr_number: int = 14
    release_id: str = "REL-1042"
    findings: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, str]] = field(default_factory=list)
    risk_score: int = 0
    deployment_recommendation: str = "pending"