# Automotive MR Test Prioritization Tool

This tool generates a test-priority report for a merge request using:

- vehicle/program requirements
- MR details
- touched modules and ECUs
- previous bugs or field defects
- known risky modules

## Files

- `generate_test_priorities.py`: command-line tool
- `sample_mr_input.json`: example input
- `system_prompt.md`: reusable prompt if you want an LLM version too
- `mr_test_prioritization_agent.md`: agent design notes

## Run

```bash
python3 generate_test_priorities.py sample_mr_input.json
```

To save the report:

```bash
python3 generate_test_priorities.py sample_mr_input.json -o report.md
```

## Expected Input Format

Provide a JSON file with keys like:

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

## What The Tool Produces

The report includes:

- MR risk summary
- program context
- priority test areas with scores
- modules needing regression focus
- suggested test scenarios
- lower-priority areas

## LLM Integration Direction

The current version intentionally stays rule-based. This keeps the scoring
transparent, repeatable, and easy for automotive QA or validation engineers to
review.

An LLM can be added later as an optional second layer. The recommended approach
is:

1. Use `generate_test_priorities.py` to create the deterministic risk report.
2. Send that report to an LLM only to rewrite it into a more polished test
   strategy.
3. Keep the rule-based score as the source of truth so the LLM does not invent
   modules, ECUs, requirements, or defect history.

## Notes

- The current version uses automotive-specific scoring rules, not machine learning.
- It works best when `modules_touched`, `affected_ecus`, and `bug_history` are filled in clearly.
- It prioritizes safety-critical functions, ECU impact, diagnostics, field defects, and integration-heavy changes.
- If you want, this can be extended next to read MR diffs automatically from GitLab or GitHub exports.
