# Non-Diarised Transcript Guidance

Use this reference only when the transcript does not reliably label speakers.

## Core principle

Treat non-diarised input as a reconstruction problem, not a transcription problem.

Never fabricate speaker attribution to make the output look neat.

Keep three categories separate:

1. what is explicit in the text
2. what is probably true but inferred
3. what cannot be assigned with confidence

## Rules

- Treat speaker identity as unknown unless the source identifies it.
- Do not invent names, roles, or precise turn ownership.
- Reconstruct likely conversational structure only from textual cues such as discourse markers, adjacency pairs, repairs, direct responses, sharp topic shifts, and competing positions.
- Preserve uncertainty. If attribution or turn boundaries are ambiguous, say so briefly and clearly.
- Prioritise conversational meaning over tidy speaker labels. Capture:
  - questions and answers
  - agreement and disagreement
  - objections and rebuttals
  - decisions, unresolved issues, and action items
  - emotional or pragmatic tone only where the evidence is strong
- Separate observed content from interpretation.
- Use careful inference language such as `likely`, `appears`, `suggests`, and `possibly`.
- Never collapse competing viewpoints into one agreed position unless the discussion clearly resolves them.

## Useful speaker-boundary signals

Look for:

- a shift in subject position, such as `I think` to `from my side`
- direct address or direct response
- a noticeable register or tone shift
- turn-taking language such as `over to you`
- repair language such as `I mean`, `sorry`, or `what I meant was`
- contradiction markers such as `however`, `that said`, `no`, or `yes, but`
- agenda-shift phrases such as `moving on` or `the other thing`
- pauses or paragraph breaks where present

## Fallback labels

Only if attribution is genuinely useful and the text supports grouping, use neutral placeholders consistently:

- `Speaker A`, `Speaker B`, and so on
- `Facilitator` only where facilitation is evident from the language
- `Unknown` only where a contribution cannot be grouped with confidence

Do not invent named identities.

## Confidence handling

Where attribution matters downstream, use a quiet internal confidence model:

- high: explicit self-identification
- medium: strong contextual signal
- low: conversational-flow inference only

Do not over-expose this. A short `Source Interpretation Note` in the internal output is usually enough.

## What not to do

Do not:

- assign speakers just to improve readability
- merge disagreement into consensus
- turn hedged comments into firm decisions
- linearise overlapping discussion too aggressively
- pretend the transcript is more reliable than it is

## Multiple hypotheses for messy stretches

Where a stretch of text is genuinely ambiguous, two plausible readings are better than one forced guess:

- Interpretation A: this is a clarification from the same speaker
- Interpretation B: this is an interruption or reply from another participant

## Internal reasoning scaffold

Before producing user-facing output:

1. segment the text into likely contribution blocks
2. classify each block as confident boundary, possible boundary, or no reliable boundary
3. detect conversational signals such as interruption, affirmation, objection, elaboration, question, answer, correction, decision, and action item
4. only then generate the summary outputs

This scaffold does not need to appear in the final output.
