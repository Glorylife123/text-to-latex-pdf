#!/usr/bin/env python3
"""Validate common LaTeX project issues and write validation_report.txt."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path


TEXT_SPECIAL_PATTERN = re.compile(r"(?<!\\)[%&#_]")


def strip_comments(line: str) -> str:
    escaped = False
    for index, char in enumerate(line):
        if char == "\\" and not escaped:
            escaped = True
            continue
        if char == "%" and not escaped:
            return line[:index]
        escaped = False
    return line


def strip_math_and_commands(line: str) -> str:
    line = re.sub(r"\\\(.+?\\\)", "", line)
    line = re.sub(r"\$[^$]+\$", "", line)
    line = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", "", line)
    return line


def check_special_chars(tex: str) -> list[str]:
    issues = []
    math_depth = 0
    table_depth = 0
    for number, line in enumerate(tex.splitlines(), 1):
        line = strip_comments(line)
        stripped = line.lstrip()
        if not stripped:
            continue
        begin_match = re.search(r"\\begin\{([^}]+)\}", line)
        end_match = re.search(r"\\end\{([^}]+)\}", line)
        if begin_match and begin_match.group(1) in {"equation", "align", "gather", "multline"}:
            math_depth += 1
        if begin_match and begin_match.group(1) in {"tabular", "tabularx", "longtable"}:
            table_depth += 1
        macro_definition = re.search(r"\\(?:re)?newcommand|\\(?:re)?newenvironment|\\def|\\renewcommand", stripped)
        skip_line = macro_definition is not None or math_depth > 0 or table_depth > 0
        if end_match and end_match.group(1) in {"equation", "align", "gather", "multline"}:
            math_depth = max(0, math_depth - 1)
        if end_match and end_match.group(1) in {"tabular", "tabularx", "longtable"}:
            table_depth = max(0, table_depth - 1)
        if skip_line:
            continue
        text = strip_math_and_commands(line)
        match = TEXT_SPECIAL_PATTERN.search(text)
        if match:
            issues.append(f"Line {number}: possible unescaped special character `{match.group(0)}`.")
    return issues


def check_environment_balance(tex: str) -> list[str]:
    issues = []
    tex = "\n".join(strip_comments(line) for line in tex.splitlines())
    begins = re.findall(r"\\begin\{([^}]+)\}", tex)
    ends = re.findall(r"\\end\{([^}]+)\}", tex)
    begin_counts = Counter(begins)
    end_counts = Counter(ends)
    for env in sorted(set(begin_counts) | set(end_counts)):
        if begin_counts[env] != end_counts[env]:
            issues.append(f"Environment `{env}` begin/end mismatch: {begin_counts[env]} begin, {end_counts[env]} end.")
    display_open = len(re.findall(r"(?<!\\)\\\[(?![-0-9.]+\w*\])", tex))
    display_close = len(re.findall(r"(?<!\\)\\\]", tex))
    if tex.count(r"\(") != tex.count(r"\)"):
        issues.append("Inline math delimiters \\( and \\) are not balanced.")
    if display_open != display_close:
        issues.append("Display math delimiters \\[ and \\] are not balanced.")
    return issues


def check_table_columns(tex: str) -> list[str]:
    issues = []
    table_blocks = re.findall(r"\\begin\{tabularx?\}.*?\\end\{tabularx?\}", tex, flags=re.S)
    table_blocks += re.findall(r"\\begin\{longtable\}.*?\\end\{longtable\}", tex, flags=re.S)
    for idx, block in enumerate(table_blocks, 1):
        rows = [row.strip() for row in block.split(r"\\") if "&" in row]
        counts = [row.count("&") for row in rows if not row.lstrip().startswith("%")]
        if counts and len(set(counts)) > 1:
            issues.append(f"Table {idx}: inconsistent number of `&` separators across rows: {counts}.")
    return issues


def check_image_paths(tex: str, project_dir: Path) -> list[str]:
    issues = []
    for image in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex):
        image_path = project_dir / image
        if not image_path.exists():
            issues.append(f"Missing image file: {image}")
    return issues


def check_duplicate_labels(tex: str) -> list[str]:
    labels = re.findall(r"\\label\{([^}]+)\}", tex)
    counts = Counter(labels)
    return [f"Duplicate label `{label}` appears {count} times." for label, count in counts.items() if count > 1]


def validate(project_dir: Path) -> list[str]:
    main_tex = project_dir / "main.tex"
    if not main_tex.exists():
        return ["Missing main.tex."]
    tex = main_tex.read_text(encoding="utf-8")
    issues = []
    issues.extend(check_special_chars(tex))
    issues.extend(check_environment_balance(tex))
    issues.extend(check_table_columns(tex))
    issues.extend(check_image_paths(tex, project_dir))
    issues.extend(check_duplicate_labels(tex))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a LaTeX project.")
    parser.add_argument("project", type=Path, nargs="?", default=Path("."), help="Project directory containing main.tex.")
    args = parser.parse_args()

    issues = validate(args.project)
    report = args.project / "validation_report.txt"
    if issues:
        report.write_text("Validation issues:\n" + "\n".join(f"- {issue}" for issue in issues) + "\n", encoding="utf-8")
        print(f"Validation completed with {len(issues)} issue(s). See {report}.")
        return 1
    report.write_text("Validation passed. No common issues found.\n", encoding="utf-8")
    print(f"Validation passed. See {report}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
