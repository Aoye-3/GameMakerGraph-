# Playtest Lens

Use this lens only when actual player behavior, runtime evidence, captures, traces, diagnostics, or structured
notes exist.

## Separate evidence from interpretation

- **Observation:** what the player did, said, missed, repeated, or abandoned;
- **Context:** build revision, familiarity, platform/input, test goal, and session conditions;
- **Interpretation:** a plausible explanation;
- **Confidence:** how strongly the evidence supports it;
- **Evidence gap:** what would distinguish competing explanations.

A player's proposed solution is evidence of dissatisfaction or desire, not automatically the correct fix.

## Evaluation axes

- Did the behavior recur, and can the same state be reached again?
- Does it block progress, hide the intended experience, create unfairness, or reduce polish?
- How often and how widely is the issue exposed?
- Is implementation failing the intent, or is the intended experience itself weak?
- Do behavior, comments, state, captures, and diagnostics agree?
- Could onboarding, controls, readability, balance, performance, or a bug produce the same symptom?
- Could the proposed fix damage unrepresented players or situations?

Classify findings as implementation defect, comprehension problem, balance/pacing problem, experience problem,
or evidence problem. Prioritize at most three. For each, return observation/context, likely cause and a credible
alternative, severity/confidence, the smallest discriminating experiment, and evidence needed. If evidence is
stale or contradictory, request a targeted replay instead of recommending a broad redesign.
