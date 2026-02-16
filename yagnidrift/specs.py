from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from typing import Any


FENCE_INFO = "yagnidrift"

_FENCE_RE = re.compile(
    r"```(?P<info>yagnidrift)\s*\n(?P<body>.*?)\n```",
    re.DOTALL,
)


def extract_yagnidrift_spec(description: str) -> str | None:
    m = _FENCE_RE.search(description or "")
    if not m:
        return None
    return m.group("body").strip()


def parse_yagnidrift_spec(text: str) -> dict[str, Any]:
    data = tomllib.loads(text)
    if not isinstance(data, dict):
        raise ValueError("yagnidrift block must parse to a TOML table/object.")
    return data


@dataclass(frozen=True)
class YagnidriftSpec:
    schema: int
    max_new_files: int
    max_new_dirs: int
    enforce_no_speculative_abstractions: bool
    abstraction_keywords: list[str]
    allow_paths: list[str]
    ignore: list[str]

    @staticmethod
    def from_raw(raw: dict[str, Any]) -> "YagnidriftSpec":
        schema = int(raw.get("schema", 1))
        max_new_files = int(raw.get("max_new_files", 8))
        if max_new_files < 0:
            max_new_files = 0
        max_new_dirs = int(raw.get("max_new_dirs", 3))
        if max_new_dirs < 0:
            max_new_dirs = 0
        enforce_no_spec = bool(raw.get("enforce_no_speculative_abstractions", True))
        abstraction_keywords = [
            str(x).lower()
            for x in (
                raw.get("abstraction_keywords")
                or ["factory", "adapter", "manager", "engine", "framework", "orchestrator", "provider", "base"]
            )
        ]
        allow_paths = [str(x) for x in (raw.get("allow_paths") or [])]
        ignore = [str(x) for x in (raw.get("ignore") or [])]
        ignore = [*ignore, ".workgraph/**", ".git/**"]
        return YagnidriftSpec(
            schema=schema,
            max_new_files=max_new_files,
            max_new_dirs=max_new_dirs,
            enforce_no_speculative_abstractions=enforce_no_spec,
            abstraction_keywords=abstraction_keywords,
            allow_paths=allow_paths,
            ignore=ignore,
        )
