# Source patterns

Use this file to preserve the method behind the skill without tying it to any specific tracker or document platform.

## Source hierarchy

Treat source material in this order:

1. Authoritative product or design document
2. Implementation specification or scoped delivery document
3. Resolved tasks, tickets, or work items
4. Supporting notes, comments, or walkthrough material

If these conflict, prefer the highest-authority source that still reflects the feature as actually delivered.

## Mapping guidance

Map source material like this:

- summary and scope notes -> `Summary`
- release timing or rollout notes -> `Target release`
- explicit rollout state -> `Release type`
- product areas or surfaces touched -> `App(s)`
- introduction or framing prose -> `# Introduction`
- outcome-focused value statements -> `# Main benefits`
- user roles or affected groups -> `# Who benefits`
- grouped capabilities -> `# Functionality/features`
- explicit decisions or trade-offs -> `# Key decisions and rationale`
- confirmed limitations or rollout conditions -> `# Important considerations`
- source links, task IDs, or document references -> `# Source references`

## Document shaping rules

- group related work into coherent capability themes
- do not mirror source headings blindly if they make the final document harder to scan
- do not reproduce acceptance criteria or implementation checklists in the main body unless they are essential to understanding the feature
- preserve important caveats, rollout conditions, and decisions even when the source is messy
- prefer one strong thematic feature subsection over many tiny sections
