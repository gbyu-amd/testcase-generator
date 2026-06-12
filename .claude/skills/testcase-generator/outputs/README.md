# 输出结果说明

## 目录用途

本目录用于保存测试用例生成后的原始文件、评审报告和导出文件。

## 目录结构

```
outputs/
├── origin_exports/      # 原始测试用例文件（Markdown 格式）
│   ├── login_testcases.md
│   ├── cart_testcases.md
│   └── checkout_testcases.md
├── excel_exports/       # Excel 导出文件
│   └── 测试用例导出_YYYYMMDD_HHMMSS.xlsx
└── review_reports/      # 用例评审报告
    └── review_report.md
```

## 保存规则

- 原始测试用例保存到 `origin_exports/`，文件命名格式：`<module_name>_testcases.md`
- Excel 导出文件保存到 `excel_exports/`，文件命名格式：`测试用例导出_YYYYMMDD_HHMMSS.xlsx`
- 用例评审报告保存到 `review_reports/`（如需要）
- `testcase_templates/` 仅作为参考模板，不保存新生成的用例
- 生成模式下，新增或补充的 Markdown 用例只写入 `origin_exports/`

## 用例编号规则

- 每次生成到单个输出文件的用例编号从 001 开始递增
- 输出文件编号不依赖 `testcase_templates/` 中已有用例的编号
- 例如：登录-功能-001、登录-功能-002...
