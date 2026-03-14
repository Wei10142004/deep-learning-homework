@echo off
chcp 65001 >nul
echo 正在将 Markdown 报告导出为 PDF（通过 LaTeX）...
echo.

set MD=function_fitting_report_20250314.md
set PDF=function_fitting_report_20250314.pdf

where pandoc >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 pandoc。请先安装: https://pandoc.org/installing.html
    exit /b 1
)

pandoc "%MD%" -o "%PDF%" ^
  --pdf-engine=xelatex ^
  -V CJKmainfont="SimSun" ^
  -V geometry:margin=2.5cm ^
  -V fontsize=11pt ^
  -V documentclass=article

if %errorlevel% equ 0 (
    echo.
    echo 导出成功: %PDF%
) else (
    echo.
    echo 导出失败。若报错与中文或字体相关，可尝试将 CJKmainfont 改为 Microsoft YaHei 或安装 TeX Live 的 ctex 支持。
)
pause
