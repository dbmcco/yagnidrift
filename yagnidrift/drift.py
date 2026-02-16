from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import PurePosixPath
from typing import Any

from yagnidrift.git_tools import WorkingChanges
from yagnidrift.globmatch import match_any
from yagnidrift.specs import YagnidriftSpec


@dataclass(frozen=True)
class Finding:
    kind: str
    severity: str
    summary: str
    details: dict[str, Any] | None = None


def _is_allowed(path: str, allow_paths: list[str]) -> bool:
    if not allow_paths:
        return False
    return match_any(path, allow_paths)


def _is_speculative(path: str, keywords: list[str]) -> bool:
    low = path.lower()
    stem = PurePosixPath(low).stem
    parts = [p for p in low.replace("-", "_").split("/") if p]
    for kw in keywords:
        token = str(kw).strip().lower()
        if not token:
            continue
        if token in stem:
            return True
        if any(token in part for part in parts):
            return True
    return False


def compute_yagni_drift(
    *,
    task_id: str,
    task_title: str,
    description: str,
    spec: YagnidriftSpec,
    git_root: str | None,
    changes: WorkingChanges | None,
) -> dict[str, Any]:
    findings: list[Finding] = []

    changed_files: list[str] = []
    new_files: list[str] = []
    if changes:
        changed_files = [
            p
            for p in changes.changed_files
            if not (p.startswith(".workgraph/") or p.startswith(".git/") or match_any(p, spec.ignore))
        ]
        new_files = [p for p in changes.new_files if p in changed_files]

    new_dirs = sorted({str(PurePosixPath(p).parent) for p in new_files if str(PurePosixPath(p).parent) not in {"", "."}})

    telemetry: dict[str, Any] = {
        "files_changed": len(changed_files),
        "new_files": len(new_files),
        "new_dirs": len(new_dirs),
    }

    if spec.schema != 1:
        findings.append(
            Finding(
                kind="unsupported_schema",
                severity="warn",
                summary=f"Unsupported yagnidrift schema: {spec.schema} (expected 1)",
            )
        )

    if len(new_files) > spec.max_new_files:
        findings.append(
            Finding(
                kind="too_many_new_files",
                severity="warn",
                summary=f"Task adds many new files ({len(new_files)} > {spec.max_new_files})",
                details={"new_files": new_files[:60]},
            )
        )

    if len(new_dirs) > spec.max_new_dirs:
        findings.append(
            Finding(
                kind="too_many_new_dirs",
                severity="warn",
                summary=f"Task adds many new directories ({len(new_dirs)} > {spec.max_new_dirs})",
                details={"new_dirs": new_dirs[:30]},
            )
        )

    speculative_files: list[str] = []
    if spec.enforce_no_speculative_abstractions:
        for p in new_files:
            if _is_allowed(p, spec.allow_paths):
                continue
            if _is_speculative(p, spec.abstraction_keywords):
                speculative_files.append(p)

    if speculative_files:
        findings.append(
            Finding(
                kind="speculative_abstraction",
                severity="warn",
                summary="Task appears to add speculative abstraction layers not required by current scope",
                details={"files": speculative_files[:50]},
            )
        )

    score = "green"
    if any(f.severity == "warn" for f in findings):
        score = "yellow"
    if any(f.severity == "error" for f in findings):
        score = "red"

    recommendations: list[dict[str, Any]] = []
    for f in findings:
        if f.kind == "too_many_new_files":
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Split work into smaller tasks or remove speculative file scaffolding",
                    "rationale": "Large file creation bursts are a common sign of overbuilding ahead of validated need.",
                }
            )
        elif f.kind == "too_many_new_dirs":
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Flatten directory structure to the minimum needed for this task",
                    "rationale": "Premature structure multiplies maintenance cost and decision surface.",
                }
            )
        elif f.kind == "speculative_abstraction":
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Inline or defer abstraction layers until a second real use-case appears",
                    "rationale": "YAGNI: abstractions should follow repeated pressure, not precede it.",
                }
            )
        elif f.kind == "unsupported_schema":
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Set yagnidrift schema = 1",
                    "rationale": "Only schema v1 is currently supported.",
                }
            )

    seen_actions: set[str] = set()
    recommendations = [r for r in recommendations if not (r["action"] in seen_actions or seen_actions.add(r["action"]))]  # type: ignore[arg-type]

    return {
        "task_id": task_id,
        "task_title": task_title,
        "git_root": git_root,
        "score": score,
        "spec": asdict(spec),
        "telemetry": telemetry,
        "findings": [asdict(f) for f in findings],
        "recommendations": recommendations,
    }
