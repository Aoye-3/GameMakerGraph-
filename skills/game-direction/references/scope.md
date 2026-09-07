# Scope Lens

Use this lens to protect the smallest coherent player experience while exposing schedule, dependency, and
production risk.

## Establish the baseline

Clarify what must be protected: the player action and feeling, the assumption the next build must test, real
platform/time/capacity constraints, reusable assets, and already committed implementation. If no baseline
exists, define a testable one before calling new work scope creep.

## Evaluation axes

- **Core versus support:** Does the item test the core promise or only make it broader or prettier?
- **Uncertainty reduction:** Does it answer an important unknown or build around an unproven assumption?
- **Dependency fan-out:** How many systems, assets, interfaces, and verification paths must change?
- **Content multiplication:** Does a mechanic create reusable variety or demand handcrafted content repeatedly?
- **Integration cost:** Is a small item expensive once connected to controls, UI, saves, assets, or balance?
- **Reversibility:** Can it be prototyped or removed cheaply?
- **Quality floor:** What companion feedback/onboarding/testing is necessary for the slice to be understandable?
- **Cut integrity:** Does the cut preserve a coherent experience instead of disconnected systems?

Classify work as **keep now**, **simplify**, **defer**, or **cut**. Prefer dependency reasoning to false numeric
precision. Return the smallest coherent slice, explicit inclusions/exclusions, largest risk, cheapest test,
and the observation that would justify expanding scope. Do not create schedules or task plans unless asked.
