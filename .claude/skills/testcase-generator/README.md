# 淘宝测试用例生成器

## 项目是什么

这是一个**基于 Claude Code 的 AI 测试用例生成工具**，以 Skill（技能插件）形式封装，专门服务于淘宝类电商前端项目的功能测试工作。

核心价值：把需求文档、界面设计图、接口文档等输入，自动转化为结构化、可执行、可导出的测试用例，代替测试人员手工编写用例的重复劳动，并通过规则和脚本保证用例质量。

## 项目结构

```
testcase-generator/
├── knowledge_base/       # 知识层：项目背景、业务术语、用户角色、各模块核心流程
├── generation_rules/     # 规则层：编写规范、编号规则、优先级、覆盖维度、补充规则
├── testcase_templates/   # 参考层：各模块高质量参考用例（只读）
│   ├── common_templates/ # 通用格式模板
│   └── modules/          # 各模块参考用例
├── inputs/               # 输入层：本次生成的素材
│   ├── requirements/     # 需求文档 PRD
│   ├── ui_design/        # 界面设计图
│   └── api_docs/         # 接口文档
├── scripts/              # 脚本层：机器校验和导出
│   ├── validate_cases.py # 校验格式、质量、编号
│   └── export_testcases.py # 导出 Excel
└── outputs/              # 输出层
    ├── origin_exports/   # 原始测试用例（Markdown）
    └── excel_exports/    # Excel 交付文件
```

## 工作流程

```
用户提供输入文档
       │
       ▼
① AI 读取知识层和规则层
   理解业务背景、用户角色、模块流程、编写规范
       │
       ▼
② AI 读取参考用例（只读）
   了解该模块已有哪些场景，避免重复生成
       │
       ▼
③ AI 分析输入文档
   提取页面入口、主流程、分支流程、字段规则、
   按钮状态、异常提示、数据依赖
       │
       ▼
④ AI 生成用例
   按 9 个覆盖维度设计场景，附需求覆盖率对照表，
   保存为 Markdown
       │
       ▼
⑤ 脚本校验（validate_cases.py）
   检查编号格式、字段完整性、预期结果质量、
   场景重复、核心链路关键场景覆盖等
       │
      有 ERROR？── 是 ──▶ AI 修复 ──▶ 重新校验
       │ 否
       ▼
⑥ 导出 Excel（export_testcases.py）
   生成带冻结表头、列宽、自动筛选的 .xlsx 文件
       │
       ▼
⑦ 回复结果
   文件路径、用例数量、覆盖模块、需求覆盖率
```

## 设计思路

**质量门禁优先**：生成后必须通过脚本校验才能导出，有 ERROR 时强制修复，防止空洞或格式错误的用例流入交付物。

**知识与规则分离**：业务知识（项目背景、流程）和生成规则（怎么写用例）分开存放，互不干扰，换项目时只需替换知识层。

**参考用例只读**：`testcase_templates/` 存放高质量范例，AI 只读不写，新生成内容一律写入 `outputs/origin_exports/`，模板不被污染。

**完整可追溯**：每条用例有来源字段，生成后附需求覆盖率对照表，支持从用例反查到对应的 PRD 需求。

## 适用场景

| 场景 | 输入 | 输出 |
|---|---|---|
| 新功能上线前 | PRD 文件 | 功能、异常、边界等完整用例 |
| UI 改版 | 界面设计图说明 | 交互、展示、兼容性用例 |
| 接口联调 | 接口文档 | 状态码、超时、重复提交等接口类用例 |
| 补充存量模块 | 已有用例 + 新需求 | 去重后仅生成缺失场景 |

## 快速开始

### 1. 准备输入文件

| 输入类型 | 保存位置 | 适用场景 |
|---|---|---|
| 需求文档 | `inputs/requirements/` | 功能需求、PRD |
| 界面设计 | `inputs/ui_design/` | UI 改版、交互说明 |
| 接口文档 | `inputs/api_docs/` | 接口测试、数据一致性 |

### 2. 提出需求

在对话中提出需求，例如：

- `根据 inputs/requirements/taobao_login_prd.md 生成测试用例`
- `根据界面设计图补充购物车模块用例`
- `根据接口文档补充异常和数据一致性用例`

### 3. 获取输出

Agent 会自动完成校验和导出，最终输出：
- Markdown 用例文件：`outputs/origin_exports/<module_name>_testcases.md`
- Excel 文件：`outputs/excel_exports/测试用例导出_YYYYMMDD_HHMMSS.xlsx`

## 脚本命令

```bash
# 校验本次生成的用例（推荐显式指定输出文件）
python scripts/validate_cases.py --source outputs/origin_exports/<module_name>_testcases.md

# 导出 Excel（校验通过后执行）
python scripts/export_testcases.py --source outputs/origin_exports/<module_name>_testcases.md

# 导出并清理历史 xlsx，仅保留本次文件
python scripts/export_testcases.py --source outputs/origin_exports/<module_name>_testcases.md --clean

# 如需校验参考用例库，显式指定 source
python scripts/validate_cases.py --source testcase_templates/modules
```

> 不带 `--source` 时脚本会默认全量扫描 `outputs/origin_exports/` 下所有用例文件；
> 单模块生成时建议显式指定文件，避免误把其他模块用例一并校验或导出。

如果 PowerShell 中文路径输出异常，运行前设置：

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
```

## 文件说明

- **SKILL.md**：Agent 执行规则，包含完整的生成流程和质量要求
- **README.md**：给使用者看的快速上手说明
- **testcase_templates/modules/**：参考用例库，只读使用，不保存新生成用例
- **outputs/origin_exports/**：生成模式下唯一保存原始 Markdown 用例的位置

## 参考模块

| 模块 | 文件路径 |
|---|---|
| 登录 | `testcase_templates/modules/login/` |
| 搜索 | `testcase_templates/modules/search/` |
| 商品详情 | `testcase_templates/modules/product_detail/` |
| 购物车 | `testcase_templates/modules/cart/` |
| 结算下单 | `testcase_templates/modules/checkout/` |
| 首页 | `testcase_templates/modules/home/` |
| 我的足迹 | 扩展模块，生成结果保存到 `outputs/origin_exports/myfootprint_testcases.md` |
