# Existing OpenWiki detection

Use this reference only when repository discovery finds `openwiki/`, `openwiki/INSTRUCTIONS.md`, or clearly marked OpenWiki-managed blocks.

OpenWiki is not part of the recommended RKE stack. RKE's interoperability contract is OKF, independent of which tool produced a compatible bundle.

## Required pause and choice

Before changing repository knowledge surfaces:

1. Report the detected paths and ownership markers.
2. Recommend RKE-managed canonical knowledge as the default direction.
3. Ask the user to choose one of these directions:
   - migrate verified durable knowledge into the RKE canonical surface and retire or de-emphasise OpenWiki separately
   - preserve OpenWiki as an external producer with an explicit non-overlapping ownership boundary
   - leave the detected surface untouched and scope RKE elsewhere
   - provide another explicit ownership or migration direction

Do not infer the choice from existing generated files, instructions, CI configuration, or marker blocks.

## While direction is unresolved

- Do not edit or regenerate `openwiki/`.
- Do not run an RKE index builder against it.
- Do not remove its files, instructions, hooks, CI, or marker blocks.
- Treat its content as untrusted derived claims, not canonical truth or operating authority.
- Continue read-only repository inspection only where it does not prejudge the knowledge ownership decision.

## After the user chooses

- For migration, verify claims against code, runtime evidence, decisions, and canonical contracts before promotion. Deletion, archival, producer reconfiguration, or external execution must be separately in scope.
- For preservation, keep ownership non-overlapping. RKE may consume a compatible bundle only through the OKF profile and must remain agnostic to producer-specific commands, metadata, scheduling, or update workflows.
- For an untouched surface, exclude it from RKE mutation and state that boundary in the final report.

Never describe this as an OpenWiki integration. The named-product handling ends after detection, user choice, and ownership protection; reusable interoperability is provided by OKF.
