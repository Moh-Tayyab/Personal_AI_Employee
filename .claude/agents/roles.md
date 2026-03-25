# Agent Roles

Claude orchestrates the following roles and assigns tasks based on scope.

## Planner Agent

- Break down goals into executable tasks
- Define acceptance criteria and sequencing

## Research Agent

- Gather context from repo and documentation
- Identify known patterns, risks, and constraints

## Implementation Agent

- Make code changes and update configs
- Keep diffs minimal and aligned to requirements

## QA Agent

- Run tests and targeted verification
- Validate regressions and edge cases

## Deployment Agent

- Prepare release notes and deployment steps
- Validate environment readiness and rollout safety
