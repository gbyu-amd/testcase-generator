# 工具脚本说明

## 目录用途

本目录用于存放辅助维护测试用例的脚本，例如校验用例格式、导出表格文件等。

## 脚本列表

- `case_utils.py`：公共工具模块，提供表头定义、路径安全检查、Markdown 表格解析和文件发现逻辑，不需要直接运行。
- `convert_docx.py`：将 Word (.docx) 文档转换为 Markdown，忽略所有图片。正式生成用例时必须先整份转换并覆盖 `inputs/requirements/current_prd.md`；`--section --print` 仅用于临时排查章节转换问题。
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


## 校验用例脚本

### 校验全部模块

```bash
python scripts/validate_cases.py
```

默认递归校验 `outputs/origin_exports/` 下的生成用例文件，包括 `public_site/` 和 `business_site/` 分类目录。

### 校验单个模块

```bash
python scripts/validate_cases.py --source outputs/origin_exports/business_site/data_analysis_paired_t_testcases.md
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

### 默认导出全部模块（合并汇总）

在项目根目录执行：

```bash
python scripts/export_testcases.py
```

脚本会默认读取 `outputs/origin_exports/**/*_testcases.md`，包括站点分类目录下的用例文件；导出前先执行完整校验，并按站点分类导出到 `outputs/excel_exports/public_site/` 或 `outputs/excel_exports/business_site/`。该模式会将同一站点下多个 Markdown 合并为 `测试用例导出_YYYYMMDD_HHMMSS.xlsx`，仅适合临时汇总。
存在 `ERROR` 时会停止导出。

### 指定单个模块导出（分需求交付）

```bash
python scripts/export_testcases.py --source outputs/origin_exports/business_site/data_analysis_paired_t_testcases.md
```

单文件 `--source` 会导出同名 Excel，例如 `data_analysis_paired_t_testcases.xlsx`。分需求交付时应逐个 Markdown 源文件执行该命令，不使用默认合并导出。

### 指定导出文件名

```bash
python scripts/export_testcases.py -o data_analysis_paired_t_testcases.xlsx --source outputs/origin_exports/business_site/data_analysis_paired_t_testcases.md
```

### 导出并清理历史 Excel

```bash
python scripts/export_testcases.py --source outputs/origin_exports/business_site/data_analysis_paired_t_testcases.md --clean
```

`--clean` 只清理本次输出目录下其他 `.xlsx` 文件，使用前需确认不会删除仍需保留的交付文件。

### 启用严格校验

```bash
python scripts/export_testcases.py --strict
```

启用 `--strict` 后，只要存在 `ERROR` 或 `WARN`，脚本都会停止导出。

## 文件发现规则

- 默认只扫描文件名以 `_testcases.md` 结尾的 Markdown。
- 另存文件若使用 `<module_name>_testcases_YYYYMMDD_HHMMSS.md` 命名，不会被默认扫描；校验或导出时必须通过 `--source` 显式指定。
- `export_testcases.py` 导出时会按 `difficulty_level_rules.md` 校正 Excel 中的 `用例标签`。若 Markdown 源文件也要求 0 WARN，应先根据 `validate_cases.py` 的 WARN 明细修复源文件。

## 使用原则

- 脚本只能处理本项目内的用例文件。
- 执行前必须确认目标模块。
- 导出结果应保存到 `outputs/excel_exports/<site_type>/`。
- 校验失败时应先修复用例，再进行导出。
