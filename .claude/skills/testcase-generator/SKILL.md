---
name: cpv-testcase-generator
description: 根据 CPV 系统的需求文档、界面设计图、业务规则和已有参考用例，生成测试用例并导出为 Excel。适用于统一门户、公共管理站点、业务站点、年度计划、任务、方案、监控项目、数据分析、一键分析、报告编制、审计追踪等 CPV 测试场景。
---

# CPV 功能测试用例生成器

## 目标

为 CPV 系统生成结构化、可执行、可校验、可导出的功能测试用例。

生成结果必须贴近 CPV 真实业务场景，不能只输出“功能正常”“页面展示正确”等空泛描述。

## 适用场景

- 根据原始 Word PRD（`.docx`）或用户直接提供的需求文本生成测试用例。
- 根据 UI 设计图补充页面展示、交互和校验用例。
- 补充、追加、覆盖或另存已有模块用例。
- 将 Markdown 用例校验并导出为分需求 Excel。

## 必读规则

生成、补充或导出用例前，按顺序读取以下文件：

1. `generation_rules/workflow_rules.md`
2. `generation_rules/testcase_writing_guidelines.md`
3. `generation_rules/coverage_dimension_rules.md`
4. `generation_rules/priority_rules.md`
5. `generation_rules/difficulty_level_rules.md`
6. `testcase_templates/modules/menu_index.md`

按需读取：

- 命中 `generation_rules/coverage_dimension_rules.md` 的专项规则路由时，必须先读取对应专项规则，再生成或补充用例。
- 涉及 Excel / CSV / 模板文件导入、批量导入、导入模板或错误报告时，读取 `generation_rules/import_coverage_rules.md`。
- 新增或补充分析方法、数据分析详情页、分析结果、替换数据源或一键分析时，读取 `generation_rules/data_analysis_coverage_rules.md`。
- 涉及审计追踪、电子签名记录、操作日志、操作前后值、详情导出或合规追溯时，读取 `generation_rules/audit_trail_coverage_rules.md`。
- `testcase_templates/modules/menu_index.md` 命中的 `*_template.md` 参考用例。
- `knowledge_base/project_overview.md`、`business_glossary.md`、`user_roles.md`。
- `knowledge_base/core_flows/` 下与当前模块相关的流程。
- `testcase_templates/common_templates/` 下的异常、边界、兼容等通用模板。

规则职责：

| 文件 | 职责 |
|---|---|
| `workflow_rules.md` | 输入处理、资料读取、输出路径、追加 / 覆盖 / 另存、去重、元信息、覆盖率、校验和导出闭环 |
| `testcase_writing_guidelines.md` | 16 列表头、字段写法、备注来源、标签和质量底线 |
| `coverage_dimension_rules.md` | 通用覆盖维度、高风险场景和专项规则路由 |
| `import_coverage_rules.md` | 文件导入、导入模板、批量导入和错误报告专项覆盖规则 |
| `data_analysis_coverage_rules.md` | 数据分析、分析方法、替换数据源和一键分析专项覆盖规则 |
| `audit_trail_coverage_rules.md` | 审计追踪、电子签名记录、操作日志、操作前后值和合规追溯专项覆盖规则 |
| `priority_rules.md` | P0 / P1 / P2 判定 |
| `difficulty_level_rules.md` | `用例标签` 中的简单 / 一般 / 困难判定 |

## 执行流程

1. 判断需求影响模块、站点分类和输出文件路径。
2. 若输入是 Word，按 `workflow_rules.md` 直接从 `.docx` 提取用户指定章节。
3. 若用户直接提供需求文本，按用户提供的文本范围提取章节及必要上下文。
4. 按章节名检查并读取 `inputs/ui_design/<章节名>/`。
5. 读取菜单索引和命中参考用例；参考用例只读，不修改。
6. 按 `coverage_dimension_rules.md` 判断是否命中导入、数据分析或审计追踪专项规则；命中时先读取专项规则并形成生成前 checklist。
7. 若输出文件已存在且包含有效用例表，必须等待用户明确选择 `追加`、`覆盖` 或 `另存`。
8. 生成或更新 Markdown 用例：新建 / 覆盖 / 另存写入元信息块、需求问题清单、用例统计摘要、标准 16 列用例表和需求覆盖率对照表；追加模式不改写历史摘要和历史覆盖率，只补充本次新增记录。
9. 运行 `validate_cases.py`；存在 ERROR 时先修复 Markdown，不导出 Excel。
10. 校验通过后按单个 Markdown 源文件导出同名 Excel。
11. 回复 Markdown 路径、Excel 路径、用例数量、覆盖模块和需求覆盖情况；追加模式需区分本次新增数量和文件合计数量。

## 关键约束

- 新生成或补充的用例只写入 `outputs/origin_exports/public_site/` 或 `outputs/origin_exports/business_site/`。
- Excel 交付默认分需求导出：`outputs/excel_exports/<site_type>/<module_name>_testcases.xlsx`。
- 不带 `--source` 或传入目录会生成合并 Excel，仅用于临时汇总，不作为默认交付方式。
- `export_testcases.py --clean` 只用于清理临时汇总 Excel，不作为删除分需求交付文件的手段。
- `testcase_templates/` 是只读参考库，不保存新生成用例。
- 不得静默覆盖已有有效用例文件。
- 不得通过删除业务场景绕过校验错误。
- 每条新用例的 `备注` 必须按 `testcase_writing_guidelines.md` 记录真实来源。
- 每条新用例的 `一级分组`、`二级分组`、`三级分组` 必须全部填写，不得留空。
- 新生成用例的 `是否自动化`、`关联接口`、`用例测试类`、`关联项目` 字段必须留空。
- 第三方软件、测试团队既有对比口径或业务确认值可作为测试判定依据时，不得仅因 PRD 未展开算法公式而写入需求问题清单。
- 命中专项规则时，需求覆盖率对照表必须包含适用默认覆盖项和不适用项的回查结果；回查项不得直接当作用例分组名。
- 直接依赖待确认需求的用例名称前加 `【待确认】`，并在需求问题清单中说明对应的用例处理方式。

## 常用命令

```bash
# 列出 Word 章节
python scripts/extract_docx.py inputs/requirements/raw_docs/<文件名>.docx --list-sections

# 从 Word 直接提取章节内容（默认推荐）
python scripts/extract_docx.py inputs/requirements/raw_docs/<文件名>.docx --section "<章节名>" --print

# 校验单个 Markdown 用例文件
python scripts/validate_cases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md

# 仅修复 Markdown 表格格式
python scripts/validate_cases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md --fix

# 分需求导出 Excel
python scripts/export_testcases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md
```

## 质量底线

- 前置条件必须可复现，写清用户、站点、权限、数据状态和必要环境。
- 步骤必须可执行，使用有序编号。
- 预期结果必须可验证，包含页面反馈、数据状态或业务状态。
- CPV 核心链路必须覆盖状态流转、权限控制、数据一致性、合规追溯和跨模块联动。
- 优先级只能使用 `P0`、`P1`、`P2`。
- `用例描述` 使用 `正例`、`反例`、`边界`、`权限`、`UI`、`兼容`、`回归`、`联动`。
- `用例标签` 只保留难度等级：`简单`、`一般` 或 `困难`。
