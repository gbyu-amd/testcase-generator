# 历史 PRD 归档

本目录用于保存已经处理过或暂时不用的原始 PRD。

建议命名：

- `PM-A_YYYYMMDD.docx`
- `PM-B_YYYYMMDD.docx`
- `CPV产品规格说明书_汇总版_YYYYMMDD.docx`

什么时候需要归档：

- 不关心追溯：不用归档，直接保留最新 Word 文件。
- 已经用这份 PRD 生成正式用例：建议归档。
- PRD 来自不同 PM 或版本经常变化：更建议归档。

使用规则：

- 日常生成用例直接读取 `inputs/requirements/raw_docs/` 下的原始 Word。
- 更换 PRD 前，按需把旧 Word 文件移动或复制到本目录归档。
- 归档文件只作追溯，不直接作为默认生成入口；如需基于归档文件生成，应在对话中显式指定文件路径。
