#!/usr/bin/env python3
"""Build a Chinese academic LaTeX project from plain text or Markdown."""

from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path


PLACEHOLDERS = [
    "TITLE",
    "AUTHOR",
    "DATE",
    "ABSTRACT",
    "KEYWORDS",
    "BODY",
    "TABLES",
    "FIGURES",
    "EQUATIONS",
    "REFERENCES",
    "APPENDIX",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def escape_latex(text: str) -> str:
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    result = text
    for old, new in replacements:
        result = result.replace(old, new)
    return result


def escape_text_preserving_math(text: str) -> str:
    parts = re.split(r"(\$[^$]+\$|\\\(.+?\\\)|\\\[.+?\\\])", text)
    output = []
    for part in parts:
        if not part:
            continue
        if part.startswith("$") and part.endswith("$"):
            output.append(r"\(" + part[1:-1].strip() + r"\)")
        elif part.startswith(r"\(") or part.startswith(r"\["):
            output.append(part)
        else:
            output.append(escape_latex(part))
    return "".join(output)


def slugify_label(text: str, prefix: str) -> str:
    ascii_text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return f"{prefix}:{ascii_text or prefix}"


def parse_metadata(markdown: str) -> dict[str, str]:
    title = "中文学术文档"
    author = ""
    abstract = "本文根据用户提供的文本自动整理生成。"
    keywords = "中文学术写作；LaTeX；自动排版"
    date = r"\today"

    lines = markdown.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            break

    patterns = {
        "author": r"^(作者|Author)[:：]\s*(.+)$",
        "abstract": r"^(摘要|Abstract)[:：]\s*(.+)$",
        "keywords": r"^(关键词|关键字|Keywords)[:：]\s*(.+)$",
        "date": r"^(日期|Date)[:：]\s*(.+)$",
    }
    for line in lines:
        stripped = line.strip()
        for key, pattern in patterns.items():
            match = re.match(pattern, stripped, flags=re.IGNORECASE)
            if match:
                value = match.group(2).strip()
                if key == "author":
                    author = value
                elif key == "abstract":
                    abstract = value
                elif key == "keywords":
                    keywords = value
                elif key == "date":
                    date = value

    return {
        "TITLE": escape_text_preserving_math(title),
        "AUTHOR": escape_text_preserving_math(author),
        "DATE": escape_text_preserving_math(date) if date != r"\today" else date,
        "ABSTRACT": escape_text_preserving_math(abstract),
        "KEYWORDS": escape_text_preserving_math(keywords),
    }


def is_table_block(lines: list[str], index: int) -> bool:
    return (
        index + 1 < len(lines)
        and "|" in lines[index]
        and re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", lines[index + 1])
        is not None
    )


def split_table_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def markdown_table_to_latex(table_lines: list[str], caption: str, number: int) -> str:
    rows = [split_table_row(line) for line in table_lines if "|" in line]
    if len(rows) < 2:
        return ""
    header = rows[0]
    body = rows[2:]
    col_count = len(header)
    column_spec = "l" * col_count
    out = [
        r"\begin{table}[H]",
        r"\centering",
        rf"\caption{{{escape_text_preserving_math(caption)}}}",
        rf"\label{{tab:auto-{number}}}",
    ]
    if col_count > 4:
        out.append(r"\resizebox{\textwidth}{!}{%")
    out.extend([
        rf"\begin{{tabular}}{{{column_spec}}}",
        r"\toprule",
        " & ".join(escape_text_preserving_math(cell) for cell in header) + r" \\",
        r"\midrule",
    ])
    for row in body:
        padded = (row + [""] * col_count)[:col_count]
        out.append(" & ".join(escape_text_preserving_math(cell) for cell in padded) + r" \\")
    out.extend([r"\bottomrule", r"\end{tabular}"])
    if col_count > 4:
        out.append("}")
    out.append(r"\end{table}")
    return "\n".join(out)


def formula_description_to_latex(text: str, number: int) -> str:
    raw = text.strip()
    content = raw.split("：", 1)[-1].split(":", 1)[-1].strip()
    replacements = {
        " 等于 ": " = ",
        "等于": " = ",
        " 除以 ": " / ",
        "除以": " / ",
        " 乘以 ": r" \times ",
        "乘以": r" \times ",
        " 减去 ": " - ",
        "减去": " - ",
        " 加上 ": " + ",
        "加上": " + ",
        " 转置": r"^{T}",
        "sqrt": r"\sqrt",
    }
    expr = content
    for old, new in replacements.items():
        expr = expr.replace(old, new)
    expr = re.sub(r"\bsqrt\(([^)]+)\)", r"\\sqrt{\1}", expr)
    expr = expr.rstrip("。.;；")
    if "=" not in expr:
        expr = r"\text{" + escape_latex(content) + "}"
    else:
        left, right = expr.split("=", 1)
        left_tokens = re.findall(r"[A-Za-z][A-Za-z0-9_]*", left)
        if left_tokens:
            left = left_tokens[-1]
        expr = normalize_math_identifiers(left.strip()) + " = " + normalize_math_identifiers(right.strip())
        frac_match = re.match(r"^(.+?)\s*/\s*(.+)$", expr.split("=", 1)[1].strip())
        if frac_match:
            expr = expr.split("=", 1)[0].strip() + " = " + rf"\frac{{{frac_match.group(1).strip()}}}{{{frac_match.group(2).strip()}}}"
    return "\n".join(
        [
            r"\begin{equation}",
            rf"\label{{eq:auto-{number}}}",
            expr,
            r"\end{equation}",
        ]
    )


def normalize_math_identifiers(expr: str) -> str:
    def repl(match: re.Match[str]) -> str:
        name = match.group(0)
        if "_" not in name:
            return name
        base, sub = name.split("_", 1)
        return rf"{base}_{{\mathrm{{{sub}}}}}"

    return re.sub(r"\b[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+\b", repl, expr)


def figure_placeholder(caption: str, number: int) -> str:
    escaped = escape_text_preserving_math(caption)
    return "\n".join(
        [
            r"\begin{figure}[H]",
            r"\centering",
            r"\fbox{\parbox[c][5cm][c]{0.82\textwidth}{\centering 图像占位：请将对应图片文件放入 figures/ 文件夹后替换此占位框。}}",
            rf"\caption{{{escaped}}}",
            rf"\label{{fig:auto-{number}}}",
            r"\end{figure}",
        ]
    )


def convert_markdown(markdown: str) -> dict[str, str]:
    lines = markdown.splitlines()
    body: list[str] = []
    tables: list[str] = []
    figures: list[str] = []
    equations: list[str] = []
    references_raw: list[str] = []
    in_references = False
    table_number = 1
    figure_number = 1
    equation_number = 1
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("# "):
            i += 1
            continue
        if re.match(r"^(作者|Author|摘要|Abstract|关键词|关键字|Keywords|日期|Date)[:：]", stripped, re.I):
            i += 1
            continue
        if re.match(r"^#{2,6}\s+", stripped):
            heading = re.sub(r"^#{2,6}\s+", "", stripped)
            if any(key in heading for key in ["参考文献", "References", "文献信息"]):
                in_references = True
                i += 1
                continue
            in_references = False
            level = min(stripped.count("#"), 4)
            command = {2: "section", 3: "subsection", 4: "subsubsection"}.get(level, "paragraph")
            body.append(rf"\{command}{{{escape_text_preserving_math(heading)}}}")
            i += 1
            continue
        if in_references:
            if stripped:
                references_raw.append(stripped.lstrip("-*0123456789. "))
            i += 1
            continue
        if is_table_block(lines, i):
            table_lines = []
            while i < len(lines) and "|" in lines[i].strip():
                table_lines.append(lines[i])
                i += 1
            tables.append(markdown_table_to_latex(table_lines, f"自动生成表格 {table_number}", table_number))
            table_number += 1
            continue
        if stripped.startswith("|") and "|" in stripped:
            i += 1
            continue
        if re.match(r"^(图\s*\d*|图片说明|Figure)\s*[:：]", stripped, re.I):
            caption = re.split(r"[:：]", stripped, maxsplit=1)[-1].strip()
            figures.append(figure_placeholder(caption, figure_number))
            figure_number += 1
            i += 1
            continue
        if re.match(r"^(公式|公式说明|Equation)\s*[:：]", stripped, re.I):
            equations.append(formula_description_to_latex(stripped, equation_number))
            equation_number += 1
            i += 1
            continue
        if stripped.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:])
                i += 1
            body.append(r"\begin{itemize}")
            body.extend(rf"\item {escape_text_preserving_math(item)}" for item in items)
            body.append(r"\end{itemize}")
            continue
        if stripped:
            body.append(escape_text_preserving_math(stripped) + "\n")
        i += 1

    return {
        "BODY": "\n".join(body).strip() or "此处为根据用户输入整理生成的正文内容。",
        "TABLES": "\n\n".join(filter(None, tables)),
        "FIGURES": "\n\n".join(figures),
        "EQUATIONS": "\n\n".join(equations),
        "REFERENCES_RAW": "\n".join(references_raw),
        "APPENDIX": "",
    }


def make_references(references_raw: str) -> tuple[str, str]:
    entries = [line.strip() for line in references_raw.splitlines() if line.strip()]
    if not entries:
        return "", ""
    bib_entries = []
    plain_items = []
    for idx, entry in enumerate(entries, 1):
        if re.search(r"\b(19|20)\d{2}\b", entry) and "." in entry:
            key = f"ref{idx}"
            year_match = re.search(r"\b((?:19|20)\d{2})\b", entry)
            year = year_match.group(1) if year_match else ""
            title = entry
            author = ""
            parts = [part.strip() for part in entry.split(".") if part.strip()]
            if len(parts) >= 2:
                author = parts[0]
                title = parts[1]
            fields = [f"  title = {{{escape_latex(title)}}}"]
            if author:
                fields.append(f"  author = {{{escape_latex(author)}}}")
            if year:
                fields.append(f"  year = {{{year}}}")
            bib_entries.append("@misc{" + key + ",\n" + ",\n".join(fields) + "\n}")
        else:
            plain_items.append(entry)
    if bib_entries and not plain_items:
        refs_tex = "\n".join([r"\bibliographystyle{plain}", r"\bibliography{references}"])
        return refs_tex, "\n\n".join(bib_entries) + "\n"
    items = bib_entries_to_plain(bib_entries) + plain_items
    refs_tex = [r"\begin{thebibliography}{99}"]
    for idx, item in enumerate(items, 1):
        refs_tex.append(rf"\bibitem{{ref{idx}}} {escape_text_preserving_math(item)}")
    refs_tex.append(r"\end{thebibliography}")
    return "\n".join(refs_tex), ""


def make_bibitems(references_raw: str) -> str:
    entries = [line.strip() for line in references_raw.splitlines() if line.strip()]
    if not entries:
        return r"\bibitem[1]{ref1} 参考文献信息待补充。"
    return "\n".join(
        rf"\bibitem[{idx}]{{ref{idx}}} {escape_text_preserving_math(entry)}"
        for idx, entry in enumerate(entries, 1)
    )


def bib_entries_to_plain(entries: list[str]) -> list[str]:
    plain = []
    for entry in entries:
        title = re.search(r"title = \{(.+?)\}", entry)
        author = re.search(r"author = \{(.+?)\}", entry)
        year = re.search(r"year = \{(.+?)\}", entry)
        pieces = []
        if author:
            pieces.append(author.group(1))
        if title:
            pieces.append(title.group(1))
        if year:
            pieces.append(year.group(1))
        plain.append(". ".join(pieces))
    return plain


def template_has_real_content(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    meaningful = [
        line
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("%") and "{{" not in line
    ]
    return bool(meaningful)


def choose_template(skill_dir: Path, requested: str | None) -> Path:
    templates = skill_dir / "assets" / "templates"
    user_template = templates / "user_template.tex"
    if template_has_real_content(user_template):
        return user_template
    name = requested or "chinese_article"
    mapping = {
        "article": "chinese_article.tex",
        "chinese_article": "chinese_article.tex",
        "thesis": "thesis_section.tex",
        "thesis_section": "thesis_section.tex",
        "report": "research_report.tex",
        "research_report": "research_report.tex",
    }
    return templates / mapping.get(name, "chinese_article.tex")


def is_user_template(template_path: Path) -> bool:
    return template_path.name == "user_template.tex"


def template_placeholders(template: str) -> set[str]:
    return {key for key in PLACEHOLDERS if "{{" + key + "}}" in template}


def prepare_values_for_template(template: str, values: dict[str, str]) -> dict[str, str]:
    prepared = dict(values)
    placeholders = template_placeholders(template)
    body_parts = [prepared.get("BODY", "")]
    for key in ["TABLES", "FIGURES", "EQUATIONS"]:
        if key not in placeholders and prepared.get(key):
            body_parts.append(prepared[key])
    prepared["BODY"] = "\n\n".join(part for part in body_parts if part).strip()
    if "REFERENCES" in placeholders:
        has_bibliography_shell = (
            r"\begin{thebibliography}" in template
            and r"\end{thebibliography}" in template
            and "{{REFERENCES}}" in template
        )
        if has_bibliography_shell:
            prepared["REFERENCES"] = prepared.get("BIBITEMS", "") or r"\bibitem[1]{ref1} 参考文献信息待补充。"
    return prepared


def apply_template(template: str, values: dict[str, str]) -> str:
    result = template
    found = False
    for key in PLACEHOLDERS:
        token = "{{" + key + "}}"
        if token in result:
            found = True
            result = result.replace(token, values.get(key, ""))
    if found:
        return result

    body = "\n\n".join(
        part
        for part in [
            rf"\title{{{values['TITLE']}}}",
            rf"\author{{{values['AUTHOR']}}}",
            rf"\date{{{values['DATE']}}}",
            r"\maketitle",
            r"\begin{abstract}" + "\n" + values["ABSTRACT"] + "\n" + r"\end{abstract}",
            rf"\noindent\textbf{{关键词：}} {values['KEYWORDS']}",
            values["BODY"],
            values["TABLES"],
            values["FIGURES"],
            values["EQUATIONS"],
            values["REFERENCES"],
            values["APPENDIX"],
        ]
        if part
    )
    begin = re.search(r"\\begin\{document\}", result)
    end = re.search(r"\\end\{document\}", result)
    if begin and end and begin.end() <= end.start():
        return result[: begin.end()] + "\n" + body + "\n" + result[end.start() :]
    return result + "\n\n" + body + "\n"


def write_readme(project_dir: Path, engine_note: str = "") -> None:
    readme = f"""# Compile Instructions

This project was generated for XeLaTeX.

## Local compile

```bash
latexmk -xelatex -interaction=nonstopmode main.tex
```

If `latexmk` is unavailable:

```bash
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

If `references.bib` is present and citations are used, run BibTeX or Biber between XeLaTeX passes as required by the template.

## Overleaf

Upload all files in this directory, set the compiler to XeLaTeX, and compile `main.tex`.

{engine_note}
"""
    (project_dir / "README_compile.md").write_text(readme, encoding="utf-8")


def copy_user_template_files(skill_dir: Path, output_dir: Path) -> None:
    files_dir = skill_dir / "assets" / "templates" / "user_template_files"
    if not files_dir.exists():
        return
    for source in files_dir.iterdir():
        target = output_dir / source.name
        if source.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def zip_project(project_dir: Path) -> Path:
    zip_path = project_dir / "latex_project.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in project_dir.rglob("*"):
            if path == zip_path:
                continue
            archive.write(path, path.relative_to(project_dir))
    return zip_path


def build_project(input_path: Path, output_dir: Path, template_name: str | None, skill_dir: Path) -> Path:
    markdown = read_text(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "figures").mkdir(exist_ok=True)

    metadata = parse_metadata(markdown)
    converted = convert_markdown(markdown)
    references_raw = converted.pop("REFERENCES_RAW")
    refs_tex, bib = make_references(references_raw)
    values = {**metadata, **converted, "REFERENCES": refs_tex, "BIBITEMS": make_bibitems(references_raw)}

    template_path = choose_template(skill_dir, template_name)
    template = template_path.read_text(encoding="utf-8")
    values = prepare_values_for_template(template, values)
    main_tex = apply_template(template, values)
    (output_dir / "main.tex").write_text(main_tex, encoding="utf-8")
    if is_user_template(template_path):
        copy_user_template_files(skill_dir, output_dir)
    if bib:
        (output_dir / "references.bib").write_text(bib, encoding="utf-8")
    write_readme(output_dir)
    zip_project(output_dir)
    return output_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Chinese academic LaTeX project.")
    parser.add_argument("input", type=Path, help="Input Markdown or text file.")
    parser.add_argument("-o", "--output", type=Path, default=Path("latex_project"), help="Output project directory.")
    parser.add_argument("-t", "--template", default=None, help="Template: chinese_article, thesis_section, research_report.")
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).resolve().parents[1], help="Skill root directory.")
    args = parser.parse_args()

    build_project(args.input, args.output, args.template, args.skill_dir)
    print(f"Project generated at: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
