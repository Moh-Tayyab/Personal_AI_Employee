---
name: agent-skill-evals
description: Create, run, and analyze evaluations for agent skills. Use this skill when you want to test skill performance, measure quality, or generate benchmark reports. Includes test case creation, automated execution, and results visualization.
compatibility: Requires Python 3.9+ for evaluation scripts
---

# Agent Skill Evals

This skill provides comprehensive evaluation capabilities for agent skills, including test case creation, automated execution, benchmarking, and results analysis.

## When to Use This Skill

- Testing new skills before deployment
- Measuring skill performance improvements
- Comparing different skill versions
- Generating quality reports for stakeholders
- Identifying performance bottlenecks

## Core Capabilities

### 1. Test Case Management
- Create structured test cases with inputs, expected outputs, and assertions
- Organize test suites by skill or functionality
- Version test cases for regression testing

### 2. Automated Execution
- Run skills against test suites automatically
- Execute baseline comparisons (with/without skill)
- Capture timing, token usage, and success metrics
- Handle parallel execution for efficiency

### 3. Results Analysis
- Generate benchmark reports with statistical analysis
- Create visualizations (charts, graphs, heatmaps)
- Identify performance patterns and anomalies
- Calculate confidence intervals and significance

### 4. Quality Assurance
- Automated assertion checking
- Edge case detection
- Regression testing
- Performance regression alerts

## Workflow

### Creating Evaluations

1. **Define Test Cases**
   - Write realistic prompts that trigger the skill
   - Specify expected output formats and quality criteria
   - Create assertions for objective verification

2. **Run Evaluations**
   - Execute test cases automatically
   - Capture baseline performance
   - Measure timing, tokens, and success rates

3. **Analyze Results**
   - Generate comprehensive reports
   - Visualize performance trends
   - Identify improvement opportunities

### Quality Metrics Tracked

- **Success Rate**: Percentage of test cases passing assertions
- **Execution Time**: Average and distribution of completion times
- **Token Usage**: Resource efficiency metrics
- **Accuracy**: Precision and recall for specific tasks
- **Robustness**: Performance across edge cases

## Output Formats

### Reports
- **Benchmark Reports**: Statistical summaries with confidence intervals
- **Quality Dashboards**: Interactive visualizations of performance
- **Regression Reports**: Changes between versions
- **Compliance Reports**: Adherence to specifications

### Data Formats
- **JSON Results**: Structured data for further analysis
- **CSV Exports**: Spreadsheet-compatible data
- **HTML Dashboards**: Interactive web-based reports
- **PDF Summaries**: Professional printable reports

## Best Practices

### Test Case Design
- Use realistic, representative prompts
- Include both common and edge cases
- Balance test suite size vs execution time
- Version test cases for reproducibility

### Evaluation Strategy
- Run multiple iterations for statistical significance
- Compare against baseline implementations
- Test under realistic constraints
- Include performance regression tests

### Results Interpretation
- Focus on actionable insights
- Consider statistical significance
- Account for variance and confidence
- Prioritize user experience over raw metrics

## Integration

This skill works with:
- Any agent skill in the skills/ directory
- External evaluation frameworks
- Continuous integration pipelines
- Quality assurance workflows

## Example Use Cases

### Skill Development
```
# Before deployment
1. Create test suite for new skill
2. Run comprehensive evaluation
3. Analyze results and fix issues
4. Generate final quality report
```

### Performance Monitoring
```
# Regular checks
1. Run monthly skill evaluations
2. Compare against previous versions
3. Alert on performance regressions
4. Update benchmarks
```

### Quality Assurance
```
# Release validation
1. Execute regression test suite
2. Verify compliance with specs
3. Generate release report
4. Document quality metrics
```

## Getting Started

1. **Create Test Suite**: Define what you want to test
2. **Run Evaluation**: Execute tests automatically
3. **Review Results**: Analyze the generated reports
4. **Iterate**: Improve based on findings

This skill transforms subjective skill assessment into objective, measurable quality assurance.