# Automotive MR Test Prioritization Assistant

This file describes the thinking behind the tool in this repo. The goal is to
help a QA or validation engineer quickly decide where test effort should go when
an automotive merge request arrives.

## Why This Exists

In automotive software, the riskiest part of an MR is not always the largest
code change. A small update to a state machine, diagnostic monitor, CAN signal,
calibration threshold, or fail-safe path can deserve more attention than a much
larger low-risk change.

This assistant is meant to bring those risks to the surface early.

## What It Looks At

The assistant checks the MR against practical validation signals:

- vehicle or program requirements
- touched modules and changed files
- affected ECUs or controllers
- safety notes and compliance tags
- known risky modules
- previous bugs, regressions, or field issues
- acceptance criteria and test coverage notes

## How It Thinks About Risk

An area becomes more important to test when it touches one or more of these:

- safety-related behavior such as charging, battery, braking, steering, ADAS, thermal management, or powertrain control
- ECU-to-ECU communication, gateways, CAN/LIN/FlexRay/Ethernet signals, UDS, OBD, or DTC handling
- fail-safe behavior, fallback states, degraded mode, timeouts, recovery logic, or state transitions
- modules that already have a history of bugs or field incidents
- requirements connected to ISO 26262, ASPICE, SOTIF, cybersecurity, or UNECE work

An area can usually be tested more lightly when the change is isolated, not
safety-relevant, has no known defect history, and does not affect shared vehicle
signals or controllers.

## Expected Output

The report should help the team answer:

- Overall, is this MR low, medium, or high risk?
- Which module should be tested first?
- What requirement or vehicle behavior is connected to that module?
- Which old bug or field issue should be replayed?
- What test style is appropriate: unit, SIL, HIL, bench, vehicle, diagnostic, or regression?
- Which areas are lower priority for this MR?

## Example

If an MR changes battery thermal derating and charging state recovery, and there
was a previous field issue where charging current failed to derate during sensor
latency, the assistant should prioritize:

- battery thermal behavior
- charging current limits
- invalid or delayed sensor values
- DTC reporting
- fail-safe and recovery behavior
- HIL or bench regression for the old failure path

It should not spend equal effort on unrelated display or UI areas unless the MR
also changes driver-visible status behavior.

## Success Criteria

This assistant is useful when it helps the team:

- focus first on the highest-risk vehicle behavior
- connect test effort to requirements and real defect history
- avoid missing fragile ECU, diagnostic, or fail-safe interactions
- explain the test strategy clearly during review
- avoid over-testing areas that are not meaningfully affected by the MR
