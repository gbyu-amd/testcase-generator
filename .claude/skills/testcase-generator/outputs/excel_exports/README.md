# 表格导出文件说明

## 目录用途

本目录用于保存从 Markdown 用例导出的表格文件及导出说明。

## 目录结构

```text
excel_exports/
├── public_site/    # 公共管理站点 Excel 导出文件
└── business_site/  # 业务站点 Excel 导出文件
```

导出脚本会根据 `--source` 所属的 `origin_exports/<site_type>/` 自动选择对应的 Excel 输出目录。

| Markdown 来源目录 | Excel 输出目录 |
|---|---|
| `outputs/origin_exports/public_site/` | `outputs/excel_exports/public_site/` |
| `outputs/origin_exports/business_site/` | `outputs/excel_exports/business_site/` |

## 导出字段

导出表格应包含以下字段：

- 一级分组
- 二级分组
- 三级分组
- 用例名称
- 优先级
- 创建人
- 用例描述
- 前置条件
- 用例步骤
- 预期结果
- 备注
- 用例标签
- 是否自动化
- 关联接口
- 用例测试类
- 关联项目

## 导出前检查

- 表格字段是否完整。
- 优先级是否只使用 P0、P1、P2。
- 同一分组下用例名称是否唯一。
- 用例步骤是否可执行。
- 预期结果是否可验证。
- 新生成用例的备注是否写明具体来源，例如需求文档、UI 设计图、核心流程或规则文件。
- 新生成用例的是否自动化、关联接口、用例测试类、关联项目字段是否留空。
