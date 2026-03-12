---
name: test-eval-skill
description: A simple skill for testing evaluation frameworks. Use this skill when you want to test the skill evaluation system itself.
---

# Test Evaluation Skill

This is a simple skill designed to test the evaluation framework. It performs basic text transformations.

## Workflow

1. Read the input text
2. Transform the text according to the specified transformation type
3. Return the transformed text

## Transformation Types

- **uppercase**: Convert all text to uppercase
- **reverse**: Reverse the order of characters in the text
- **count**: Count the number of characters in the text

## Example Usage

```
User: Transform "hello world" to uppercase using test-eval-skill
Claude: Uses this skill to convert "hello world" to "HELLO WORLD"
```