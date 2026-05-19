# Text to LaTeX PDF

一个 Claude Code Skill，将纯文本、Markdown、学术笔记、论文段落、研究报告等转换为中文学术 LaTeX 项目，并在可用时编译生成 PDF。

## 功能特性

- **智能转换**：自动解析 Markdown 标题、摘要、关键词、正文、表格、公式、图片说明和参考文献
- **多模板支持**：内置通用学术论文、毕业论文章节、研究报告三种模板，支持用户自定义模板
- **自动编排**：生成完整的 LaTeX 项目结构，包括 `main.tex`、`references.bib`、`figures/` 目录等
- **编译验证**：自动检测 LaTeX 环境并尝试编译 PDF，失败时生成错误摘要
- **格式规范**：默认 XeLaTeX + ctexart，A4 纸张，2.5cm 页边距，1.5 倍行距，booktabs 三线表

## 项目结构

```
text-to-latex-pdf/
├── SKILL.md                          # Skill 定义文件
├── assets/
│   └── templates/
│       ├── chinese_article.tex       # 通用中文学术论文模板
│       ├── thesis_section.tex        # 毕业论文章节模板
│       ├── research_report.tex       # 研究报告模板
│       └── user_template.tex         # 用户自定义模板（留空则使用内置模板）
├── examples/
│   ├── report_input.md               # 研究报告示例输入
│   ├── thesis_section_input.md       # 论文章节示例输入
│   └── user_template_input.md        # 自定义模板示例输入
├── references/
│   ├── latex_style_rules.md          # LaTeX 排版规范参考
│   ├── template_placeholders.md      # 模板占位符说明
│   └── troubleshooting_latex.md      # LaTeX 常见问题排查指南
├── scripts/
│   ├── build_latex_project.py        # 构建 LaTeX 项目主脚本
│   ├── compile_latex.py              # LaTeX 编译脚本
│   └── validate_latex.py             # LaTeX 项目验证脚本
└── README.md
```

## 使用方式

### 作为 Claude Code Skill 使用

在 Claude Code 中直接描述需求即可触发：

```
将以下文本转换为 LaTeX 项目...
帮我把这篇笔记排版成毕业论文格式...
把这个研究报告转成 PDF...
```

### 独立使用脚本

**构建项目：**

```bash
python scripts/build_latex_project.py input.md -o output_dir -t chinese_article
```

参数说明：
- `input.md`：输入的 Markdown 或文本文件
- `-o, --output`：输出目录（默认 `latex_project`）
- `-t, --template`：模板选择，可选 `chinese_article`、`thesis_section`、`research_report`

**验证项目：**

```bash
python scripts/validate_latex.py output_dir
```

**编译 PDF：**

```bash
python scripts/compile_latex.py output_dir
```

## 模板说明

| 模板 | 适用场景 |
|------|---------|
| `chinese_article.tex` | 通用中文学术论文、短篇论文 |
| `thesis_section.tex` | 硕士毕业论文、课程论文、学位论文 |
| `research_report.tex` | 研究报告、课程作业、数学建模论文、周报 |

### 自定义模板

将你的 `.tex` 文件放入 `assets/templates/user_template.tex`，系统会优先使用自定义模板。支持以下占位符：

`{{TITLE}}` `{{AUTHOR}}` `{{DATE}}` `{{ABSTRACT}}` `{{KEYWORDS}}` `{{BODY}}` `{{TABLES}}` `{{FIGURES}}` `{{EQUATIONS}}` `{{REFERENCES}}` `{{APPENDIX}}`

详见 `references/template_placeholders.md`。

## 输入方式

支持两种输入方式：

### 1. 直接提供文本

将已有的笔记、文稿、Markdown 文件等直接交给 Skill，它会自动解析并转换为 LaTeX 项目。

### 2. 提供提示词，由 AI 生成内容

不需要准备完整的文本，只需描述你的需求，AI 会先根据提示词撰写内容，再执行后续的 LaTeX 转换和编译流程。例如：

```
帮我写一篇关于深度学习在医学影像中应用的研究报告，要求包含摘要、三个主要章节、一个数据对比表格和参考文献，生成 PDF。
```

```
写一个毕业论文的"相关理论与技术"章节，内容涵盖卷积神经网络和 Transformer，约 3000 字。
```

### Markdown 约定

如果直接提供文本，建议遵循以下结构以便自动识别：

```markdown
# 文档标题

作者：张三
摘要：本文研究了...
关键词：关键词1；关键词2

## 第一节

正文内容...

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据 | 数据 | 数据 |

图1：图片说明

公式：y 等于 x 的平方

## 参考文献

- 张三. 论文标题. 期刊名, 2024.
```

## 环境要求

- Python 3.10+
- XeLaTeX（编译 PDF 需要，如 TeX Live 或 MiKTeX）
- 可选：`latexmk`、`bibtex`/`biber`

如果没有安装 TeX 环境，脚本仍会生成完整的 LaTeX 项目文件，可上传至 [Overleaf](https://www.overleaf.com) 在线编译。

## License

MIT
