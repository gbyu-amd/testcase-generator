# 工具脚本说明

## 目录用途

本目录用于存放辅助维护测试用例的脚本，例如校验用例格式、导出表格文件等。

## 脚本列表

- `case_utils.py`：公共工具模块，提供表头定义、路径安全检查、Markdown 表格解析和文件发现逻辑，不需要直接运行。
- `validate_cases.py`：检查用例编号、字段完整性、优先级和重复场景，支持 ERROR/WARN 分级、JSON 输出和安全格式修复。
- `export_testcases.py`：将模块 Markdown 用例导出为 Excel 表格文件，导出前会先执行完整校验。

## 推荐执行闭环

生成测试用例后，建议按以下顺序执行：

1. Agent 生成或修改 `outputs/origin_exports/<module_name>_testcases.md`
2. 运行 `validate_cases.py` 校验输出文件
3. 如果存在 `ERROR`，Agent 根据问题明细修复 Markdown 用例
4. 如只是表格格式问题，可运行 `validate_cases.py --fix`
5. 重新运行 `validate_cases.py`
6. 校验通过后运行 `export_testcases.py` 导出 Excel

脚本只负责机械校验和安全格式修复；前置条件、预期结果、重复场景、优先级和用例类型等业务语义问题应由 Agent 或测试人员根据资料修复。

## 校验用例脚本

### 校验全部模块

```bash
python scripts/validate_cases.py
```

默认校验 `outputs/origin_exports/` 下的生成用例文件。

### 校验单个模块

```bash
python scripts/validate_cases.py --source outputs/origin_exports/cart_testcases.md
```

### 输出 JSON 结果

```bash
python scripts/validate_cases.py --json
```

### 自动修复格式问题

```bash
python scripts/validate_cases.py --fix
```

`--fix` 只修复 `outputs/origin_exports/` 内的 Markdown 表格格式，例如表头顺序、分隔行、单元格空格、换行 `<br>`、竖线转义、重复空行和文件末尾换行。不会修改 `testcase_templates/`，也不会修改用例编号、优先级、用例类型、测试场景、前置条件或预期结果等业务内容。

校验内容包括标准表头、字段完整性、优先级、用例类型、重复编号、重复测试场景、重复流程和空泛预期结果。
问题会按 `ERROR` 和 `WARN` 分级；存在 `ERROR` 时脚本退出码为 `1`。

## 导出表格脚本

### 默认导出全部模块

在项目根目录执行：

```bash
python scripts/export_testcases.py
```

脚本会默认读取 `outputs/origin_exports/**/*_testcases.md`，导出前先执行完整校验，并将结果导出到 `outputs/excel_exports/`。
存在 `ERROR` 时会停止导出。

### 指定单个模块导出

```bash
python scripts/export_testcases.py --source outputs/origin_exports/cart_testcases.md
```

### 指定导出文件名

```bash
python scripts/export_testcases.py -o cart_testcases.xlsx --source outputs/origin_exports/cart_testcases.md
```

### 启用严格校验

```bash
python scripts/export_testcases.py --strict
```

启用 `--strict` 后，只要存在 `ERROR` 或 `WARN`，脚本都会停止导出。

## 使用原则

- 脚本只能处理本项目内的用例文件。
- 执行前必须确认目标模块。
- 导出结果应保存到 `outputs/excel_exports/`。
- 校验失败时应先修复用例，再进行导出。
