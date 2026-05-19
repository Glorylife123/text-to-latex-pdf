# LaTeX Style Rules

Use this reference when generating or repairing substantial Chinese academic LaTeX.

## Defaults

- Engine: XeLaTeX.
- Document class: `ctexart` unless the user supplies a template.
- Page: A4, 2.5 cm margins.
- Line spacing: 1.5.
- Encoding: UTF-8.
- Output language: Chinese by default, preserving user-provided English terms.

## Text Conversion

- Convert unstructured text to sections before LaTeX generation.
- Escape text-mode special characters: `\`, `%`, `&`, `_`, `#`, `$`, `{`, `}`, `~`, `^`.
- Do not escape characters already inside clear LaTeX commands or math environments.
- Preserve domain terms, variable names, and citations.

## Sections

- Use `\section`, `\subsection`, and `\subsubsection`.
- Avoid over-fragmented headings for short reports.
- For thesis sections, prefer a sober structure: background, method, analysis, discussion, summary.
- For SAV literature reviews, use bibliographic information, research question, method, argument, evidence, limitations, and reflection.

## Tables

- Use `booktabs` with `\toprule`, `\midrule`, and `\bottomrule`.
- Do not use vertical rules.
- Use `tabularx` when the table should fill text width.
- Use `\resizebox{\textwidth}{!}{...}` only for wide tables that cannot be reasonably wrapped.
- Use `longtable` for long multi-page tables.
- Keep column counts consistent across rows.
- Escape text content in cells unless it is intentionally LaTeX.

## Figures

- Put images under `figures/`.
- Use `figure` with `\centering`, `\includegraphics`, `\caption`, and `\label`.
- If the user provides only a caption, create a placeholder box with `\fbox{\parbox{...}{...}}`.
- Do not invent image filenames; use provided files when available.

## Math

- Inline math uses `\( ... \)`.
- Display math uses `equation` for one equation and `align` for aligned multi-line derivations.
- Check paired delimiters and environment closure.
- Avoid placing Chinese punctuation inside math unless intentional.

## References

- Generate `references.bib` only when enough structured bibliographic information exists.
- Do not invent DOI, PMID, volume, issue, page range, publisher, venue, or URL.
- If information is incomplete, use a plain `thebibliography` list or a simple references section.
- Keep citation keys stable, ASCII-only, and descriptive.
