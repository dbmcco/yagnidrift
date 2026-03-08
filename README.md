# yagnidrift

`yagnidrift` is a Speedrift-suite sidecar for **YAGNI drift** (speculative complexity).

It flags when a task appears to add more structure than needed right now: too many new files/directories or speculative abstraction layers.

## Ecosystem Map

This project is part of the Speedrift suite for Workgraph-first drift control.

- Spine: [Workgraph](https://graphwork.github.io/)
- Orchestrator: [driftdriver](https://github.com/dbmcco/driftdriver)
- Baseline lane: [coredrift](https://github.com/dbmcco/coredrift)
- Optional lanes: [specdrift](https://github.com/dbmcco/specdrift), [datadrift](https://github.com/dbmcco/datadrift), [depsdrift](https://github.com/dbmcco/depsdrift), [uxdrift](https://github.com/dbmcco/uxdrift), [therapydrift](https://github.com/dbmcco/therapydrift), [yagnidrift](https://github.com/dbmcco/yagnidrift), [redrift](https://github.com/dbmcco/redrift)

## Task Spec Format

Add a per-task fenced TOML block:

````md
```yagnidrift
schema = 1
max_new_files = 8
max_new_dirs = 3
enforce_no_speculative_abstractions = true
abstraction_keywords = ["factory", "adapter", "manager", "engine", "framework", "orchestrator", "provider", "base"]
allow_paths = ["src/**", "tests/**"]
```
````

## Workgraph Integration

From a Workgraph repo (where `driftdriver install` has written wrappers):

```bash
./.workgraph/drifts check --task <id> --write-log --create-followups
```

Standalone:

```bash
/path/to/yagnidrift/bin/yagnidrift --dir . wg check --task <id> --write-log --create-followups
```

Exit codes:
- `0`: clean
- `3`: findings exist (advisory)

## Agent Guidance

This section is for AI agents (Claude Code, Codex, Amplifier) working in Speedrift-managed repos.

### When This Lane Runs

`yagnidrift` runs automatically when a task description contains a `yagnidrift` TOML block. It is also triggered by `driftdriver` during factory cycles and attractor loop passes.

### Per-Task Workflow

1. yagnidrift flags speculative complexity — too many new files, unnecessary abstraction layers
2. Run drift checks at task start and before completion:
   ```bash
   ./.workgraph/drifts check --task <id> --write-log --create-followups
   ```
3. Drift is advisory — never hard-block the current task
4. If findings appear, prefer follow-up tasks over scope expansion

### Key Rules

- Exit code `0` = clean, `3` = findings exist (advisory)
- Follow-up tasks are deduped and capped at 3 per lane per repo
- Do not suppress findings — let driftdriver manage significance scoring
- yagnidrift watches for abstraction keywords: factory, adapter, manager, engine, framework, orchestrator, provider, base
- If flagged, simplify before adding more structure
- Use `allow_paths` in the spec to whitelist intentional new structure
- Prefer inline code over premature abstractions
