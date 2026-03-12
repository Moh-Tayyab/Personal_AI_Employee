# Agent Teams Integration Hooks

# TeammateIdle Hook - Quality Gates
[
  {
    "matcher": "*",
    "hooks": [
      {
        "type": "command",
        "command": "python3 scripts/team_quality_check.py --teammate-id \"$TEAMMATE_ID\" --team-name \"$TEAM_NAME\" --last-action \"$LAST_ACTION\"",
        "statusMessage": "Running teammate quality check..."
      }
    ]
  }
]

# TaskCompleted Hook - Validation
[
  {
    "matcher": "*",
    "hooks": [
      {
        "type": "agent",
        "prompt": "Verify that the completed task meets quality standards and all deliverables are present. Task details: $ARGUMENTS. Check for completeness, accuracy, and adherence to project guidelines.",
        "statusMessage": "Validating completed task...",
        "model": "claude-haiku-4-5-20251001"
      }
    ]
  }
]