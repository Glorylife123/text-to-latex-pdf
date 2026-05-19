# Troubleshooting LaTeX

Use this reference when compilation fails or the user asks to fix LaTeX errors.

## Common Failures

- `Undefined control sequence`: missing package, misspelled command, or non-LaTeX Markdown syntax left in `main.tex`.
- `Missing $ inserted`: math content outside math delimiters or unescaped `_`.
- `Misplaced alignment tab character &`: unescaped `&` in text or inconsistent table columns.
- `File ... not found`: missing image, wrong relative path, or missing `.bib`.
- `Environment ... undefined`: missing package such as `amsmath`, `longtable`, or `tabularx`.
- `Unicode character ... not set up`: compile with XeLaTeX rather than pdfLaTeX.
- `Citation ... undefined`: BibTeX/Biber not run or citation key mismatch.

## Repair Order

1. Read the first meaningful error in the log, not only the last line.
2. Fix escaping and unclosed environments before changing packages.
3. Check table row column counts.
4. Check image paths relative to `main.tex`.
5. Check duplicate labels and citation keys.
6. Re-run validation before recompilation.

## Minimal Fix Policy

- Preserve user templates and institutional formatting.
- Do not replace the document class unless the user permits it.
- Do not remove content to make compilation pass unless the content is clearly malformed and preserved elsewhere.
- Prefer local fixes around the failing line.

## No TeX Environment

If `latexmk` and `xelatex` are unavailable:

- Do not treat this as project failure.
- Generate `README_compile.md` with local and Overleaf instructions.
- Zip the project.
- Tell the user that PDF compilation was skipped because no TeX engine was found.
