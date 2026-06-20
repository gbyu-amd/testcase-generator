# CPV 菜单参考用例索引

生成测试用例前，先按本索引匹配 CPV 菜单路径，再读取对应参考文件。参考文件只读，不保存新生成用例。

| 站点分类 | CPV 菜单路径 | 参考文件 |
|---|---|---|
| 公共管理站点 | 公共管理站点 / 审计追踪 / 权限管理 | `public_site/audit_trail/audit_trail_permission_manage.md` |
| 业务站点 | 业务站点 / 配置管理 / 审计追踪 | `business_site/configuration_manage/audit_trail.md` |
| 业务站点 | 业务站点 / 年度计划与任务 / 年度计划设置 | `business_site/plan_manage/annual_plan_settings.md` |
| 业务站点 | 业务站点 / 年度计划与任务 / 任务管理 | `business_site/plan_manage/task_manage.md` |
| 业务站点 | 业务站点 / 方案管理 / 方案模板 | `business_site/scheme_manage/scheme_templates.md` |
| 业务站点 | 业务站点 / 方案管理 / 方案编制 | `business_site/scheme_manage/scheme_formulation.md` |
| 业务站点 | 业务站点 / 方案执行 / 关联分析 | `business_site/scheme_execution/correlation_analysis.md` |
| 业务站点 | 业务站点 / 方案执行 / 监控项目 / 箱线图 | `business_site/scheme_execution/monitoring_items_box_plot.md` |
| 业务站点 | 业务站点 / 方案执行 / 监控项目 / 配对T检验 | `business_site/scheme_execution/monitoring_items_paired_t.md` |
| 业务站点 | 业务站点 / 报告管理 / 报告生成 | `business_site/report_manage/report_generation.md` |
| 业务站点 | 业务站点 / 报告管理 / 报告模板 | `business_site/report_manage/report_templates.md` |

## 维护规则

- `public_site/` 和 `business_site/` 下只维护一级菜单目录。
- 一级菜单下的参考用例同时支持 `<level2_menu>.md` 和 `<level2_menu>_<requirement_or_submodule>.md` 两种命名；二级菜单未拆分时可用 `correlation_analysis.md`，同一二级菜单下按需求或子功能拆分时使用 `monitoring_items_box_plot.md`、`monitoring_items_paired_t.md`。
- 新增、移动或重命名参考用例文件时，必须同步更新本索引。
- 若需求跨多个菜单，应读取所有命中的参考文件。
