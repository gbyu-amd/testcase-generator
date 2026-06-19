# 用例分组与命名规则

当前输出不再包含独立的"用例编号"字段。用例追踪和去重使用：

```text
一级分组 + 二级分组 + 三级分组 + 用例名称
```

## 分组规则

| 字段 | 填写规则 | 示例 |
|---|---|---|
| 一级分组 | 站点分类，优先使用公共管理站点或业务站点 | `业务站点` |
| 二级分组 | 一级菜单或业务域 | `数据分析` |
| 三级分组 | 二级菜单、页面或子流程 | `监控项目分析` |
| 用例名称 | 具体验证目标，20 字以内为佳 | `合格文件上传后生成分析结果` |

- 同一输出文件内，分组命名必须稳定，不要同一模块混用多个叫法。
- 同一分组下 `用例名称` 不允许重复。
- 跨模块联动用例以主操作所在模块作为分组，其他模块写入 `备注` 或需求覆盖率对照表；`用例标签` 只保留难度等级。

## 用例描述建议值

| 用例描述 | 适用场景 |
|---|---|
| 正例 | 正常业务流程，如创建、提交、审批、生效、分析、报告输出 |
| 反例 | 错误、失败、状态异常、数据源失效、插件不可用 |
| 边界 | 字段长度、文件大小、批次数量、周期范围、日期区间等边界 |
| 权限 | 登录态、站点权限、菜单权限、按钮权限、跨站点数据隔离 |
| 回归 | CPV 高风险操作路径、合规风险和历史问题回归验证 |
| 兼容 | 浏览器、分辨率、弱网、多页签、页面刷新和长耗时任务恢复 |
| 联动 | 计划、任务、方案、监控项目、分析结果、报告之间的状态同步 |

## 输出路径规则

| 推荐二级分组 | 适用范围 | 输出路径示例 |
|---|---|---|
| 登录与站点 | 登录、站点下拉、公共管理/自定义站点跳转、统一认证、会话失效 | `public_site/login_site_testcases.md` |
| 公共管理 | 统一门户、站点管理、用户管理、权限管理、系统服务管理 | `public_site/public_site_testcases.md` |
| 产品与基础数据 | 产品、工艺路线、CPP、CQA、CMA、IPC、基础字典、导入导出 | `business_site/product_master_data_testcases.md` |
| 年度计划与任务 | 年度计划、周期性任务、任务日历、任务进度、任务关闭 | `business_site/annual_plan_task_testcases.md` |
| 方案编制 | 方案模板、方案创建、提交、审批、退回、生效、升版 | `business_site/protocol_testcases.md` |
| 监控项目 | 监控项目生成、状态流转、分析前置、结果确认、重新分析 | `business_site/monitoring_item_testcases.md` |
| 数据分析 | 文件上传校验、插件状态、算法配置、图表配置、结果保存/回传 | `business_site/data_analysis_testcases.md` |
| 一键分析 | 替换数据源、字段匹配、处理规则同步、批量分析、未分析原因 | `business_site/one_click_analysis_testcases.md` |
| 报告编制 | 报告模板、报告创建、结果引用、审批、生效、导出、任务回推 | `business_site/report_testcases.md` |
| 审计与电子签名 | 审计追踪、电子签名、操作前后值、失败原因、合规追溯 | 按所属站点选择 `public_site/audit_esignature_testcases.md` 或 `business_site/audit_esignature_testcases.md` |
| 系统配置与异步任务 | 工作流配置、异步任务、导入导出、失败重试 | 按所属站点选择 `public_site/system_config_async_task_testcases.md` 或 `business_site/system_config_async_task_testcases.md` |

## 新模块规则

1. 确定站点分类：`public_site` 或 `business_site`。
2. 确定中文分组：一级分组、二级分组、三级分组。
3. 确定输出文件名：`outputs/origin_exports/<site_type>/<module_name>_testcases.md`。
4. 同一个输出文件内，分组字段和需求覆盖率对照表中的模块引用必须保持一致。
5. 不修改 `testcase_templates/modules/` 目录。
