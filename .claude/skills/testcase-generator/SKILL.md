---
name: cpv-testcase-generator
description: 根据 CPV 系统的需求文档、界面设计图、业务规则和已有参考用例，生成测试用例并导出为 Excel。适用于统一门户、公共管理站点、业务站点、年度计划、任务、方案、监控项目、数据分析、一键分析、报告编制、审计追踪等 CPV 测试场景。
---

# CPV 功能测试用例生成器

## 技能目标

为 CPV 系统生成结构化功能测试用例。基于需求文档、界面设计图、业务说明或已有用例，生成可执行、可导出的测试用例。

生成结果必须贴近 CPV 真实业务场景，不能只输出"功能正常""页面展示正确"这类空泛描述。

## 触发场景

- 根据需求文档生成测试用例
- 根据界面设计图补充测试用例
- 将已有用例整理成可导出表格格式

## 资料读取顺序

**快速上下文规则：**

用户指定 `REQ-CPV-xxx` 时，优先执行：

```bash
python scripts/resolve_context.py --req REQ-CPV-xxx
```

然后只读取脚本返回的最小文件集合：`generation_rules/quick_rules.md`、对应 `REQ-CPV-xxx.md`、存在实际素材的 UI 目录、命中的参考用例和必要核心流程。除非信息不足、校验失败或用户明确要求，不主动读取整份 `inputs/requirements/current_prd.md`、全部 `generation_rules/` 或无实际图片的 UI 占位目录。

生成测试用例前，优先按以下顺序读取资料：

1. 本 SKILL.md 文件
2. 若用户指定 `REQ-CPV-xxx`，执行 `scripts/resolve_context.py --req REQ-CPV-xxx` 并按返回清单读取
3. `generation_rules/quick_rules.md`
4. 用户本次指定的需求文件、章节、界面设计图或补充说明
5. `knowledge_base/project_overview.md`、`business_glossary.md`、`user_roles.md`（信息不足时读取）
6. `knowledge_base/core_flows/` 下的相关流程（按需读取）
7. `testcase_templates/modules/menu_index.md` 和命中的参考文件（按需读取）
8. `testcase_templates/common_templates/` 下的通用模板（按用例类型选用）
9. 详细规则文件：`testcase_writing_guidelines.md`、`coverage_dimension_rules.md`、`priority_rules.md`、`difficulty_level_rules.md`、`case_append_rules.md`（复杂场景、追加合并或校验失败时读取）

**模块参考用例读取规则：**

- `testcase_templates/modules/` 按站点分类和一级菜单组织，`public_site/`、`business_site/` 下只维护一级菜单目录，目录名必须使用小写英文 snake_case。
- 二级菜单参考用例不再建子目录，统一维护为一级菜单目录下的 `<level2_menu>.md` 文件，例如 `testcase_templates/modules/business_site/report_manage/report_generation.md`。
- 生成前必须先读取 `testcase_templates/modules/menu_index.md`，按 CPV 菜单路径精确匹配参考文件。
- 若需求明确对应二级菜单，仅读取索引命中的二级菜单 `.md` 参考文件。
- 若需求只对应一级菜单，或索引未命中二级菜单，则读取该一级菜单目录下最相关的 `.md` 参考文件；仍无法确定时记录缺失参考资料和生成假设。
- 若同一需求跨多个二级菜单，应读取所有相关 `.md` 参考文件；参考用例只读，不得修改。

**通用模板选用说明：**

| 模板文件 | 适用场景 | 对应用例类型 |
|---|---|---|
| `negative_flow_testcase_template.md` | 生成异常、权限、状态变化用例时，参考异常场景清单和预期结果写法 | 异常、权限 |
| `boundary_value_testcase_template.md` | 生成边界值用例时，参考最小值/最大值/越界的覆盖要求 | 边界 |
| `compatibility_testcase_template.md` | 生成兼容性用例时，参考环境描述和关键元素验证要求 | 兼容 |

不涉及对应类型时可跳过；联动和回归类用例参考最相关的模板即可。

如果资料缺失，可以继续生成，但必须在结果中写明缺失资料和生成假设。

**当前 PRD 处理规则：**

- `inputs/requirements/current_prd.md` 是默认当前 PRD 入口，用户更换产品经理提供的新 PRD 时，可直接替换该文件内容。
- `inputs/requirements/archive/` 仅保存历史 PRD，用于追溯；除非用户显式指定，不主动读取归档文件。
- 用户指定 PRD 的某个章节时，只读取该章节及必要上下文，不默认拆分或扫描整份 PRD。
- 若基于第二份 PRD 补充已有模块用例，必须先读取对应 `outputs/origin_exports/<site_type>/<module_name>_testcases.md` 去重，再按“追加 / 覆盖 / 另存”规则处理。
- 若用户指定拆分后的 `REQ-CPV-xxx`，必须优先使用 `scripts/resolve_context.py --req REQ-CPV-xxx` 定位需求、UI、参考用例和输出路径。

## 核心执行流程

### 前置检查

- [ ] 已判断影响的功能模块名称（如年度计划、任务管理、方案编制、监控项目、数据分析、报告编制、权限管理等）
- [ ] 已判断输出所属站点分类：`public_site`（公共管理站点）或 `business_site`（业务站点）
- [ ] 若输入为 `REQ-CPV-xxx`，已运行 `scripts/resolve_context.py --req REQ-CPV-xxx`
- [ ] 已检查输出文件是否已存在，并按下方规则确认处理方式
- [ ] 已按 `testcase_templates/modules/menu_index.md` 命中对应参考用例作为只读参考
- [ ] 已确认输出路径：`outputs/origin_exports/<site_type>/<module_name>_testcases.md`
- [ ] 已确认本次输出字段使用图片表头格式
- [ ] 已确认每条新生成用例的 `备注` 来源，来源可为需求文档、UI 设计图、核心流程或具体规则
- [ ] 已记录本次输入文件列表及其最后修改时间，准备写入元信息块

### 站点分类规则

`outputs/origin_exports/` 下按 CPV 站点类型分两类保存：

| 站点分类 | 保存目录 | 适用范围 |
|---|---|---|
| 公共管理站点 | `outputs/origin_exports/public_site/` | 统一门户、站点管理、全局用户、权限管理、系统服务管理、公共管理审计、登录日志等公共管理菜单 |
| 业务站点 | `outputs/origin_exports/business_site/` | 产品与基础数据、年度计划与任务、方案编制、监控项目、数据分析、一键分析、报告编制、业务站点配置和异步任务等 CPV 业务菜单 |

- 跨站点登录、站点切换、统一门户入口类用例，优先归入 `public_site`。
- 业务数据隔离、业务站点内权限和 CPV 主流程类用例，优先归入 `business_site`。
- 同一需求同时影响两个站点时，应按主验证目标拆分或分别生成到两个站点目录，避免把公共管理菜单和业务站点菜单混写到同一输出文件。

### 输出文件冲突处理

生成前必须检查 `outputs/origin_exports/<site_type>/<module_name>_testcases.md` 是否已存在：

**文件不存在** → 直接新建，编号从 001 开始。

**文件存在但为空或没有有效用例表** → 视为初始化占位文件，可直接覆盖写入标准表头和新生成用例，不需要触发追加 / 覆盖 / 另存确认。

**文件已存在** → 停止生成，向用户说明文件已存在并提供以下三个选项，等待用户明确选择后再继续：

| 选项 | 说明 | 字段处理 |
|---|---|---|
| **追加** | 在现有文件末尾补充本次新场景，保留已有用例 | 保持同一套标准表头 |
| **覆盖** | 清空现有文件，重新生成全量用例 | 使用标准表头重新生成 |
| **另存** | 保留现有文件，将本次用例保存为带时间戳的新文件：`<module_name>_testcases_YYYYMMDD.md` | 使用标准表头另存 |

不允许在未获得用户明确选择前自行决定处理方式，不允许静默覆盖已有文件。

### 通用步骤

1. 判断需求影响的功能模块
2. 检查输出文件是否存在，按"输出文件冲突处理"规则确认处理方式
3. 提取页面入口、用户角色、前置条件、主流程、分支流程、字段规则、按钮状态、异常提示和数据依赖
4. 设计正向流程、异常流程、边界值、字段校验、权限控制、状态变化和跨模块联动用例
5. 参考 `testcase_templates/` 中已有用例，避免重复场景，但不要修改参考用例
6. 生成本次输出用例，按确认的处理方式和编号规则写入；每条新用例的 `备注` 必须写明来源
7. 在用例表格后追加"需求覆盖率对照表"，逐条列出 PRD 验收标准 / 需求点与覆盖它的用例名称，标注未覆盖项
8. 在文件头部写入元信息块（见"输出文件元信息"规则），记录本次生成的输入来源和时间
9. 保存到目标文件
10. 运行校验脚本：`python scripts/validate_cases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md`
11. 如果校验失败，必须根据问题明细修复 Markdown 用例文件，然后重新运行校验
12. 校验通过后运行导出脚本：`python scripts/export_testcases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md`
13. 回复导出文件路径、用例数量、覆盖模块和需求覆盖率（已覆盖 / 需求总数）

### 需求覆盖率对照

生成用例后，必须输出需求覆盖率对照表，确保 PRD 中的验收标准或需求点都被追溯到具体用例：

| 需求点 / 验收标准 | 需求描述 | 覆盖用例名称 |
|---|---|---|

- 每条 PRD 需求点至少对应一条用例，核心链路需求应有 P0 用例覆盖。
- 未覆盖的需求点必须显式列出并说明原因（如资料缺失、需求暂缓）。
- 参考菜单索引命中的 `testcase_templates/modules/<site_type>/<level1_menu>/<level2_menu>.md` 末尾的"覆盖的验收标准"表作为格式范例。

### 输出文件元信息

每次生成或覆盖输出文件时，必须在文件**最顶部**写入以下元信息块，追加模式下在追加内容前插入一条追加记录：

```markdown
<!--
生成时间：YYYY-MM-DD HH:MM
操作类型：新建 / 覆盖 / 追加
输入文件：
  - inputs/requirements/xxx.md（最后修改：YYYY-MM-DD）
  - inputs/ui_design/xxx/（最后修改：YYYY-MM-DD）
生成假设：（如有，列出关键假设；无则填"无"）
-->
```

**填写规则：**

- `生成时间`：填写实际生成时刻，格式 `YYYY-MM-DD HH:MM`。
- `操作类型`：新建文件填 `新建`，覆盖已有文件填 `覆盖`，追加内容填 `追加`。
- `输入文件`：列出本次实际读取的所有输入文件路径，并标注该文件的最后修改日期（通过读取文件属性或文件内声明获取，无法获取时填 `未知`）。未使用任何输入文件时填 `无（基于知识库生成）`。
- `生成假设`：若输入资料不完整，记录本次生成所依赖的关键假设，供后续评审参考。

**追加模式的特殊处理：**

追加时不修改已有元信息块，在文件末尾（需求覆盖率对照表之后）追加以下追加记录：

```markdown
<!--
追加时间：YYYY-MM-DD HH:MM
追加输入文件：
  - inputs/requirements/xxx.md（最后修改：YYYY-MM-DD）
追加生成假设：（无则填"无"）
-->
```

### 校验修复闭环

生成用例后必须按以下闭环执行：

1. 运行 `validate_cases.py` 校验输出文件
2. 如果存在 `ERROR`，不要导出 Excel
3. Agent 根据问题明细修复 `outputs/origin_exports/<site_type>/<module_name>_testcases.md`
4. 修复内容必须基于业务资料和质量要求，不得随意删除用例来绕过校验
5. 重新运行 `validate_cases.py`
6. 只有校验通过后，才运行 `export_testcases.py`

`validate_cases.py --fix` 只能用于修复 Markdown 表格格式问题，例如表头、分隔行、单元格空格、换行和文件末尾换行。业务语义问题必须由 Agent 根据资料修复，例如前置条件缺失、预期结果空泛、场景重复、优先级不合法或用例描述不清晰。

### 输入来源对应操作

| 输入来源 | 读取位置 | 重点提取 |
|---|---|---|
| 当前 PRD | `inputs/requirements/current_prd.md` | 用户指定章节、验收标准、主流程、异常处理 |
| 拆分需求 | `inputs/requirements/<site_type>/<module_slug>/REQ-*.md` | 已确认的单需求、来源章节、关联 UI |
| UI 设计 | `inputs/ui_design/` | 页面元素、按钮状态、错误提示 |

## 输出规则

### 备注来源规则

- 新生成或追加的每条用例，`备注` 字段必须填写来源。
- 来自需求文档、PRD、验收标准或用户补充需求的用例，填写 `来源：需求文档`。
- 来自 UI 设计图、截图、原型图或界面交互说明的用例，填写 `来源：UI设计图`。
- 来自核心流程、业务规则、覆盖维度规则、优先级规则或具体知识库文件的用例，必须写清具体来源，例如 `来源：data_analysis_flow.md`、`来源：coverage_dimension_rules.md-合规追溯`、`来源：priority_rules.md-P0`。
- 同一条用例参考多个来源时，用分号分隔，例如 `来源：需求文档；来源：UI设计图；来源：data_analysis_flow.md`。
- `备注` 不得为空，不得填写 `无`，不得只写"通用""综合"等不可追溯来源。

### 文件保存位置

| 内容 | 保存位置 |
|---|---|
| 原始测试用例（Markdown） | `outputs/origin_exports/<site_type>/<module_name>_testcases.md` |
| Excel 导出文件 | `outputs/excel_exports/<site_type>/测试用例导出_YYYYMMDD_HHMMSS.xlsx` |

### 重要说明

- 采用生成模式：新生成或补充的测试用例只写入 `outputs/origin_exports/public_site/` 或 `outputs/origin_exports/business_site/`
- Excel 导出文件按相同站点分类写入 `outputs/excel_exports/public_site/` 或 `outputs/excel_exports/business_site/`
- `testcase_templates/` 仅作为只读参考模板，不可修改或追加内容
- 输出表头必须与下方"输出字段"保持一致
- 输出文件不再使用独立用例编号字段，追踪时使用"分组 + 用例名称"
- 必须运行校验和导出脚本，不可跳过

## 脚本执行命令

```bash
# 校验指定生成文件
python scripts/validate_cases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md

# 仅修复 Markdown 表格格式（不修改业务语义）
python scripts/validate_cases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md --fix

# 导出 Excel（校验通过后执行）
python scripts/export_testcases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md

# 导出并清理历史 xlsx（可选，仅保留本次导出文件）
python scripts/export_testcases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md --clean
```

脚本默认读取 `outputs/origin_exports/` 下的生成文件；需要校验参考用例时，再显式传入 `--source testcase_templates/modules`，脚本会递归扫描菜单索引和模块目录下的参考用例 `.md` 文件。

## Python 环境要求

脚本仅使用 Python 标准库，无需安装第三方依赖。运行脚本需使用 Python 3.10 或更高版本。完整跨平台环境说明见 `README.md`。

## 输出字段

| 一级分组 | 二级分组 | 三级分组 | 用例名称 | 优先级 | 创建人 | 用例描述 | 前置条件 | 用例步骤 | 预期结果 | 备注 | 用例标签 | 是否自动化 | 关联接口 | 用例测试类 | 关联项目 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 质量要求

- 每条用例必须有明确前置条件
- 用例步骤必须可执行
- 预期结果必须可验证，包含页面反馈、数据状态或业务状态
- CPV 核心业务链路必须覆盖状态流转、权限控制、审批/生效、数据完整性、异常拦截、审计追踪和跨模块联动
- 优先级只能使用 P0、P1、P2
- 用例描述建议使用：正例、反例、边界、权限、兼容、回归、联动
- `用例标签` 必须包含按 `generation_rules/difficulty_level_rules.md` 判定的难度等级：`简单`、`一般` 或 `困难`
- 新生成用例的 `备注` 必须写明具体来源，例如需求文档、UI 设计图、核心流程或具体规则文件
- 新生成用例的 `是否自动化`、`关联接口`、`用例测试类`、`关联项目` 字段必须留空