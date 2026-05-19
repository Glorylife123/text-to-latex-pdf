# Template Placeholders

Read this file before adapting a user template or diagnosing missing placeholder behavior.

## Supported Placeholders

- `{{TITLE}}`: Document title.
- `{{AUTHOR}}`: Author name or organization.
- `{{DATE}}`: Date string. Use `\today` when no date is provided.
- `{{ABSTRACT}}`: Abstract text.
- `{{KEYWORDS}}`: Chinese keyword list, usually separated by Chinese semicolons.
- `{{BODY}}`: Main structured content.
- `{{TABLES}}`: Generated table environments.
- `{{FIGURES}}`: Generated figure environments.
- `{{EQUATIONS}}`: Generated equation environments.
- `{{REFERENCES}}`: BibTeX commands, `thebibliography`, or a plain references section.
- `{{APPENDIX}}`: Appendix material.

## Strict Template Mode

Use strict template mode whenever `assets/templates/user_template.tex` contains meaningful content or the user supplies a template:

- Do not change `\documentclass`.
- Do not rewrite the preamble.
- Do not add duplicate packages.
- Do not remove school, journal, lab, or course formatting.
- Fill placeholders only.
- Keep template support files in `assets/templates/user_template_files/`; scripts should copy them into generated projects when the user template is selected.
- If no placeholders exist, insert generated body content immediately after `\begin{document}` or before `\end{document}` according to the template structure.
- Repair the preamble only when compilation fails and the smallest safe fix is clear.

## Missing Placeholders

If a template lacks one or more placeholders:

1. Fill the placeholders that exist.
2. Merge missing content into `{{BODY}}` if that placeholder exists.
3. If no placeholders exist, insert a complete title block and generated body inside `document`.
4. If no `document` environment exists, treat the template as a fragment and append the generated body after it.

## Placeholder Content Rules

- Placeholder values should already be valid LaTeX.
- Escape plain text before replacement.
- Keep bibliography commands in `{{REFERENCES}}`.
- Keep generated tables and figures out of `{{BODY}}` when the template has dedicated placeholders.
