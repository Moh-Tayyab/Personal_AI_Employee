#!/usr/bin/env bash
set -euo pipefail

diff_content="$(git diff --cached)"
if [[ -z "$diff_content" ]]; then
  diff_content="$(git diff)"
fi

if [[ -z "$diff_content" ]]; then
  echo "No git changes to review."
  exit 0
fi

codex exec "Review this git diff and suggest improvements. Focus on correctness, tests, and regressions.

$diff_content"
