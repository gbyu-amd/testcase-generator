# 用例生成工作流规则

本文件维护 CPV 测试用例生成的执行流程，负责回答“输入资料如何处理、输出文件如何确定、已有用例如何处理、交付物如何校验导出”。规则入口和必读清单以 `SKILL.md` 为准；用例字段写法、覆盖维度、优先级和难度分别以本目录其他规则文件为准。

## 输入资料处理

### Word PRD

用户指定 `.docx` 或提到“根据某 Word 的某章节生成用例”时，直接从原始 Word 提取目标章节，原始 `.docx` 是事实源：

```bash
python scripts/extract_docx.py inputs/requirements/raw_docs/<文件名>.docx --section "<章节名>" --print
```

提取到的章节内容直接用于生成用例，不生成中间需求文件。

如果用户未指定章节，可先列章节：

```bash
python scripts/extract_docx.py inputs/requirements/raw_docs/<文件名>.docx --list-sections
```

### 直接提供的需求文本

用户直接在对话或附件中提供需求文本时，按用户指定章节或文本范围读取，不默认扩展到其他历史资料。

### 历史资料

`inputs/requirements/archive/` 仅用于历史追溯；除非用户显式指定，不主动读取归档文件。

### UI 设计图

UI 设计图、页面截图或原型图按章节名组织在 `inputs/ui_design/<章节名>/`。生成前先列出 `inputs/ui_design/` 下所有子目录，再与章节名匹配，不使用 Glob 匹配中文目录名。

目录名与章节名一致时读取其中所有图片；有实际图片则读取，不存在图片则跳过并记录资料缺失或生成假设。

## 资料读取原则

- 规则文件读取顺序以 `SKILL.md` 的“必读规则”和“按需读取”为准，本文件不重复维护完整清单。
- 业务资料按当前任务范围读取：先确定 PRD 章节，再匹配 UI 设计图，随后读取菜单索引、命中参考模板和必要知识库。
- 不因需求简单而跳过必读规则；简单需求也按同一套输出、去重、校验和导出口径处理。
- 信息不足时可读取 `knowledge_base/`、`knowledge_base/core_flows/` 或 `testcase_templates/common_templates/`，但不得用参考资料替代 PRD 明确要求。

## 输出归属和文件处理

站点分类、输出根目录和默认文件名均在本节维护，其他规则文件只引用本节。

| 站点分类 | `<site_type>` | Markdown 输出根目录 | Excel 输出根目录 | 适用范围 |
|---|---|---|---|---|
| 公共管理站点 | `public_site` | `outputs/origin_exports/public_site/` | `outputs/excel_exports/public_site/` | 统一门户、站点管理、全局用户、权限管理、系统服务管理、公共管理审计、登录日志 |
| 业务站点 | `business_site` | `outputs/origin_exports/business_site/` | `outputs/excel_exports/business_site/` | 产品与基础数据、年度计划与任务、方案编制、监控项目、数据分析、一键分析、报告编制、业务站点配置和异步任务 |

- 跨站点登录、站点切换、统一门户入口类用例，优先归入 `public_site`。
- 业务数据隔离、业务站点内权限和 CPV 主流程类用例，优先归入 `business_site`。
- 同一需求同时影响两个站点时，按主验证目标拆分或分别生成，避免公共管理菜单和业务站点菜单混写。

Markdown 输出路径固定为：

```text
outputs/origin_exports/<site_type>/<module_name>_testcases.md
```

确定输出文件时：

1. 先读取本次指定 PRD 章节。若 PRD 明确写出菜单入口、一级菜单、二级菜单或模块名称，以 PRD 原文作为业务归属第一依据。
2. 按下表确定默认 `<site_type>/<module_name>`。
3. 需求已明确到具体分析方法或子功能时，可在默认模块名后追加稳定英文子名，避免落到过宽的通用文件。
4. 同一个输出文件内，分组字段和需求覆盖率对照表中的模块引用必须保持一致。

| 需求类型 | 默认输出文件 |
|---|---|
| 登录、站点切换、统一认证、会话失效 | `public_site/login_site_testcases.md` |
| 统一门户、公共管理、站点管理、用户管理、权限管理、系统服务管理 | `public_site/public_site_testcases.md` |
| 产品、工艺路线、CPP、CQA、CMA、IPC、基础字典、业务基础数据、导入导出 | `business_site/product_master_data_testcases.md` |
| 年度计划、任务、任务日历、任务进度、任务关闭 | `business_site/annual_plan_task_testcases.md` |
| 方案编制、方案模板、方案审批、方案升版 | `business_site/protocol_testcases.md` |
| 监控项目、方案执行、工艺能力汇总 | `business_site/monitoring_item_testcases.md` 或 `business_site/process_capability_summary_testcases.md` |
| 数据分析、分析方法、分析结果 | `business_site/data_analysis_testcases.md`，具体分析方法可拆成更细文件 |
| 一键分析、替换数据源、数据处理、未分析原因 | `business_site/one_click_analysis_testcases.md` |
| 报告编制、报告模板、报告导出、报告审批、生效和任务回推 | `business_site/report_testcases.md` |
| 审计追踪、电子签名、工作流配置、异步任务 | 按所属站点选择对应站点输出目录 |

命名要求：

- `<module_name>` 和追加子名必须使用小写英文 snake_case，不带空格。
- 具体分析方法或子功能可拆成更细文件，例如 `data_analysis_paired_t_testcases.md`、`data_analysis_p_control_chart_testcases.md`。
- 输出文件按需求或子功能命名并统一以 `_testcases.md` 结尾；参考模板命名规则见 `testcase_templates/modules/menu_index.md`。
- PRD 未明确菜单路径且上表无命中时，按最接近的业务域命名，并在元信息块中记录“缺失明确菜单路径”的生成假设。

新需求不属于现有任何模块时：

1. 按“输出文件定位”确定站点分类、中文分组和输出文件名。
2. 参考 `testcase_templates/common_templates/` 下的通用模板。
3. 基于用户提供的资料、`knowledge_base/` 和通用覆盖维度生成用例。
4. 保存到 `outputs/origin_exports/<site_type>/<new_module_name>_testcases.md`，其中 `site_type` 只能为 `public_site` 或 `business_site`。

## 目标文件处理

生成前必须检查目标 Markdown 文件状态。

| 文件状态 | 处理规则 |
|---|---|
| 文件不存在 | 直接新建，使用标准表头写入新用例，不新增独立用例编号字段；新建时也需执行去重，确保本次生成内部无冗余 |
| 文件存在但为空或没有有效用例表 | 视为初始化占位文件，可直接覆盖写入标准表头和新生成用例，不触发追加 / 覆盖 / 另存确认 |
| 文件已存在且包含有效用例表 | 不得静默覆盖，必须向用户说明文件已存在，并等待用户明确选择追加、覆盖或另存 |

用户选择后的处理：

| 选项 | 说明 | 字段处理 |
|---|---|---|
| 追加 | 保留现有用例，在文件末尾补充本次新场景 | 保持标准表头 |
| 覆盖 | 清空现有文件，重新生成全量用例 | 使用标准表头 |
| 另存 | 保留现有文件，本次用例另存为带时间戳的新文件 `<module_name>_testcases_YYYYMMDD_HHMMSS.md` | 使用标准表头 |

带时间戳的另存文件不会被 `validate_cases.py` 和 `export_testcases.py` 的默认扫描逻辑命中；校验或导出另存文件时，必须通过 `--source` 显式指定该文件路径。

## 参考资料处理

- 若 UI 图与 PRD 描述存在字段、数据结构或字数限制等冲突，停止生成并询问用户以哪个为准。
- 若资料缺失，可以继续生成，但必须在元信息或回复中写明缺失资料和生成假设。
- 参考模板匹配和读取范围以 `testcase_templates/modules/menu_index.md` 为准。
- 参考模板只用于用例风格、分组、覆盖思路和去重判断，不作为业务归属依据；业务归属以 PRD 和“输出归属和文件处理”为准。
- 参考模板只读，不修改 `testcase_templates/modules/`。

## 生成与去重流程

1. 判断新需求所属站点分类和功能模块，确认模块名和输出文件路径。
2. 按 `testcase_templates/modules/menu_index.md` 读取参考用例。
3. 若输出文件已存在，读取其中所有已有用例的分组、用例名称、前置条件、用例步骤和预期结果。
4. 按“去重规则”逐一判断新场景是否与已有用例重复。
5. 非重复的新场景按目标文件处理方式写入；追加模式在文件末尾补充，新建 / 覆盖 / 另存模式写入完整用例表。
6. 重复场景不新增用例，在本次输出中注明“已有覆盖，参见 <用例名称>”。

## 去重规则

### 判断维度

按以下顺序判断是否重复：

1. 同一分组下 `用例名称` 是否完全相同。
2. 前置条件是否相同或高度相近。
3. 用例步骤的核心操作路径是否一致。
4. 预期结果是否相同。

四项均相同或高度相近时，视为重复，不新增。

### 可独立新增的差异

以下差异值得独立用例：

- 优先级不同，例如核心路径与边界路径。
- 预期结果有实质差异，例如错误提示、跳转目标、数据状态不同。
- 前置条件涉及不同用户类型、站点权限、产品数据权限或业务数据状态。
- 边界方向不同，例如已有最小值边界，新场景是最大值边界。
- 操作路径不同，且会影响验证目标或结果。

### 应合并或忽略的差异

以下差异不值得独立用例：

- 仅步骤措辞不同，操作目标完全一致。
- 数据值不同但验证目标相同，例如密码 5 位和 4 位都是验证长度不足拦截。
- 与已有用例仅是步骤顺序调整，且不影响业务结果。

### 重复时的处理

- 完全重复：不新增，注明“已有用例 <用例名称> 覆盖相同场景”。
- 部分重复但预期不同：可新增独立用例；差异说明写入本次回复或需求覆盖率对照表，新增用例的 `备注` 仍只写具体来源。

## 元信息和覆盖率

新建、覆盖或另存文件时，在文件顶部写入元信息块：

```markdown
<!--
生成时间：YYYY-MM-DD HH:MM
操作类型：新建 / 覆盖 / 另存
来源文档：inputs/requirements/raw_docs/<文件名>.docx
来源章节：<章节名>
输入文件：
  - <实际读取的输入文件>（最后修改：YYYY-MM-DD 或 未知）
生成假设：无 / <关键假设>
-->
```

追加模式不改已有元信息块，在文件末尾追加本次追加记录。

生成用例后必须维护“需求覆盖率对照表”：

| 需求点 / 验收标准 | 需求描述 | 覆盖用例名称 |
|---|---|---|

- 新建、覆盖或另存文件时，写入完整需求覆盖率对照表。
- 追加模式下，在本次新增用例后补充本次需求覆盖率记录，不改写已有历史覆盖率记录。
- 每条 PRD 需求点至少对应一条用例，核心链路需求应有核心用例覆盖；优先级按 `priority_rules.md` 判定。
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
