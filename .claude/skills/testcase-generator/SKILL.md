---
name: taobao-testcase-generator
description: 根据淘宝项目的需求文档、界面设计图、接口文档、业务规则和已有参考用例，生成测试用例并导出为 Excel。适用于登录、搜索、商品详情、购物车、结算下单、多页签操作等淘宝前端测试场景。
---

# 淘宝功能测试用例生成器

## 技能目标

为淘宝类电商前端项目生成结构化功能测试用例。基于需求文档、界面设计图、接口文档、业务说明或已有用例，生成可执行、可导出的测试用例。

生成结果必须贴近真实电商业务场景，不能只输出"功能正常""页面展示正确"这类空泛描述。

## 触发场景

- 根据需求文档生成测试用例
- 根据界面设计图补充测试用例
- 根据接口文档补充异常、状态和数据一致性用例
- 将已有用例整理成可导出表格格式

## 资料读取顺序

生成测试用例前，优先按以下顺序读取资料：

1. 本 SKILL.md 文件
2. `knowledge_base/project_overview.md`
3. `knowledge_base/business_glossary.md`
4. `knowledge_base/user_roles.md`
5. `knowledge_base/common_business_rules.md`
6. `knowledge_base/core_flows/` 下的相关流程
7. `generation_rules/` 下的规则文件
8. `testcase_templates/common_templates/` 下的通用模板（按需选用，见下表）
9. `testcase_templates/modules/<module_name>/testcases.md`（作为参考，只读）
10. 用户本次提供的需求、界面设计图、接口文档或补充说明

**通用模板选用说明：**

| 模板文件 | 适用场景 | 对应用例类型 |
|---|---|---|
| `functional_testcase_template.md` | 生成正向主流程用例时，参考字段填写要求和示例 | 正向 |
| `negative_flow_testcase_template.md` | 生成异常、权限、状态变化用例时，参考异常场景清单和预期结果写法 | 异常、权限 |
| `boundary_value_testcase_template.md` | 生成边界值用例时，参考最小值/最大值/越界的覆盖要求 | 边界 |
| `compatibility_testcase_template.md` | 生成兼容性用例时，参考环境描述和关键元素验证要求 | 兼容 |

不涉及对应类型时可跳过；联动和回归类用例参考最相关的模板即可。

如果资料缺失，可以继续生成，但必须在结果中写明缺失资料和生成假设。

## 核心执行流程

### 前置检查

- [ ] 已判断影响的功能模块名称（如登录、购物车等）
- [ ] 已读取对应模块已有用例作为只读参考
- [ ] 已确认输出路径：`outputs/origin_exports/<module_name>_testcases.md`
- [ ] 已确认本次生成文件的用例编号从 001 开始，不依赖参考用例编号

### 通用步骤

1. 判断需求影响的功能模块
2. 提取页面入口、用户角色、前置条件、主流程、分支流程、字段规则、按钮状态、异常提示和数据依赖
3. 设计正向流程、异常流程、边界值、字段校验、权限控制、状态变化和跨模块联动用例
4. 参考 `testcase_templates/` 中已有用例，避免重复场景，但不要修改参考用例
5. 生成本次输出用例，编号从 001 开始递增
6. 在用例表格后追加"需求覆盖率对照表"，逐条列出 PRD 验收标准 / 需求点与覆盖它的用例编号，标注未覆盖项
7. 保存到 `outputs/origin_exports/<module_name>_testcases.md`
8. 运行校验脚本：`python scripts/validate_cases.py --source outputs/origin_exports/<module_name>_testcases.md`
9. 如果校验失败，必须根据问题明细修复 Markdown 用例文件，然后重新运行校验
10. 校验通过后运行导出脚本：`python scripts/export_testcases.py --source outputs/origin_exports/<module_name>_testcases.md`
11. 回复导出文件路径、用例数量、覆盖模块和需求覆盖率（已覆盖 / 需求总数）

### 需求覆盖率对照

生成用例后，必须输出需求覆盖率对照表，确保 PRD 中的验收标准或需求点都被追溯到具体用例：

| 需求点 / 验收标准 | 需求描述 | 覆盖用例编号 |
|---|---|---|

- 每条 PRD 需求点至少对应一条用例，核心链路需求应有 P0 用例覆盖。
- 未覆盖的需求点必须显式列出并说明原因（如资料缺失、需求暂缓）。
- 参考 `testcase_templates/modules/login/testcases.md` 末尾的"覆盖的验收标准"表作为格式范例。

### 校验修复闭环

生成用例后必须按以下闭环执行：

1. 运行 `validate_cases.py` 校验输出文件
2. 如果存在 `ERROR`，不要导出 Excel
3. Agent 根据问题明细修复 `outputs/origin_exports/<module_name>_testcases.md`
4. 修复内容必须基于业务资料和质量要求，不得随意删除用例来绕过校验
5. 重新运行 `validate_cases.py`
6. 只有校验通过后，才运行 `export_testcases.py`

`validate_cases.py --fix` 只能用于修复 Markdown 表格格式问题，例如表头、分隔行、单元格空格、换行和文件末尾换行。业务语义问题必须由 Agent 根据资料修复，例如前置条件缺失、预期结果空泛、场景重复、优先级不合法或用例类型不合法。

### 输入来源对应操作

| 输入来源 | 读取位置 | 重点提取 |
|---|---|---|
| PRD | `inputs/requirements/` | 验收标准、主流程、异常处理 |
| UI 设计 | `inputs/ui_design/` | 页面元素、按钮状态、错误提示 |
| 接口文档 | `inputs/api_docs/` | 成功失败场景、状态码、数据一致性 |

## 输出规则

### 文件保存位置

| 内容 | 保存位置 |
|---|---|
| 原始测试用例（Markdown） | `outputs/origin_exports/<module_name>_testcases.md` |
| Excel 导出文件 | `outputs/excel_exports/测试用例导出_YYYYMMDD_HHMMSS.xlsx` |

### 重要说明

- 采用生成模式：新生成或补充的测试用例只写入 `outputs/origin_exports/`
- `testcase_templates/` 仅作为只读参考模板，不可修改或追加内容
- 每次生成到输出文件的用例编号从 001 开始递增
- 输出文件编号不依赖 `testcase_templates/` 中已有用例的编号
- 必须运行校验和导出脚本，不可跳过

## 脚本执行命令

```bash
# 校验指定生成文件
python scripts/validate_cases.py --source outputs/origin_exports/<module_name>_testcases.md

# 仅修复 Markdown 表格格式（不修改业务语义）
python scripts/validate_cases.py --source outputs/origin_exports/<module_name>_testcases.md --fix

# 导出 Excel（校验通过后执行）
python scripts/export_testcases.py --source outputs/origin_exports/<module_name>_testcases.md

# 导出并清理历史 xlsx（可选，仅保留本次导出文件）
python scripts/export_testcases.py --source outputs/origin_exports/<module_name>_testcases.md --clean
```

脚本默认读取 `outputs/origin_exports/` 下的生成文件；需要校验参考用例时，再显式传入 `--source testcase_templates/modules`。

如果虚拟环境不存在，先创建：
```bash
python -m venv .venv
```

如果 PowerShell 中文路径输出异常，运行脚本前设置：
```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
```

## 输出字段

| 用例编号 | 功能模块 | 测试场景 | 优先级 | 前置条件 | 操作步骤 | 预期结果 | 用例类型 | 来源 |
|---|---|---|---|---|---|---|---|---|

## 质量要求

- 每条用例必须有明确前置条件
- 操作步骤必须可执行
- 预期结果必须可验证，包含页面反馈、数据状态或业务状态
- 核心交易链路必须覆盖失败回滚、重复提交、库存变化、价格变化和登录态失效
- 优先级只能使用 P0、P1、P2
- 用例类型只能使用：正向、异常、边界、权限、回归、兼容、联动