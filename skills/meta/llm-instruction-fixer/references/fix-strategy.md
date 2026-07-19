# Repair Priorities

Work from behaviour-critical defects down to polish.

## First: unsafe trust and authority boundaries

Repair any path where untrusted source content can become behavioural authority, select tools or destinations, disclose unrelated context, or drive privileged side effects. Prefer explicit trust classification, least privilege, constrained egress, deterministic validation, human approval, and shutdown controls over claims that prompt wording or regex sanitisation makes arbitrary text safe.

## Second: colliding rules

Resolve places where the model is being told two incompatible things. That may mean:

- naming the winning rule
- merging overlapping directions
- deleting the lower-value instruction

## Third: unstable output contract

Make the output shape more deterministic by tightening:

- required sections
- ordering
- formatting expectations
- refusal or failure handling

## Fourth: inconsistent voice

Bring the file back to one operating stance when persona drift could change outputs.

## Fifth: overload and structure

If the file is hard to execute, simplify the shape before adding more content. Common improvements:

- ordered rules
- shorter sections
- clearer hierarchy
- explicit precedence notes

## Sixth: real coverage gaps

Add only the missing behaviour needed to stop avoidable guessing.

## Last: secondary tightening

Once the execution surface is stable, clean up weaker issues such as:

- vague modifiers
- duplicate wording
- examples that add noise rather than clarity
