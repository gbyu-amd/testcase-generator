# 工具脚本说明

## 目录用途

本目录用于存放辅助维护测试用例的脚本，例如校验用例格式、导出表格文件等。

## 脚本列表

- `case_utils.py`：公共工具模块，提供表头定义、路径安全检查、Markdown 表格解析和文件发现逻辑，不需要直接运行。
- `context_config.py`：上下文映射配置，集中维护模块识别、输出文件、参考用例、核心流程和规则清单，不需要直接运行。
- `split_requirements.py`：将整份 Markdown PRD 按章节拆成独立需求文件，生成需求索引，并为每个需求创建对应 UI 目录 README。
- `resolve_context.py`：按 `REQ-CPV-xxx` 解析生成用例所需的最小上下文，包括需求文件、UI 目录、输出文件、参考用例和校验/导出命令。
- `validate_cases.py`：检查标准表头、字段完整性、优先级、重复用例名称和重复流程，支持 ERROR/WARN 分级、JSON 输出和安全格式修复。
- `export_testcases.py`：将模块 Markdown 用例导出为 Excel 表格文件，导出前会先执行完整校验。

## 推荐执行闭环

生成测试用例后，建议按以下顺序执行：

1. Agent 生成或修改 `outputs/origin_exports/<site_type>/<module_name>_testcases.md`
2. 运行 `validate_cases.py` 校验输出文件
3. 如果存在 `ERROR`，Agent 根据问题明细修复 Markdown 用例
4. 如只是表格格式问题，可运行 `validate_cases.py --fix`
5. 重新运行 `validate_cases.py`
6. 校验通过后运行 `export_testcases.py` 导出 Excel

脚本只负责机械校验和安全格式修复；前置条件、预期结果、重复用例、优先级和用例描述等业务语义问题应由 Agent 或测试人员根据资料修复。

## 需求拆分脚本

### 按整份 PRD 拆分需求

```bash
python scripts/split_requirements.py --prd "inputs/requirements/current_prd.md"
```

默认按 3/4 级标题拆分小章节，生成：

- `inputs/requirements/requirements_index.md`
- `inputs/requirements/<site_type>/<module_slug>/REQ-CPV-xxx.md`
- `inputs/ui_design/REQ-CPV-xxx/README.md`

拆分脚本只初始化 `inputs/ui_design/REQ-CPV-xxx/README.md`，不再自动扫描、复制或归类 UI 图片。UI 素材由人工确认后直接放入对应 `REQ-CPV-xxx` 目录，并更新该目录 README。

默认使用短编号文件名，避免 Windows 长路径问题。若确实需要在文件名中追加标题，可增加 `--include-title-in-name`。

### 重建拆分文件

```bash
python scripts/split_requirements.py --prd "inputs/requirements/current_prd.md" --overwrite
```

首次拆分后建议先检查 `requirements_index.md`，确认章节边界、站点分类、模块目录和 UI 归属，再基于单个 `REQ-*` 文件生成测试用例。

## 快速上下文解析

### 按 REQ 编号获取最小读取清单

```bash
python scripts/resolve_context.py --req REQ-CPV-017
```

输出内容包括：

- 单需求文件路径
- UI 目录及是否存在实际 UI 素材
- Markdown 输出文件路径
- 命中的参考用例文件
- 优先读取的快速规则
- 校验和导出命令

### 输出 JSON

```bash
python scripts/resolve_context.py --req REQ-CPV-017 --json
```

Agent 生成单个需求用例时，优先使用本脚本结果，避免反复搜索 `requirements_index.md`、`menu_index.md`、输出目录和 UI 目录。

## 校验用例脚本

### 校验全部模块

```bash
python scripts/validate_cases.py
```

默认递归校验 `outputs/origin_exports/` 下的生成用例文件，包括 `public_site/` 和 `business_site/` 分类目录。

### 校验单个模块

```bash
python scripts/validate_cases.py --source outputs/origin_exports/business_site/data_analysis_testcases.md
```

### 输出 JSON 结果

```bash
python scripts/validate_cases.py --json
```

### 自动修复格式问题

```bash
python scripts/validate_cases.py --fix
```

`--fix` 只修复 `outputs/origin_exports/` 内的 Markdown 表格格式，例如表头顺序、分隔行、单元格空格、换行 `<br>`、竖线转义、重复空行和文件末尾换行。不会修改 `testcase_templates/`，也不会修改优先级、用例名称、用例描述、前置条件或预期结果等业务内容。

校验内容包括标准表头、字段完整性、优先级、重复用例名称、重复流程和空泛预期结果。
问题会按 `ERROR` 和 `WARN` 分级；存在 `ERROR` 时脚本退出码为 `1`。

## 导出表格脚本

### 默认导出全部模块

在项目根目录执行：

```bash
python scripts/export_testcases.py
```

脚本会默认读取 `outputs/origin_exports/**/*_testcases.md`，包括站点分类目录下的用例文件；导出前先执行完整校验，并按站点分类导出到 `outputs/excel_exports/public_site/` 或 `outputs/excel_exports/business_site/`。
存在 `ERROR` 时会停止导出。

### 指定单个模块导出

```bash
python scripts/export_testcases.py --source outputs/origin_exports/business_site/data_analysis_testcases.md
```

### 指定导出文件名

```bash
python scripts/export_testcases.py -o data_analysis_testcases.xlsx --source outputs/origin_exports/business_site/data_analysis_testcases.md
```

### 启用严格校验

```bash
python scripts/export_testcases.py --strict
```

启用 `--strict` 后，只要存在 `ERROR` 或 `WARN`，脚本都会停止导出。

## 使用原则

- 脚本只能处理本项目内的用例文件。
- 执行前必须确认目标模块。
- 导出结果应保存到 `outputs/excel_exports/<site_type>/`。
- 校验失败时应先修复用例，再进行导出。
