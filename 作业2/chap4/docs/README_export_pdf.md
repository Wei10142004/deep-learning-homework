# 将实验报告导出为 PDF（LaTeX）

报告源文件为 Markdown：`function_fitting_report_20250314.md`。下面说明如何导出为 PDF。

---

## 方法一：用 Pandoc（推荐）

Pandoc 会把 Markdown 转成 LaTeX，再用 XeLaTeX 生成 PDF，并支持中文和公式。

### 1. 安装依赖

1. **Pandoc**  
   - 下载：<https://pandoc.org/installing.html>  
   - Windows 可用安装包或 `winget install pandoc`。

2. **LaTeX 引擎（含 XeLaTeX）**  
   - **Windows**：安装 [MiKTeX](https://miktex.org/download) 或 [TeX Live](https://www.tug.org/texlive/)。  
   - 安装后确保命令行可用 `xelatex`（一般会自动加入 PATH）。

3. **中文字体**  
   - Windows 自带宋体（SimSun）即可，无需额外安装。

### 2. 导出 PDF

在 **`docs`** 目录下打开终端（或在该目录下运行脚本），执行：

**方式 A：直接双击脚本（Windows）**

```
export_report_to_pdf.bat
```

**方式 B：命令行**

```bash
cd docs
pandoc function_fitting_report_20250314.md -o function_fitting_report_20250314.pdf ^
  --pdf-engine=xelatex ^
  -V CJKmainfont="SimSun" ^
  -V geometry:margin=2.5cm
```

（Linux/macOS 下把 `^` 换成 `\` 续行。）

生成的 PDF 与 `.md` 同目录：`function_fitting_report_20250314.pdf`。

### 3. 若中文显示异常

- 把 `SimSun` 换成系统里有的中文字体，例如：  
  `-V CJKmainfont="Microsoft YaHei"` 或 `"FangSong"`。  
- 或先安装 TeX Live 的 `ctex` 宏包（如 `tlmgr install ctex`），再重试。

---

## 方法二：先转 LaTeX 再手动编译

若希望得到 `.tex` 源文件再自己改版式：

```bash
cd docs
pandoc function_fitting_report_20250314.md -o function_fitting_report_20250314.tex --standalone
```

然后用 TeX 编辑器（如 TeXworks、VS Code + LaTeX Workshop）打开该 `.tex`，在导言区加入中文支持（如 `\usepackage{ctex}`），再用 **XeLaTeX** 编译生成 PDF。

---

## 常见问题

| 现象 | 处理 |
|------|------|
| 提示找不到 `pandoc` | 安装 Pandoc 并确认其所在目录已加入系统 PATH。 |
| 提示找不到 `xelatex` | 安装 MiKTeX 或 TeX Live，并确认已安装 XeLaTeX。 |
| 中文乱码或空白 | 使用 `-V CJKmainfont="SimSun"`（或你系统里的中文字体名），并用 `--pdf-engine=xelatex`。 |
| 公式不显示 | 确保使用 `--pdf-engine=xelatex`（或 `pdflatex`），不要用不支持数学的引擎。 |
