# CPV 菜单参考用例索引

生成测试用例前，先按本索引匹配 CPV 菜单路径，再读取对应参考文件。参考文件只读，不保存新生成用例。

| 站点分类 | CPV 菜单路径 | 参考文件 |
|---|---|---|
| 公共管理站点 | 公共管理站点 / 审计追踪 / 权限管理 | `public_site/audit_trail/audit_trail_permission_manage_template.md` |
| 业务站点 | 业务站点 / 配置管理 / 审计追踪 | `business_site/configuration_manage/audit_trail_template.md` |
| 业务站点 | 业务站点 / 年度计划与任务 / 年度计划设置 | `business_site/plan_manage/annual_plan_settings_template.md` |
| 业务站点 | 业务站点 / 年度计划与任务 / 任务管理 | `business_site/plan_manage/task_manage_template.md` |
| 业务站点 | 业务站点 / 方案管理 / 方案模板 | `business_site/scheme_manage/scheme_templates_template.md` |
| 业务站点 | 业务站点 / 方案管理 / 方案编制 | `business_site/scheme_manage/scheme_formulation_template.md` |
| 业务站点 | 业务站点 / 方案执行 / 关联分析 | `business_site/scheme_execution/correlation_analysis_template.md` |
| 业务站点 | 业务站点 / 方案执行 / 监控项目 / 箱线图 | `business_site/scheme_execution/monitoring_items_box_plot_template.md` |
| 业务站点 | 业务站点 / 方案执行 / 监控项目 / 配对T检验 | `business_site/scheme_execution/monitoring_items_paired_t_template.md` |
| 业务站点 | 业务站点 / 报告管理 / 报告生成 | `business_site/report_manage/report_generation_template.md` |
| 业务站点 | 业务站点 / 报告管理 / 报告模板 | `business_site/report_manage/report_templates_template.md` |

## 维护规则

- `public_site/` 和 `business_site/` 下只维护一级菜单目录。
- 一级菜单下的参考用例统一以 `_template.md` 作为公共后缀；二级菜单未拆分时使用 `<level2_menu>_template.md`，同一二级菜单下按需求或子功能拆分时使用 `<level2_menu>_<requirement_or_submodule>_template.md`。
- 新增、移动或重命名参考用例文件时，必须同步更新本索引。
- 若需求跨多个菜单，应读取所有命中的参考文件。
