# CPV 测试用例生成器

## 项目是什么

这是一个**基于 Claude Code 的 AI 测试用例生成工具**，以 Skill（技能插件）形式封装，专门服务于 CPV 系统的功能测试工作。

核心价值：把需求文档、界面设计图等输入，自动转化为结构化、可执行、可导出的测试用例，代替测试人员手工编写用例的重复劳动，并通过规则和脚本保证用例质量。

## 项目结构

```
testcase-generator/
├── knowledge_base/       # 知识层：项目背景、业务术语、用户角色、各模块核心流程
├── generation_rules/     # 规则层：编写规范、输出路径、优先级、覆盖维度、补充规则
├── testcase_templates/   # 参考层：各模块高质量参考用例（只读）
│   ├── common_templates/ # 通用格式模板
│   └── modules/          # CPV 菜单参考用例
│       ├── menu_index.md # 菜单路径到参考文件的索引
│       └── <site_type>/<level1_menu>/<level2_menu>.md
├── inputs/               # 输入层：本次生成的素材
│   ├── requirements/     # 需求文档
│   │   ├── raw_docs/     # 原始 Word 文档（.docx）
│   │   ├── current_prd.md# 当前 Markdown PRD（由 convert_docx.py 生成）
│   │   └── archive/      # 历史 PRD 归档
│   └── ui_design/        # 界面设计图，按章节名组织
│       ├── 报告编制/      # 目录名 = PRD 章节名
│       ├── 年度计划/
│       └── _incoming/    # 待归类图片
├── scripts/              # 脚本层：转换、校验和导出
│   ├── convert_docx.py   # Word 转 Markdown（忽略图片），支持按章节提取
│   ├── validate_cases.py # 校验格式、质量、优先级和重复场景
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
用户提供 Word 文件 + 章节名
       │
       ▼
① AI 提取章节内容（convert_docx.py --section --print）
   无需用户手动转换，图片自动忽略
       │
       ▼
② AI 读取同名 UI 图目录（inputs/ui_design/<章节名>/）
   目录存在且有图片时读取，否则跳过
       │
       ▼
③ AI 读取规则层和参考用例（只读）
   了解编写规范、该模块已有哪些场景
       │
       ▼
④ AI 生成用例
   按覆盖维度设计场景，附需求覆盖率对照表，
   保存为 Markdown
       │
       ▼
⑤ 脚本校验（validate_cases.py）
   检查字段完整性、预期结果质量、场景重复等
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

| 输入类型 | 保存位置 | 说明 |
|---|---|---|
| 原始 Word 文档 | `inputs/requirements/raw_docs/` | 产品经理提供的 .docx，AI 自动提取章节内容 |
| UI 设计图 | `inputs/ui_design/<章节名>/` | 目录名与 PRD 章节名一致，AI 自动匹配读取 |
| 历史 PRD 归档 | `inputs/requirements/archive/` | 已处理过的历史版本 |

### 2. 提出需求

直接在对话中说明 Word 文件和章节名，无需手动执行任何脚本：

```
根据 inputs/requirements/raw_docs/tangyao_prd.docx 的"报告编制"章节生成测试用例
```

```
根据 inputs/requirements/raw_docs/tangyao_prd.docx 的"权限管理"章节追加生成测试用例
```

不确定章节名时，可以先问：

```
tangyao_prd.docx 里有哪些章节？
```

### 3. 获取输出

Agent 会自动完成校验和导出，最终输出：
- Markdown 用例文件：`outputs/origin_exports/<site_type>/<module_name>_testcases.md`
- Excel 文件：`outputs/excel_exports/<site_type>/测试用例导出_YYYYMMDD_HHMMSS.xlsx`

## Python 环境要求

大部分脚本仅使用 Python 标准库，建议使用 Python 3.10 或更高版本。

`convert_docx.py` 需要额外安装 `python-docx`，其余脚本无需额外依赖。

### 初始化虚拟环境

**macOS / Linux：**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install python-docx
```

激活后直接用 `python` 运行脚本即可。

**Windows：**

> 注意：项目路径较长时，Windows 长路径限制会导致在项目目录内创建虚拟环境失败。建议在短路径下创建，例如 `C:\venv\testcase`。

```powershell
python -m venv C:\venv\testcase
C:\venv\testcase\Scripts\pip install python-docx
```

运行脚本时用完整路径：

```powershell
C:\venv\testcase\Scripts\python scripts/convert_docx.py ...
```

## 脚本命令

```bash
# 列出 Word 文档所有章节（不确定章节名时先执行）
python scripts/convert_docx.py inputs/requirements/raw_docs/<文件名>.docx --list-sections

# 提取指定章节内容并打印（AI 自动调用，无需手动执行）
python scripts/convert_docx.py inputs/requirements/raw_docs/<文件名>.docx --section "<章节名>" --print

# 将 Word 文档整体转换为 Markdown（手动更新 current_prd.md 时使用）
python scripts/convert_docx.py inputs/requirements/raw_docs/<文件名>.docx --overwrite

# 校验本次生成的用例
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
- **testcase_templates/modules/**：按站点分类和一级菜单组织的参考用例库，二级菜单维护为同名 `.md` 文件，只读使用，不保存新生成用例
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
| 公共管理站点 | 审计追踪 / 权限管理 | `testcase_templates/modules/public_site/audit_trail/audit_trail_permission_manage.md` |
| 业务站点 | 配置管理 / 审计追踪 | `testcase_templates/modules/business_site/configuration_manage/audit_trail.md` |
| 业务站点 | 年度计划设置 | `testcase_templates/modules/business_site/plan_manage/annual_plan_settings.md` |
| 业务站点 | 任务管理 | `testcase_templates/modules/business_site/plan_manage/task_manage.md` |
| 业务站点 | 方案模板 | `testcase_templates/modules/business_site/scheme_manage/scheme_templates.md` |
| 业务站点 | 方案编制 | `testcase_templates/modules/business_site/scheme_manage/scheme_formulation.md` |
| 业务站点 | 关联分析 | `testcase_templates/modules/business_site/scheme_execution/correlation_analysis.md` |
| 业务站点 | 监控项目 | `testcase_templates/modules/business_site/scheme_execution/monitoring_items.md` |
| 业务站点 | 报告生成 | `testcase_templates/modules/business_site/report_manage/report_generation.md` |
| 业务站点 | 报告模板 | `testcase_templates/modules/business_site/report_manage/report_templates.md` |

参考文件路径以 `testcase_templates/modules/menu_index.md` 为准。`public_site/` 和 `business_site/` 下只维护一级菜单目录；一级菜单下的二级菜单用 `<level2_menu>.md` 文件维护。目录名和文件名必须全部小写，不带空格，以 `_` 分隔单词。
