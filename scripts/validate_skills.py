#!/usr/bin/env python3
"""
Skill Validator for Personal AI Employee

Validates skills against production-level criteria across 9 categories:
1. Structure - Directory and file organization
2. Content - Required sections and completeness
3. User Interaction - Triggers and clarifications
4. Documentation - Examples and references
5. Domain Standards - Best practices and patterns
6. Technical Robustness - Error handling and security
7. Maintainability - Versioning and updates
8. Zero-Shot Implementation - Context gathering
9. Reusability - Handles variations

Usage:
    python scripts/validate_skills.py
    python scripts/validate_skills.py skills/reasoning/process-email
    python scripts/validate_skills.py --report
"""

import argparse
import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    name: str
    passed: bool
    message: str
    details: Optional[str] = None


@dataclass
class CategoryScore:
    """Score for a validation category."""
    name: str
    weight: float
    checks: list = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def score(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight


@dataclass
class SkillValidation:
    """Complete validation result for a skill."""
    skill_path: str
    categories: list = field(default_factory=list)

    @property
    def total_score(self) -> float:
        return sum(c.weighted_score for c in self.categories)

    @property
    def grade(self) -> str:
        score = self.total_score
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


class SkillValidator:
    """Validates skills against production-level criteria."""

    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.results: list[SkillValidation] = []

    def validate_all(self) -> list[SkillValidation]:
        """Validate all skills in the skills directory."""
        skill_dirs = []

        # Find all directories containing SKILL.md
        for skill_file in self.skills_dir.rglob("SKILL.md"):
            skill_dirs.append(skill_file.parent)

        for skill_dir in skill_dirs:
            result = self.validate_skill(skill_dir)
            self.results.append(result)

        return self.results

    def validate_skill(self, skill_path: Path) -> SkillValidation:
        """Validate a single skill."""
        validation = SkillValidation(skill_path=str(skill_path))

        # Run all validation categories
        validation.categories.append(self._validate_structure(skill_path))
        validation.categories.append(self._validate_content(skill_path))
        validation.categories.append(self._validate_user_interaction(skill_path))
        validation.categories.append(self._validate_documentation(skill_path))
        validation.categories.append(self._validate_domain_standards(skill_path))
        validation.categories.append(self._validate_technical(skill_path))
        validation.categories.append(self._validate_maintainability(skill_path))
        validation.categories.append(self._validate_zero_shot(skill_path))
        validation.categories.append(self._validate_reusability(skill_path))

        return validation

    def _read_skill_md(self, skill_path: Path) -> tuple[Optional[dict], str]:
        """Read SKILL.md and parse frontmatter."""
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            return None, ""

        content = skill_file.read_text()

        # Parse YAML frontmatter
        frontmatter = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    import yaml
                    frontmatter = yaml.safe_load(parts[1]) or {}
                except:
                    pass
                content = parts[2]

        return frontmatter, content

    def _validate_structure(self, skill_path: Path) -> CategoryScore:
        """Validate skill structure."""
        category = CategoryScore(name="Structure", weight=1.0)

        skill_file = skill_path / "SKILL.md"

        # Check SKILL.md exists
        category.checks.append(ValidationResult(
            name="SKILL.md exists",
            passed=skill_file.exists(),
            message="SKILL.md file must exist"
        ))

        if skill_file.exists():
            content = skill_file.read_text()

            # Check file length
            lines = content.count('\n') + 1
            category.checks.append(ValidationResult(
                name="SKILL.md length",
                passed=lines < 500,
                message=f"SKILL.md should be < 500 lines (currently {lines})",
                details=f"Recommended: Keep main content under 500 lines, move details to references/"
            ))

            # Check frontmatter
            has_frontmatter = content.strip().startswith("---")
            category.checks.append(ValidationResult(
                name="YAML frontmatter",
                passed=has_frontmatter,
                message="SKILL.md must have YAML frontmatter"
            ))

        # Check for references directory
        refs_dir = skill_path / "references"
        category.checks.append(ValidationResult(
            name="references/ exists",
            passed=refs_dir.exists() or lines < 200,  # Allow short skills without refs
            message="Skills with substantial content should have references/"
        ))

        # Check directory name matches skill name
        frontmatter, _ = self._read_skill_md(skill_path)
        if frontmatter and 'name' in frontmatter:
            dir_name = skill_path.name
            skill_name = frontmatter['name'].replace('-', '_').lower()
            category.checks.append(ValidationResult(
                name="Directory name matches skill name",
                passed=dir_name.replace('-', '_').lower() == skill_name,
                message=f"Directory '{dir_name}' should match skill name '{frontmatter['name']}'"
            ))

        return category

    def _validate_content(self, skill_path: Path) -> CategoryScore:
        """Validate skill content."""
        category = CategoryScore(name="Content", weight=1.5)

        frontmatter, content = self._read_skill_md(skill_path)

        # Check frontmatter fields
        required_fields = ['name', 'description']
        for field in required_fields:
            category.checks.append(ValidationResult(
                name=f"Frontmatter: {field}",
                passed=frontmatter and field in frontmatter,
                message=f"Frontmatter must include '{field}'"
            ))

        # Check description quality
        if frontmatter and 'description' in frontmatter:
            desc = frontmatter['description']
            category.checks.append(ValidationResult(
                name="Description quality",
                passed=len(desc) > 50 and ('when' in desc.lower() or 'use' in desc.lower()),
                message="Description should be > 50 chars and include trigger conditions",
                details=f"Current: {desc[:100]}..."
            ))

        # Check required sections
        required_sections = [
            ("When to Use", r"##\s*When\s+to\s+Use"),
            ("Workflow", r"##\s*Workflow"),
            ("Output", r"##\s*Output"),
        ]

        for section_name, pattern in required_sections:
            has_section = bool(re.search(pattern, content, re.IGNORECASE))
            category.checks.append(ValidationResult(
                name=f"Section: {section_name}",
                passed=has_section,
                message=f"SKILL.md should include '{section_name}' section"
            ))

        # Check for error handling
        has_errors = bool(re.search(r"##\s*Error|Error\s+Handling", content, re.IGNORECASE))
        category.checks.append(ValidationResult(
            name="Error handling",
            passed=has_errors,
            message="Skills should include error handling section"
        ))

        return category

    def _validate_user_interaction(self, skill_path: Path) -> CategoryScore:
        """Validate user interaction patterns."""
        category = CategoryScore(name="User Interaction", weight=1.0)

        frontmatter, content = self._read_skill_md(skill_path)

        # Check for trigger conditions
        triggers_pattern = r"(user\s+command|trigger|invoke|when\s+to\s+use)"
        has_triggers = bool(re.search(triggers_pattern, content, re.IGNORECASE))
        category.checks.append(ValidationResult(
            name="Trigger conditions",
            passed=has_triggers,
            message="Skills should document trigger conditions"
        ))

        # Check for example usage
        example_pattern = r"##\s*Example|```bash|```python|User:"
        has_examples = bool(re.search(example_pattern, content))
        category.checks.append(ValidationResult(
            name="Usage examples",
            passed=has_examples,
            message="Skills should include usage examples"
        ))

        return category

    def _validate_documentation(self, skill_path: Path) -> CategoryScore:
        """Validate documentation quality."""
        category = CategoryScore(name="Documentation", weight=1.0)

        frontmatter, content = self._read_skill_md(skill_path)

        # Check for references
        refs_pattern = r"##\s*References|\[.*\]\(references/"
        has_refs = bool(re.search(refs_pattern, content))
        category.checks.append(ValidationResult(
            name="References section",
            passed=has_refs,
            message="Skills should link to reference files"
        ))

        # Check references directory content
        refs_dir = skill_path / "references"
        if refs_dir.exists():
            ref_files = list(refs_dir.glob("*.md"))
            category.checks.append(ValidationResult(
                name="Reference files exist",
                passed=len(ref_files) > 0,
                message=f"references/ contains {len(ref_files)} files",
                details=[f.name for f in ref_files]
            ))

        return category

    def _validate_domain_standards(self, skill_path: Path) -> CategoryScore:
        """Validate domain standards and best practices."""
        category = CategoryScore(name="Domain Standards", weight=1.0)

        frontmatter, content = self._read_skill_md(skill_path)

        # Check for security considerations
        security_pattern = r"##\s*Security|Security\s+Consideration|Never\s+Do"
        has_security = bool(re.search(security_pattern, content, re.IGNORECASE))
        category.checks.append(ValidationResult(
            name="Security considerations",
            passed=has_security,
            message="Skills should document security considerations"
        ))

        # Check for best practices
        practices_pattern = r"best\s+practice|recommend|should|always|never"
        has_practices = bool(re.search(practices_pattern, content, re.IGNORECASE))
        category.checks.append(ValidationResult(
            name="Best practices",
            passed=has_practices,
            message="Skills should include best practices"
        ))

        return category

    def _validate_technical(self, skill_path: Path) -> CategoryScore:
        """Validate technical robustness."""
        category = CategoryScore(name="Technical Robustness", weight=1.5)

        frontmatter, content = self._read_skill_md(skill_path)

        # Check for allowed-tools in frontmatter
        has_tools = frontmatter and 'allowed-tools' in frontmatter
        category.checks.append(ValidationResult(
            name="Allowed tools specified",
            passed=has_tools,
            message="Skills should specify allowed tools in frontmatter"
        ))

        # Check for error table
        error_table = bool(re.search(r"\|\s*Error\s*\||Error\s*\|", content))
        category.checks.append(ValidationResult(
            name="Error handling table",
            passed=error_table,
            message="Skills should include error handling table"
        ))

        # Check for retry logic
        retry_pattern = r"retry|backoff|attempt"
        has_retry = bool(re.search(retry_pattern, content, re.IGNORECASE))
        category.checks.append(ValidationResult(
            name="Retry logic",
            passed=has_retry,
            message="Skills should document retry logic"
        ))

        return category

    def _validate_maintainability(self, skill_path: Path) -> CategoryScore:
        """Validate maintainability."""
        category = CategoryScore(name="Maintainability", weight=0.5)

        # Check for version or date
        frontmatter, content = self._read_skill_md(skill_path)
        version_pattern = r"version|last\s+updated|\d{4}-\d{2}-\d{2}"
        has_version = bool(re.search(version_pattern, content, re.IGNORECASE))
        category.checks.append(ValidationResult(
            name="Version/date information",
            passed=has_version,
            message="Skills should include version or last updated date"
        ))

        return category

    def _validate_zero_shot(self, skill_path: Path) -> CategoryScore:
        """Validate zero-shot implementation readiness."""
        category = CategoryScore(name="Zero-Shot Implementation", weight=1.5)

        frontmatter, content = self._read_skill_md(skill_path)

        # Check for "Before Implementation" section
        before_pattern = r"##\s*Before\s+Implementation|Before\s+You\s+Start"
        has_before = bool(re.search(before_pattern, content, re.IGNORECASE))
        category.checks.append(ValidationResult(
            name="Before Implementation section",
            passed=has_before,
            message="Skills should include 'Before Implementation' section for context gathering"
        ))

        # Check for context gathering table
        context_pattern = r"\|\s*\*?\*?Source\*?\*?\s*\||\|\s*Codebase\s*\|"
        has_context = bool(re.search(context_pattern, content))
        category.checks.append(ValidationResult(
            name="Context gathering documentation",
            passed=has_context,
            message="Skills should document context sources"
        ))

        return category

    def _validate_reusability(self, skill_path: Path) -> CategoryScore:
        """Validate reusability across variations."""
        category = CategoryScore(name="Reusability", weight=1.0)

        frontmatter, content = self._read_skill_md(skill_path)

        # Check for parameterization
        param_pattern = r"\{.*?\}|\$\{|\bparameter\b|\bvariable\b"
        has_params = bool(re.search(param_pattern, content))
        category.checks.append(ValidationResult(
            name="Parameterization",
            passed=has_params,
            message="Skills should use parameters for variations"
        ))

        # Check for templates
        template_pattern = r"##\s*Template|```yaml|template"
        has_templates = bool(re.search(template_pattern, content, re.IGNORECASE))
        category.checks.append(ValidationResult(
            name="Templates/examples",
            passed=has_templates,
            message="Skills should include templates or examples"
        ))

        return category

    def generate_report(self) -> str:
        """Generate a validation report."""
        report = []
        report.append("=" * 80)
        report.append("SKILL VALIDATION REPORT")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("=" * 80)
        report.append("")

        for result in self.results:
            report.append(f"\n{'─' * 80}")
            report.append(f"SKILL: {result.skill_path}")
            report.append(f"GRADE: {result.grade} ({result.total_score:.1f}%)")
            report.append(f"{'─' * 80}")

            for category in result.categories:
                status = "✓" if category.score == 100 else ("~" if category.score >= 70 else "✗")
                report.append(f"\n{status} {category.name}: {category.score:.0f}% ({category.passed}/{category.total})")

                for check in category.checks:
                    icon = "✓" if check.passed else "✗"
                    report.append(f"  {icon} {check.name}: {check.message}")
                    if check.details and not check.passed:
                        if isinstance(check.details, list):
                            report.append(f"      Details: {', '.join(check.details[:3])}")
                        else:
                            report.append(f"      Details: {check.details[:100]}")

        # Summary
        report.append("\n" + "=" * 80)
        report.append("SUMMARY")
        report.append("=" * 80)

        if self.results:
            avg_score = sum(r.total_score for r in self.results) / len(self.results)
            report.append(f"Average Score: {avg_score:.1f}%")

            grade_counts = {}
            for r in self.results:
                grade_counts[r.grade] = grade_counts.get(r.grade, 0) + 1

            for grade in ['A', 'B', 'C', 'D', 'F']:
                if grade in grade_counts:
                    report.append(f"Grade {grade}: {grade_counts[grade]} skills")

        return "\n".join(report)

    def to_json(self) -> str:
        """Export results as JSON."""
        results = []
        for result in self.results:
            skill_result = {
                "skill_path": result.skill_path,
                "total_score": result.total_score,
                "grade": result.grade,
                "categories": []
            }
            for category in result.categories:
                cat_result = {
                    "name": category.name,
                    "weight": category.weight,
                    "score": category.score,
                    "passed": category.passed,
                    "total": category.total,
                    "checks": [
                        {
                            "name": c.name,
                            "passed": c.passed,
                            "message": c.message
                        }
                        for c in category.checks
                    ]
                }
                skill_result["categories"].append(cat_result)
            results.append(skill_result)

        return json.dumps({
            "generated": datetime.now().isoformat(),
            "skills": results
        }, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Validate skills")
    parser.add_argument("skill_path", nargs="?", help="Validate specific skill")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--skills-dir", default="skills", help="Skills directory")

    args = parser.parse_args()

    skills_dir = Path(args.skills_dir)
    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        sys.exit(1)

    validator = SkillValidator(skills_dir)

    if args.skill_path:
        skill_path = Path(args.skill_path)
        if not skill_path.exists():
            print(f"Error: Skill path not found: {skill_path}")
            sys.exit(1)
        result = validator.validate_skill(skill_path)
        validator.results.append(result)
    else:
        validator.validate_all()

    if args.json:
        print(validator.to_json())
    elif args.report:
        print(validator.generate_report())
    else:
        # Default output
        for result in validator.results:
            print(f"{result.skill_path}: {result.grade} ({result.total_score:.1f}%)")


if __name__ == "__main__":
    main()