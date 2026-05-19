#!/usr/bin/env python3
"""Compile a LaTeX project with XeLaTeX when available."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import zipfile
from pathlib import Path


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def summarize_log(project_dir: Path, output: str) -> None:
    log_path = project_dir / "main.log"
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else output
    lines = log_text.splitlines()
    interesting = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("!") or any(token in stripped.lower() for token in ["error", "undefined", "missing", "not found"]):
            interesting.append(stripped)
    if not interesting:
        interesting = lines[-80:]
    summary = "\n".join(interesting[:120])
    (project_dir / "compile_log_summary.txt").write_text(summary + "\n", encoding="utf-8")


def zip_project(project_dir: Path) -> None:
    zip_path = project_dir / "latex_project.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in project_dir.rglob("*"):
            if path == zip_path:
                continue
            archive.write(path, path.relative_to(project_dir))


def has_bib(project_dir: Path) -> bool:
    return (project_dir / "references.bib").exists()


def compile_project(project_dir: Path) -> int:
    main_tex = project_dir / "main.tex"
    if not main_tex.exists():
        (project_dir / "compile_log_summary.txt").write_text("Missing main.tex.\n", encoding="utf-8")
        return 2

    latexmk = shutil.which("latexmk")
    xelatex = shutil.which("xelatex")
    bibtex = shutil.which("bibtex")
    biber = shutil.which("biber")

    if latexmk:
        command = ["latexmk", "-xelatex", "-interaction=nonstopmode", "main.tex"]
        result = run(command, project_dir)
    elif xelatex:
        outputs = []
        first = run(["xelatex", "-interaction=nonstopmode", "main.tex"], project_dir)
        outputs.append(first.stdout)
        if has_bib(project_dir):
            if biber and (project_dir / "main.bcf").exists():
                outputs.append(run(["biber", "main"], project_dir).stdout)
            elif bibtex and (project_dir / "main.aux").exists():
                outputs.append(run(["bibtex", "main"], project_dir).stdout)
        second = run(["xelatex", "-interaction=nonstopmode", "main.tex"], project_dir)
        outputs.append(second.stdout)
        result = second
        result.stdout = "\n".join(outputs)
    else:
        message = "No latexmk or xelatex executable found. Generated LaTeX project only; compile with XeLaTeX locally or on Overleaf.\n"
        (project_dir / "compile_log_summary.txt").write_text(message, encoding="utf-8")
        zip_project(project_dir)
        print(message.strip())
        return 3

    pdf = project_dir / "main.pdf"
    output_pdf = project_dir / "output.pdf"
    if result.returncode == 0 and pdf.exists():
        if output_pdf.exists():
            output_pdf.unlink()
        pdf.rename(output_pdf)
        zip_project(project_dir)
        print(f"Compiled PDF: {output_pdf.resolve()}")
        return 0

    summarize_log(project_dir, result.stdout)
    zip_project(project_dir)
    print(f"Compilation failed. See {(project_dir / 'compile_log_summary.txt').resolve()}")
    return result.returncode or 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile a LaTeX project with XeLaTeX.")
    parser.add_argument("project", type=Path, nargs="?", default=Path("."), help="Project directory containing main.tex.")
    args = parser.parse_args()
    return compile_project(args.project)


if __name__ == "__main__":
    raise SystemExit(main())
