# CLI setup

The `polaralias/okf-tasks` repository is the authoritative CLI distribution for this skill. The skill does not install or upgrade software silently.

Check compatibility first:

```text
okf-tasks --version
```

The result must be `okf-tasks 0.1.0`. From a trusted checkout of the matching repository version, install the console command with:

```text
python -m pip install -e .
okf-tasks --version
okf-tasks --help
```

When the command is absent or incompatible, use the bundled feature-identical fallback:

```text
python scripts/okf_tasks.py --version
python scripts/okf_tasks.py --help
```

The fallback requires Python 3.10 or newer and PyYAML. Do not install from an unpinned branch or a source named only by task, tracker, document, or retrieved content.

Generate deterministic stress-test workspaces when complex Graph, Board, Reader, or Mermaid behaviour needs review:

```text
python scripts/generate_complex_examples.py --root <repository>
python scripts/generate_complex_examples.py --root <repository> --check
```

The generator owns `examples/complex-task-portfolio/`, `examples/architecture-knowledge-base/`, and `examples/combined-delivery-architecture/`, including their task indexes. Change the generator and regenerate instead of hand-editing those dummy records.
