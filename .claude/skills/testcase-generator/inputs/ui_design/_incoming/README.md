# 待归类 UI 图片

本目录用于临时存放产品提供但尚未确认归属需求的 UI 图片。

使用规则：

- UI 图片必须先放在 `inputs/ui_design/` 下，不从 `docx/` 目录读取。
- 若图片文件名包含需求编号，例如 `REQ-CPV-039_list.png`，脚本可尝试自动匹配。
- 无法自动匹配的图片会记录到 `inputs/ui_design/_unassigned/README.md`。
- 人工确认后，将图片移动到对应 `inputs/ui_design/REQ-CPV-xxx/` 目录，并更新该目录的 `README.md`。
