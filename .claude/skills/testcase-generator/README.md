# 淘宝测试用例生成器使用说明

## 项目用途

为淘宝类电商前端项目生成结构化功能测试用例，支持基于需求文档、界面设计图、接口文档、历史缺陷等多种输入源，自动生成并导出为 Excel。

## 目录结构

```
testcase-generator/
├── knowledge_base/       # 知识库（项目概览、业务术语、流程、历史缺陷）
├── generation_rules/     # 生成规则（编号、优先级、覆盖维度）
├── testcase_templates/   # 模板和参考用例
│   ├── common_templates/ # 格式模板
│   └── modules/          # 各模块参考用例（只读）
├── inputs/               # 输入文件目录
│   ├── requirements/     # 需求文档
│   ├── ui_design/        # 界面设计说明
│   └── api_docs/         # 接口文档
├── scripts/              # 校验和导出脚本
└── outputs/              # 输出文件目录
    ├── origin_exports/   # 原始测试用例（Markdown）
    └── excel_exports/    # Excel 导出文件
```

## 快速开始

### 1. 准备输入文件

根据需求将文件放入对应目录：

| 输入类型 | 保存位置 | 适用场景 |
|---|---|---|
| 需求文档 | `inputs/requirements/` | 功能需求、PRD |
| 界面设计 | `inputs/ui_design/` | UI 改版、交互说明 |
| 接口文档 | `inputs/api_docs/` | 接口测试、数据一致性 |
| 历史缺陷 | `knowledge_base/historical_bugs/` | 回归测试 |

### 2. 提出需求

在对话中提出需求，例如：

- `根据 inputs/requirements/taobao_login_prd.md 生成测试用例`
- `根据界面设计图补充购物车模块用例`
- `根据历史缺陷生成回归用例`

### 3. 获取输出

Agent 会自动：
1. 生成测试用例，保存到 `outputs/origin_exports/<module_name>_testcases.md`
2. 运行校验脚本，确认格式和质量
3. 校验通过后自动导出 Excel 到 `outputs/excel_exports/`

## 使用场景

| 场景 | 输入 | 输出 |
|---|---|---|
| 根据需求文档生成 | PRD 文件 | 功能、异常、边界等完整用例 |
| 根据界面设计补充 | UI 截图说明 | 交互、展示、兼容性用例 |
| 根据接口文档补充 | 接口说明 | 状态、异常、数据一致性用例 |
| 根据历史缺陷生成 | 缺陷信息 | 回归测试用例 |

## 文件说明

- **SKILL.md**：Agent 执行规则，包含完整的生成流程和质量要求
- **README.md**：给使用者看的快速上手说明
- **testcase_templates/modules/**：参考用例库，只读使用，不保存新生成用例
- **outputs/origin_exports/**：生成模式下唯一保存原始 Markdown 用例的位置

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