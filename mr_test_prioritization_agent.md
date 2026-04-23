# MR Test Prioritization Agent

## Purpose

This agent reviews a merge request (MR) and decides what should be tested first based on:

- project requirements
- changed features in the MR
- impacted modules and dependencies
- previous bugs, regressions, and fragile areas
- business and user risk

The goal is not to test everything equally. The goal is to identify the highest-value tests first and explain why.

## What The Agent Should Do

The agent should:

1. Read the MR summary, changed files, and acceptance criteria.
2. Map code changes to product requirements or user flows.
3. Identify which features are newly added, modified, or at regression risk.
4. Detect modules that historically had bugs or repeated incidents.
5. Prioritize testing around:
   - risky modules
   - cross-module integrations
   - business-critical flows
   - areas similar to previous bugs
6. Produce a clear testing recommendation with priorities.

## Inputs

The agent should expect these inputs when available:

- `project_requirements`
- `mr_title`
- `mr_description`
- `acceptance_criteria`
- `changed_files`
- `diff_summary`
- `modules_touched`
- `bug_history`
- `recent_incidents`
- `test_coverage_notes`
- `known_risky_modules`

## Decision Rules

The agent should use the following logic:

### Priority Signals

Increase priority when:

- the MR changes authentication, payments, checkout, search, notifications, reporting, or other core flows
- the module has repeated bug history
- the change touches shared components, common services, or APIs used by many modules
- the MR changes validation, permissions, state management, calculations, or data mapping
- the change is large, cross-cutting, or poorly described
- the change fixes a previous bug that could regress
- the requirements mention edge cases, exceptions, or conditional logic

Decrease priority when:

- the change is isolated, low-risk, and well-covered by tests
- the module has no recent issues and no dependency impact
- the MR only changes documentation, styling, or copy with no behavioral impact

## Output Format

The agent should return:

### 1. MR Risk Summary

- short description of overall risk
- top reasons for the risk level

### 2. Features To Test First

For each feature or area:

- `priority`: High / Medium / Low
- `feature_or_module`
- `why_it_matters`
- `related_requirement`
- `related_bug_history`
- `recommended_test_focus`

### 3. Modules Requiring Extra Attention

List modules that need deeper validation because of:

- repeated bugs
- fragile integrations
- complex business logic
- dependency or shared-component impact

### 4. Suggested Test Scenarios

Include:

- happy path
- edge cases
- negative scenarios
- regression scenarios
- integration scenarios

### 5. Test Scope Exclusions

Mention areas that do not need deep testing now and explain why.

## Risk Scoring Model

The agent can use a simple score from 1 to 5 for each area:

- `5`: critical business risk or repeated production bugs
- `4`: high impact with integration or logic complexity
- `3`: moderate impact with some regression risk
- `2`: low impact and localized change
- `1`: minimal risk such as copy or cosmetic updates

Example weighting:

- requirement criticality: 30%
- bug history: 25%
- code change breadth: 20%
- integration impact: 15%
- test coverage gaps: 10%

## Recommended Prompt

Use the prompt in `system_prompt.md` as the system instruction for the agent.

## Example Use Case

If an MR changes the checkout discount logic and that module had pricing bugs before, the agent should:

- rank checkout and pricing validation as High priority
- recommend testing discount combinations, invalid coupons, tax calculation interactions, and order total rounding
- call out any shared pricing service or API dependency
- de-prioritize unrelated UI areas not affected by the MR

## Success Criteria

The agent is successful when it:

- focuses the team on the most important test targets
- explains the reasoning behind priorities
- connects MR changes to requirements
- uses bug history to prevent repeat regressions
- avoids wasting effort on low-risk areas
