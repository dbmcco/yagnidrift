# yagnidrift

`yagnidrift` is a Speedrift-suite sidecar for **YAGNI drift** (speculative complexity).

It flags when a task appears to add more structure than needed right now: too many new files/directories or speculative abstraction layers.

## Ecosystem Map

This project is part of the Speedrift suite for Workgraph-first drift control.

- Spine: [Workgraph](https://graphwork.github.io/)
- Orchestrator: [driftdriver](https://github.com/dbmcco/driftdriver)
- Baseline lane: [speedrift](https://github.com/dbmcco/speedrift)
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
