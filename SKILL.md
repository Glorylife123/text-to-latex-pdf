---
name: text-to-latex-pdf
description: Convert plain text, Markdown, academic notes, thesis sections, research reports, SAV literature reviews, tables, formula descriptions, image captions, and reference information into Chinese academic LaTeX projects and compile PDFs when possible. Use when the user asks for text-to-LaTeX, Markdown-to-PDF, Chinese LaTeX templates, thesis or paper formatting, main.tex/PDF/Overleaf project generation, LaTeX compile-error repair, references.bib creation, or packaging a LaTeX project.
---

# Text to LaTeX PDF

Use this skill to turn unstructured or semi-structured user content into a Chinese academic LaTeX project. Prefer generating a usable project even when PDF compilation is unavailable.

## Inputs

Accept plain text, Markdown, paper paragraphs, section notes, tables, formula descriptions, image captions, reference lists, and existing `.tex` snippets. If the input is unstructured, first normalize it into a concise Markdown outline with title, abstract, sections, tables, figures, equations, and references when present.

## Workflow

1. Choose a template from `assets/templates/`.
2. Convert or clean the user content into structured Markdown.
3. Run `scripts/build_latex_project.py` to create a project directory with `main.tex`, `figures/`, optional `references.bib`, and `README_compile.md`.
4. Run `scripts/validate_latex.py` on the project before compiling.
5. Run `scripts/compile_latex.py` to attempt `output.pdf`.
6. If compilation fails, inspect `compile_log_summary.txt`, apply the smallest fix, validate again, and retry when reasonable.
7. Zip the project as `latex_project.zip`.

## Template Policy

- Always use `assets/templates/user_template.tex` first when it contains meaningful content, even if another template is requested.
- Treat user templates as strict template mode: preserve `documentclass`, preamble, margins, fonts, title style, figure/table style, and reference style unless compilation fails.
- Copy any supporting files under `assets/templates/user_template_files/` into the generated LaTeX project when `user_template.tex` is selected.
- Use `thesis_section.tex` for master's thesis subsections, thesis chapters, course thesis sections, and dissertation-style writing.
- Use `research_report.tex` for course papers, research reports, surveys, mathematical modeling papers, weekly reports, and SAV literature reading reports.
- Use `chinese_article.tex` for general Chinese academic articles and short papers.

When a user template is used, fill existing placeholders or insert into existing structures. Do not force abstract or keyword blocks into a template that lacks those structures unless the user's input contains abstract or keywords. Repair the preamble only when compilation fails and only with the minimum necessary change.

## Placeholders

Supported placeholders are `{{TITLE}}`, `{{AUTHOR}}`, `{{DATE}}`, `{{ABSTRACT}}`, `{{KEYWORDS}}`, `{{BODY}}`, `{{TABLES}}`, `{{FIGURES}}`, `{{EQUATIONS}}`, `{{REFERENCES}}`, and `{{APPENDIX}}`.

Read `references/template_placeholders.md` before adapting a user template or diagnosing missing placeholder behavior.

## LaTeX Rules

Default to XeLaTeX, `ctexart`, A4 paper, 2.5 cm margins, and 1.5 line spacing. Use `booktabs` tables without vertical rules. Use `tabularx` or `resizebox` for wide tables and `longtable` for long tables. Put figures in `figures/`; if only a caption exists, create a visible placeholder box.

Use `\( ... \)` for inline math and `equation` or `align` for displayed formulas. Escape text-mode special characters such as `%`, `&`, `_`, `#`, and `$`. Do not invent DOI, volume, issue, pages, PMID, or other bibliographic facts.

Read `references/latex_style_rules.md` when producing or repairing substantial LaTeX content.

## Compilation And Repair

Compile with `latexmk -xelatex -interaction=nonstopmode main.tex` when available. If `latexmk` is unavailable, run `xelatex` twice. Use BibTeX or Biber only when the project uses a `.bib` file. If no TeX engine exists, still generate `main.tex`, optional `references.bib`, `README_compile.md`, validation output, and `latex_project.zip`.

Read `references/troubleshooting_latex.md` when compilation fails or the user asks to fix LaTeX errors.

## Output Files

Produce these files when applicable:

- `main.tex`
- `references.bib`
- `figures/`
- `README_compile.md`
- `validation_report.txt`
- `output.pdf`
- `compile_log_summary.txt` when compilation fails
- `latex_project.zip`

Keep final responses concise: state where the project was created, whether PDF compilation succeeded, and what to inspect if it failed.
