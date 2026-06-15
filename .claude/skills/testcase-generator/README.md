# 淘宝测试用例生成器

## 项目是什么

这是一个**基于 Claude Code 的 AI 测试用例生成工具**，以 Skill（技能插件）形式封装，专门服务于淘宝类电商前端项目的功能测试工作。

核心价值：把需求文档、界面设计图等输入，自动转化为结构化、可执行、可导出的测试用例，代替测试人员手工编写用例的重复劳动，并通过规则和脚本保证用例质量。

## 项目结构

```
testcase-generator/
├── knowledge_base/       # 知识层：项目背景、业务术语、用户角色、各模块核心流程
├── generation_rules/     # 规则层：编写规范、编号规则、优先级、覆盖维度、补充规则
├── testcase_templates/   # 参考层：各模块高质量参考用例（只读）
│   ├── common_templates/ # 通用格式模板
│   └── modules/          # CPV 一级菜单/二级菜单参考用例
│       └── <level1_menu>/<level2_menu>/
│           ├── module_overview.md
│           └── testcases.md
├── inputs/               # 输入层：本次生成的素材
│   ├── requirements/     # 需求文档 PRD
│   └── ui_design/        # 界面设计图
├── scripts/              # 脚本层：机器校验和导出
│   ├── validate_cases.py # 校验格式、质量、编号
│   └── export_testcases.py # 导出 Excel
└── outputs/              # 输出层
    ├── origin_exports/   # 原始测试用例（Markdown）
    │   ├── public_site/   # 公共管理站点输出
    │   └── business_site/ # 业务站点输出
    └── excel_exports/    # Excel 交付文件
        ├── public_site/   # 公共管理站点 Excel
        └── business_site/ # 业务站点 Excel
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

**参考用例只读**：`testcase_templates/` 存放高质量范例，AI 只读不写，新生成内容一律写入 `outputs/origin_exports/public_site/` 或 `outputs/origin_exports/business_site/`，模板不被污染。

**完整可追溯**：每条用例通过"分组 + 用例名称"定位，并在 `备注` 中记录具体来源，例如需求文档、UI 设计图、核心流程或规则文件；生成后附需求覆盖率对照表，支持从用例反查到对应的 PRD 需求。

## 适用场景

| 场景 | 输入 | 输出 |
|---|---|---|
| 新功能上线前 | PRD 文件 | 功能、异常、边界等完整用例 |
| UI 改版 | 界面设计图说明 | 交互、展示、兼容性用例 |
| 补充存量模块 | 已有用例 + 新需求 | 去重后仅生成缺失场景 |

## 快速开始

### 1. 准备输入文件

| 输入类型 | 保存位置 | 适用场景 |
|---|---|---|
| 需求文档 | `inputs/requirements/` | 功能需求、PRD |
| 界面设计 | `inputs/ui_design/` | UI 改版、交互说明 |

### 2. 提出需求

在对话中提出需求，例如：

- `根据 inputs/requirements/taobao_login_prd.md 生成测试用例`
- `根据界面设计图补充购物车模块用例`

### 3. 获取输出

Agent 会自动完成校验和导出，最终输出：
- Markdown 用例文件：`outputs/origin_exports/<site_type>/<module_name>_testcases.md`
- Excel 文件：`outputs/excel_exports/<site_type>/测试用例导出_YYYYMMDD_HHMMSS.xlsx`

## Python 环境要求

脚本仅使用 Python 标准库，无需安装第三方依赖。建议使用 Python 3.10 或更高版本。

如团队希望在 Windows、macOS 或 Linux 上隔离运行环境，可选创建虚拟环境：

```bash
python -m venv .venv
```

Windows PowerShell 激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux 激活：

```bash
source .venv/bin/activate
```

如果 Windows PowerShell 中文路径或中文输出仍异常，运行脚本前设置：

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
```

## 脚本命令

```bash
# 校验本次生成的用例（推荐显式指定输出文件）
python scripts/validate_cases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md

# 导出 Excel（校验通过后执行）
python scripts/export_testcases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md

# 导出并清理历史 xlsx，仅保留本次文件
python scripts/export_testcases.py --source outputs/origin_exports/<site_type>/<module_name>_testcases.md --clean

# 如需校验参考用例库，显式指定 source
python scripts/validate_cases.py --source testcase_templates/modules
```

> 不带 `--source` 时脚本会默认递归扫描 `outputs/origin_exports/` 下所有用例文件，包括 `public_site/` 和 `business_site/`；
> 单模块生成时建议显式指定文件，避免误把其他模块用例一并校验或导出。

## 文件说明

- **SKILL.md**：Agent 执行规则，包含完整的生成流程和质量要求
- **README.md**：给使用者看的快速上手说明
- **testcase_templates/modules/**：按 CPV 一级菜单 / 二级菜单组织的参考用例库，只读使用，不保存新生成用例
- **outputs/origin_exports/public_site/**：公共管理站点原始 Markdown 用例保存位置
- **outputs/origin_exports/business_site/**：业务站点原始 Markdown 用例保存位置
- **outputs/excel_exports/public_site/**：公共管理站点 Excel 导出文件保存位置
- **outputs/excel_exports/business_site/**：业务站点 Excel 导出文件保存位置

## 输出站点分类

| 站点分类 | Markdown 输出目录 | Excel 输出目录 | 适用模块 |
|---|---|---|---|
| 公共管理站点 | `outputs/origin_exports/public_site/` | `outputs/excel_exports/public_site/` | 统一门户、站点管理、全局用户、权限管理、系统服务管理、公共管理审计、登录日志 |
| 业务站点 | `outputs/origin_exports/business_site/` | `outputs/excel_exports/business_site/` | 产品与基础数据、年度计划与任务、方案编制、监控项目、数据分析、一键分析、报告编制、业务站点系统配置与异步任务 |

输出文件仍按业务模块聚合，不按二级菜单继续拆分。

## 参考模块路径

| 一级菜单 | 二级菜单 | 文件路径示例 |
|---|---|---|
| 公共管理站点 | 站点管理 | `testcase_templates/modules/public_site/site_management/` |
| 公共管理站点 | 用户管理 | `testcase_templates/modules/public_site/user_management/` |
| 公共管理站点 | 权限管理 | `testcase_templates/modules/public_site/permission_management/` |
| 业务站点 | 年度计划设置 | `testcase_templates/modules/business_site/plan_management/annual_plan_settings/` |
| 业务站点 | 任务管理 | `testcase_templates/modules/business_site/plan_management/task_management/` |
| 业务站点 | 方案模板 | `testcase_templates/modules/business_site/scheme_management/scheme_templates/` |
| 业务站点 | 方案编制 | `testcase_templates/modules/business_site/scheme_management/scheme_formulation/` |
| 业务站点 | 数据管理与洞察 | `testcase_templates/modules/business_site/data_management_insights/` |
| 业务站点 | 报告生成 | `testcase_templates/modules/business_site/report_management/report_generation/` |

每个菜单目录下优先放置 `module_overview.md` 和 `testcases.md`。目录名必须全部小写，不带空格，以 `_` 分隔单词。如果某个一级菜单下暂时没有二级菜单拆分，也可以直接在 `testcase_templates/modules/<level1_menu>/` 下放置兜底参考文件。
