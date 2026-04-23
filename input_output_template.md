# Automotive MR Input Template

Use this as a checklist when preparing data for the prioritization tool.

## Project Requirements

[Paste the vehicle or program requirements affected by the MR.]

## Vehicle Platform

[Example: EV platform Gen3, ADAS program, body control platform.]

## Affected ECUs / Controllers

[List the ECUs, controllers, gateways, sensors, or displays touched by the MR.]

## Safety / Compliance Notes

[Mention ISO 26262, ASPICE, SOTIF, cybersecurity, UNECE, fail-safe behavior, or release constraints.]

## MR Title

[Paste the MR title.]

## MR Description

[Summarize what changed and why.]

## Acceptance Criteria

[Paste the acceptance criteria or validation expectations.]

## Changed Files

[Paste the changed file list.]

## Diff Summary

[Write a short human summary of the code changes.]

## Modules Touched

[List the functional areas touched, for example battery, charging, diagnostics, cluster, ADAS.]

## Bug / Field History

[List previous bugs, field incidents, regressions, or fragile modules related to this MR.]

## Known Risky Modules

[List modules already known to be unstable, complex, or historically defect-prone.]

## Test Coverage Notes

[Mention missing tests, weak coverage, HIL/SIL/bench gaps, or existing automation.]

# Expected Report Shape

## Quick Read

- Overall risk:
- Why:

## What To Test First

| Priority | Module/Function | Why It Matters | Requirement Link | Defect History | Suggested Focus |
| --- | --- | --- | --- | --- | --- |

## Regression Focus

- Area:
- Old issue to replay:
- Why it matters now:

## Suggested Test Scenarios

- Normal case:
- Boundary case:
- Fault case:
- Diagnostic case:
- Regression case:
- Integration case:

## Lower-Priority Areas

- Area:
- Why light testing is enough for this MR:
