# 用例生成工作流规则

本文件维护 CPV 测试用例生成的执行流程，负责回答“从输入资料到 Markdown / Excel 交付物应该怎么流转”。用例字段写法、覆盖维度、优先级、难度和追加去重细节分别以本目录其他规则文件为准。

## 输入资料处理

### 当前 PRD

- `inputs/requirements/current_prd.md` 是默认当前 PRD 入口。
- 用户指定 Markdown PRD 章节时，只读取该章节及必要上下文，不默认扫描整份 PRD。
- `inputs/requirements/archive/` 仅用于历史追溯；除非用户显式指定，不主动读取归档文件。

### Word PRD

用户指定 `.docx` 或提到“根据某 Word 的某章节生成用例”时，必须先将整份 Word 转换覆盖到 `inputs/requirements/current_prd.md`：

```bash
python scripts/convert_docx.py inputs/requirements/raw_docs/<文件名>.docx --overwrite
```

随后从 `current_prd.md` 提取指定章节生成用例。不得只用 `--section --print` 临时读取后跳过落地；该参数只允许用于排查章节转换问题。

如果用户未指定章节，可先列章节：

```bash
python scripts/convert_docx.py inputs/requirements/raw_docs/<文件名>.docx --list-sections
```

确认章节后仍需执行整份覆盖转换。

### UI 设计图

UI 设计图按章节名组织在 `inputs/ui_design/<章节名>/`。生成前必须先列出 `inputs/ui_design/` 下所有子目录，再与章节名匹配，不使用 Glob 匹配中文目录名：

```bash
ls inputs/ui_design/
```

Windows PowerShell 可使用：

```powershell
Get-ChildItem inputs/ui_design/
```

目录名与章节名一致时读取其中所有图片；有实际图片则读取，不存在图片则跳过并记录资料缺失或生成假设。

## 资料读取顺序

1. `SKILL.md`
2. `generation_rules/workflow_rules.md`
3. `generation_rules/case_append_rules.md`
4. `generation_rules/testcase_writing_guidelines.md`
5. `generation_rules/coverage_dimension_rules.md`
6. `generation_rules/priority_rules.md`
7. `generation_rules/difficulty_level_rules.md`
8. 用户指定 PRD 章节和对应 UI 图
9. `testcase_templates/modules/menu_index.md` 和命中的参考用例
10. 信息不足时读取 `knowledge_base/` 和相关 `knowledge_base/core_flows/`
11. 需要异常、边界、兼容等写法时读取 `testcase_templates/common_templates/`

## 参考资料使用

- 生成前必须先读取 `testcase_templates/modules/menu_index.md`，按 CPV 菜单路径匹配参考文件。
- 参考用例只读，不得修改 `testcase_templates/`。
- 若 UI 图与 PRD 描述存在字段、数据结构或字数限制等冲突，停止生成并询问用户以哪个为准。
- 若资料缺失，可以继续生成，但必须在元信息或回复中写明缺失资料和生成假设。

## 站点分类和输出位置

| 站点分类 | Markdown 输出 | Excel 输出 | 适用范围 |
|---|---|---|---|
| 公共管理站点 | `outputs/origin_exports/public_site/` | `outputs/excel_exports/public_site/` | 统一门户、站点管理、全局用户、权限管理、系统服务管理、公共管理审计、登录日志 |
| 业务站点 | `outputs/origin_exports/business_site/` | `outputs/excel_exports/business_site/` | 产品与基础数据、年度计划与任务、方案编制、监控项目、数据分析、一键分析、报告编制、业务站点配置和异步任务 |

- 跨站点登录、站点切换、统一门户入口类用例，优先归入 `public_site`。
- 业务数据隔离、业务站点内权限和 CPV 主流程类用例，优先归入 `business_site`。
- 同一需求同时影响两个站点时，按主验证目标拆分或分别生成，避免公共管理菜单和业务站点菜单混写。

## 输出文件处理

Markdown 源文件固定保存为：

```text
outputs/origin_exports/<site_type>/<module_name>_testcases.md
```

生成前必须检查目标文件是否存在：

- 文件不存在：直接新建。
- 文件存在但为空或没有有效用例表：可覆盖初始化。
- 文件已存在且包含有效用例：停止生成，等待用户明确选择 `追加`、`覆盖` 或 `另存`。

另存文件使用：

```text
<module_name>_testcases_YYYYMMDD_HHMMSS.md
```

带时间戳的另存文件不会被脚本默认扫描；校验或导出时必须用 `--source` 显式指定。

## 元信息和覆盖率

新建或覆盖文件时，在文件顶部写入元信息块：

```markdown
<!--
生成时间：YYYY-MM-DD HH:MM
操作类型：新建 / 覆盖
来源文档：inputs/requirements/raw_docs/<文件名>.docx 或 inputs/requirements/current_prd.md
来源章节：<章节名>
输入文件：
  - <实际读取的输入文件>（最后修改：YYYY-MM-DD 或 未知）
生成假设：无 / <关键假设>
-->
```

追加模式不改已有元信息块，在文件末尾追加本次追加记录。

生成用例后必须追加“需求覆盖率对照表”：

| 需求点 / 验收标准 | 需求描述 | 覆盖用例名称 |
|---|---|---|

- 每条 PRD 需求点至少对应一条用例，核心链路需求应有 P0 用例覆盖。
- 未覆盖项必须显式列出并说明原因。

## 校验和导出闭环

生成或修改 Markdown 用例后必须执行：

```bash
python scripts/validate_cases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md
```

- 存在 `ERROR` 时，不得导出 Excel。
- `validate_cases.py --fix` 只能修复 Markdown 表格格式，不得用于绕过业务语义问题。
- 难度标签 WARN 不阻断默认导出；如果要求 Markdown 源文件 0 WARN，必须根据 WARN 明细修复源文件。

校验通过后按单文件导出分需求 Excel：

```bash
python scripts/export_testcases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md
```

单文件导出生成：

```text
outputs/excel_exports/<site_type>/<module_name>_testcases.xlsx
```

不带 `--source` 或传入目录会生成 `测试用例导出_YYYYMMDD_HHMMSS.xlsx` 汇总文件，仅适合临时汇总，不作为默认交付方式。

## 环境要求

- Python 3.10 或更高版本。
- `validate_cases.py`、`export_testcases.py` 和 `case_utils.py` 仅使用标准库。
- `convert_docx.py` 需要额外安装 `python-docx`。
