# 输出结果说明

## 目录用途

本目录用于保存测试用例生成后的原始文件和导出文件。

## 目录结构

```
outputs/
├── origin_exports/      # 原始测试用例文件（Markdown 格式）
│   ├── public_site/     # 公共管理站点输出
│   │   └── <module_name>_testcases.md
│   └── business_site/   # 业务站点输出
│       ├── data_analysis_paired_t_testcases.md
│       └── <module_name>_testcases.md
├── excel_exports/       # Excel 导出文件
│   ├── public_site/     # 公共管理站点 Excel
│   │   └── <module_name>_testcases.xlsx
│   └── business_site/   # 业务站点 Excel
│       ├── data_analysis_paired_t_testcases.xlsx
│       └── <module_name>_testcases.xlsx
```

## 保存规则

- 原始测试用例按站点分类保存到 `origin_exports/public_site/` 或 `origin_exports/business_site/`，文件命名格式：`<module_name>_testcases.md`
- 分需求 Excel 导出文件按站点分类保存到 `excel_exports/public_site/` 或 `excel_exports/business_site/`，文件命名格式：`<module_name>_testcases.xlsx`
- 不带 `--source` 或传入目录批量导出时，脚本会生成 `测试用例导出_YYYYMMDD_HHMMSS.xlsx` 汇总文件；该文件仅用于临时汇总，不作为默认交付格式
- `export_testcases.py --clean` 仅清理 `测试用例导出_*.xlsx` 临时汇总文件，不删除 `<module_name>_testcases.xlsx` 分需求交付文件
- `testcase_templates/` 仅作为参考模板，不保存新生成的用例
- 生成模式下，新增或补充的 Markdown 用例只写入 `origin_exports/public_site/` 或 `origin_exports/business_site/`

## 站点分类

| 站点分类 | Markdown 保存目录 | Excel 保存目录 | 适用范围 |
|---|---|---|---|
| 公共管理站点 | `origin_exports/public_site/` | `excel_exports/public_site/` | 统一门户、站点管理、全局用户、权限管理、系统服务管理、公共管理审计、登录日志 |
| 业务站点 | `origin_exports/business_site/` | `excel_exports/business_site/` | 产品与基础数据、年度计划与任务、方案编制、监控项目、数据分析、一键分析、报告编制、业务站点系统配置与异步任务 |

## 用例追踪规则

- 输出表头不包含独立用例编号字段
- 用例追踪和去重使用 `一级分组 + 二级分组 + 三级分组 + 用例名称`
- 同一输出文件的同一分组下 `用例名称` 不允许重复；不同需求拆分到不同 Markdown 文件时，允许复用通用场景名称
