# Automotive MR Test Prioritization Tool

This repo contains a small, rule-based helper for deciding what to test first
when an automotive merge request changes software that may affect vehicle
behavior.

The idea is simple: not every changed file deserves the same test effort. If an
MR touches battery derating, diagnostics, ECUs, bus communication, or a module
with previous field issues, the validation team should see that risk clearly and
early.

## What It Does

The script reads a JSON summary of an MR and produces a Markdown report that
answers the questions a test engineer usually asks first:

- Which modules or vehicle functions should we test first?
- Why are those areas risky?
- Which requirements are connected to the change?
- Have we seen similar defects before?
- What kind of testing makes sense: HIL, SIL, bench, vehicle, diagnostics, or regression?
- Which areas can be tested more lightly for this MR?

The scoring is intentionally transparent. It is not machine learning and it does
not try to replace engineering judgement. It gives the team a fast, explainable
starting point for test planning.

## Files

- `generate_test_priorities.py`: the command-line tool
- `sample_mr_input.json`: an example automotive MR input
- `input_output_template.md`: a blank template for preparing MR data
- `system_prompt.md`: optional prompt text if this is later paired with an LLM
- `mr_test_prioritization_agent.md`: design notes for the test-prioritization assistant

## Run It

```bash
python3 generate_test_priorities.py sample_mr_input.json
```

To save the report:

```bash
python3 generate_test_priorities.py sample_mr_input.json -o report.md
```

## Input Data

The tool works best when the input includes:

- `project_requirements`
- `vehicle_platform`
- `affected_ecus`
- `compliance_tags`
- `safety_notes`
- `mr_title`
- `mr_description`
- `acceptance_criteria`
- `changed_files`
- `diff_summary`
- `modules_touched`
- `bug_history`
- `known_risky_modules`
- `test_coverage_notes`

You do not need perfect data to use it. If some information is missing, the
report will still be generated, but the prioritization will be better when bug
history, affected ECUs, and touched modules are filled in clearly.

## How It Prioritizes

The tool raises priority when an MR appears to touch:

- safety-related functions such as charging, battery, braking, steering, ADAS, or thermal management
- diagnostics, DTC behavior, UDS, CAN/LIN/FlexRay/Ethernet communication, or ECU interfaces
- modules with previous field issues or repeated bugs
- fail-safe behavior, degraded modes, timing windows, calibration, or state machines
- areas tagged with safety or process standards such as ISO 26262, ASPICE, SOTIF, cybersecurity, or UNECE

The output is a practical report, not a pass/fail decision. A validation engineer
should still review the result and adjust it based on release context, vehicle
availability, safety impact, and test coverage.

## LLM Direction

For now, the repo stays rule-based. That keeps the score repeatable and easy to
defend in a review.

If an LLM is added later, it should be used only as a writing layer:

1. Let `generate_test_priorities.py` create the deterministic risk report.
2. Give that report to the LLM.
3. Ask the LLM to rewrite it into a polished test strategy without changing the
   priority order or inventing missing ECUs, requirements, modules, or defects.

In short: the script decides the priority; an LLM may help explain it better.

## Current Scope

This version is focused on local JSON input. A useful next step would be reading
MR metadata directly from GitLab or GitHub and generating the JSON automatically.
