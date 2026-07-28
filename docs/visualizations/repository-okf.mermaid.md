# skills

> Generated from repository-local OKF records. The Markdown/YAML bundle remains canonical.

Source: `skills`

The report separates the connected repository map from detailed component and key-concept views so large bundles remain reviewable.

## Connected-area overview

```mermaid
flowchart LR
    a0["docs · 3 concepts"]
    a1["future-consideration · 6 concepts"]
    a2["repository root · 1 concepts"]
    a3["tasks · 1 concepts"]
    a0 -->|links| a1
    a0 -->|links| a2
    a0 -->|links| a3
    a1 -->|links| a0
    a2 -->|links| a0
    a3 -->|links| a0
    classDef default fill:#eef2ff,stroke:#4f46e5,color:#1e1b4b
```

## Connected component 1

```mermaid
flowchart LR
    n0["skills complete Markdown inventory"]:::knowledge
    n1["skills documentation map"]:::knowledge
    n2["skills repository OKF visualization"]:::knowledge
    n3["Autofix candidate assessor"]:::knowledge
    n4["Codebase Context Pack Builder"]:::knowledge
    n5["Company Context Pack Builder"]:::knowledge
    n6["Hook Setup Skill"]:::knowledge
    n7["QA Guidance Pack Builder"]:::knowledge
    n8["Future Consideration"]:::knowledge
    n9["Skills Workbench"]:::knowledge
    n10["Adopt RKE OKF knowledge format · done"]:::task
    n0 -->|links| n1
    n0 -->|links| n2
    n0 -->|links| n3
    n0 -->|links| n4
    n0 -->|links| n5
    n0 -->|links| n6
    n0 -->|links| n7
    n0 -->|links| n8
    n0 -->|links| n9
    n0 -->|links| n10
    n1 -->|links| n9
    n1 -->|links| n0
    n1 -->|links| n3
    n1 -->|links| n4
    n1 -->|links| n5
    n1 -->|links| n6
    n1 -->|links| n7
    n1 -->|links| n8
    n1 -->|links| n10
    n1 -->|links| n2
    n2 -->|links| n1
    n2 -->|links| n0
    n2 -->|links| n10
    n3 -->|links| n1
    n4 -->|links| n1
    n5 -->|links| n1
    n6 -->|links| n1
    n7 -->|links| n1
    n8 -->|links| n1
    n9 -->|links| n1
    n10 -->|links| n1
    n10 -->|links| n2
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

## Key concept neighbourhoods

### skills documentation map

```mermaid
flowchart LR
    n0["skills complete Markdown inventory"]:::boundary
    n1["skills documentation map"]:::knowledge
    n2["skills repository OKF visualization"]:::boundary
    n3["Autofix candidate assessor"]:::boundary
    n4["Codebase Context Pack Builder"]:::boundary
    n5["Company Context Pack Builder"]:::boundary
    n6["Hook Setup Skill"]:::boundary
    n7["QA Guidance Pack Builder"]:::boundary
    n8["Future Consideration"]:::boundary
    n9["Skills Workbench"]:::boundary
    n10["Adopt RKE OKF knowledge format · done"]:::boundary
    n0 -->|links| n1
    n0 -->|links| n2
    n0 -->|links| n3
    n0 -->|links| n4
    n0 -->|links| n5
    n0 -->|links| n6
    n0 -->|links| n7
    n0 -->|links| n8
    n0 -->|links| n9
    n0 -->|links| n10
    n1 -->|links| n9
    n1 -->|links| n0
    n1 -->|links| n3
    n1 -->|links| n4
    n1 -->|links| n5
    n1 -->|links| n6
    n1 -->|links| n7
    n1 -->|links| n8
    n1 -->|links| n10
    n1 -->|links| n2
    n2 -->|links| n1
    n2 -->|links| n0
    n2 -->|links| n10
    n3 -->|links| n1
    n4 -->|links| n1
    n5 -->|links| n1
    n6 -->|links| n1
    n7 -->|links| n1
    n8 -->|links| n1
    n9 -->|links| n1
    n10 -->|links| n1
    n10 -->|links| n2
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

### skills complete Markdown inventory

```mermaid
flowchart LR
    n0["skills complete Markdown inventory"]:::knowledge
    n1["skills documentation map"]:::boundary
    n2["skills repository OKF visualization"]:::boundary
    n3["Autofix candidate assessor"]:::boundary
    n4["Codebase Context Pack Builder"]:::boundary
    n5["Company Context Pack Builder"]:::boundary
    n6["Hook Setup Skill"]:::boundary
    n7["QA Guidance Pack Builder"]:::boundary
    n8["Future Consideration"]:::boundary
    n9["Skills Workbench"]:::boundary
    n10["Adopt RKE OKF knowledge format · done"]:::boundary
    n0 -->|links| n1
    n0 -->|links| n2
    n0 -->|links| n3
    n0 -->|links| n4
    n0 -->|links| n5
    n0 -->|links| n6
    n0 -->|links| n7
    n0 -->|links| n8
    n0 -->|links| n9
    n0 -->|links| n10
    n1 -->|links| n9
    n1 -->|links| n0
    n1 -->|links| n3
    n1 -->|links| n4
    n1 -->|links| n5
    n1 -->|links| n6
    n1 -->|links| n7
    n1 -->|links| n8
    n1 -->|links| n10
    n1 -->|links| n2
    n2 -->|links| n1
    n2 -->|links| n0
    n2 -->|links| n10
    n3 -->|links| n1
    n4 -->|links| n1
    n5 -->|links| n1
    n6 -->|links| n1
    n7 -->|links| n1
    n8 -->|links| n1
    n9 -->|links| n1
    n10 -->|links| n1
    n10 -->|links| n2
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

### skills repository OKF visualization

```mermaid
flowchart LR
    n0["skills complete Markdown inventory"]:::boundary
    n1["skills documentation map"]:::boundary
    n2["skills repository OKF visualization"]:::knowledge
    n3["Adopt RKE OKF knowledge format · done"]:::boundary
    n0 -->|links| n1
    n0 -->|links| n2
    n0 -->|links| n3
    n1 -->|links| n0
    n1 -->|links| n3
    n1 -->|links| n2
    n2 -->|links| n1
    n2 -->|links| n0
    n2 -->|links| n3
    n3 -->|links| n1
    n3 -->|links| n2
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

### Adopt RKE OKF knowledge format

```mermaid
flowchart LR
    n0["skills complete Markdown inventory"]:::boundary
    n1["skills documentation map"]:::boundary
    n2["skills repository OKF visualization"]:::boundary
    n3["Adopt RKE OKF knowledge format · done"]:::task
    n0 -->|links| n1
    n0 -->|links| n2
    n0 -->|links| n3
    n1 -->|links| n0
    n1 -->|links| n3
    n1 -->|links| n2
    n2 -->|links| n1
    n2 -->|links| n0
    n2 -->|links| n3
    n3 -->|links| n1
    n3 -->|links| n2
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

### Skills Workbench

```mermaid
flowchart LR
    n0["skills complete Markdown inventory"]:::boundary
    n1["skills documentation map"]:::boundary
    n2["Skills Workbench"]:::knowledge
    n0 -->|links| n1
    n0 -->|links| n2
    n1 -->|links| n2
    n1 -->|links| n0
    n2 -->|links| n1
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

### Future Consideration

```mermaid
flowchart LR
    n0["skills complete Markdown inventory"]:::boundary
    n1["skills documentation map"]:::boundary
    n2["Future Consideration"]:::knowledge
    n0 -->|links| n1
    n0 -->|links| n2
    n1 -->|links| n0
    n1 -->|links| n2
    n2 -->|links| n1
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

## Legend

- Blue: task
- Purple: workstream
- Orange: tracker profile
- Green: durable knowledge
- Dashed neutral nodes: neighbouring context repeated from another area or key-concept view
- Time references: edges to addressable `Task.time[]` fragments
- Arrows: structured relationships or repository-local Markdown links
