# 历史 PRD 归档

本目录用于保存已经处理过或暂时不用的原始 PRD。

建议命名：

- `PM-A_YYYYMMDD.md`
- `PM-B_YYYYMMDD.md`
- `CPV产品规格说明书_汇总版_YYYYMMDD.md`

什么时候需要归档：

- 不关心追溯：不用归档，直接覆盖 `current_prd.md`。
- 已经用这份 PRD 生成正式用例：建议归档。
- PRD 来自不同 PM 或版本经常变化：更建议归档。

使用规则：

- 日常生成用例只读取 `inputs/requirements/current_prd.md`。
- 更换 PRD 前，先把当前 `current_prd.md` 复制到本目录归档。
- 归档文件只作追溯，不直接作为默认生成入口；如需基于归档文件生成，应在对话中显式指定文件路径。
