# 需求拆分索引

本文件由 `scripts/split_requirements.py` 生成，用于记录整份 PRD 拆分后的需求文件和 UI 目录映射。首次生成后请人工确认章节边界、模块归属和 UI 归属。

| 需求编号 | 原始编号 | 需求标题 | 站点 | 模块 | 需求文件 | UI 目录 | 原始章节 |
|---|---|---|---|---|---|---|---|
| REQ-CPV-001 | CPV-HOME-01 | 首页代办与看板（CPV-HOME-01） | business_site | home_workspace | `inputs/requirements/business_site/home_workspace/REQ-CPV-001.md` | `inputs/ui_design/REQ-CPV-001` | 模块详细功能说明 > 首页工作台（CPV-HOME-01） > 首页代办与看板（CPV-HOME-01） |
| REQ-CPV-002 | CPV-AP-01 | 计划全生命周期管理（CPV-AP-01） | business_site | annual_plan | `inputs/requirements/business_site/annual_plan/REQ-CPV-002.md` | `inputs/ui_design/REQ-CPV-002` | 模块详细功能说明 > 年度计划设置 > 计划全生命周期管理（CPV-AP-01） |
| REQ-CPV-003 | CPV-TM-01 | 任务执行与状态跟踪（CPV-TM-01） | business_site | task_manage | `inputs/requirements/business_site/task_manage/REQ-CPV-003.md` | `inputs/ui_design/REQ-CPV-003` | 模块详细功能说明 > 任务管理 > 任务执行与状态跟踪（CPV-TM-01） |
| REQ-CPV-004 | CPV-PT-01 | 方案模版相关功能（CPV-PT-01） | business_site | plan_template | `inputs/requirements/business_site/plan_template/REQ-CPV-004.md` | `inputs/ui_design/REQ-CPV-004` | 模块详细功能说明 > 方案模版 > 方案模版相关功能（CPV-PT-01） |
| REQ-CPV-005 | CPV-PP-01 | 方案编制相关功能（CPV-PP-01） | business_site | plan_compile | `inputs/requirements/business_site/plan_compile/REQ-CPV-005.md` | `inputs/ui_design/REQ-CPV-005` | 模块详细功能说明 > 方案编制 > 方案编制相关功能（CPV-PP-01） |
| REQ-CPV-006 | - | 方案编制支持导出 | business_site | plan_compile | `inputs/requirements/business_site/plan_compile/REQ-CPV-006.md` | `inputs/ui_design/REQ-CPV-006` | 模块详细功能说明 > 方案编制 > 方案编制支持导出 |
| REQ-CPV-007 | - | 方案编制和报告编制关联模版相关优化 | business_site | plan_compile | `inputs/requirements/business_site/plan_compile/REQ-CPV-007.md` | `inputs/ui_design/REQ-CPV-007` | 模块详细功能说明 > 方案编制 > 方案编制和报告编制关联模版相关优化 |
| REQ-CPV-008 | - | 【方案编制】新增相关性分析 | business_site | plan_compile | `inputs/requirements/business_site/plan_compile/REQ-CPV-008.md` | `inputs/ui_design/REQ-CPV-008` | 模块详细功能说明 > 方案编制 > 【方案编制】新增相关性分析 |
| REQ-CPV-009 | - | 相关性分析和监控项目支持在方案中直接分析 | business_site | project_monitor | `inputs/requirements/business_site/project_monitor/REQ-CPV-009.md` | `inputs/ui_design/REQ-CPV-009` | 模块详细功能说明 > 方案编制 > 相关性分析和监控项目支持在方案中直接分析 |
| REQ-CPV-010 | CPV-MI-01 | 监控项目（CPV-MI-01） | business_site | project_monitor | `inputs/requirements/business_site/project_monitor/REQ-CPV-010.md` | `inputs/ui_design/REQ-CPV-010` | 模块详细功能说明 > 项目监控 > 监控项目（CPV-MI-01） |
| REQ-CPV-011 | - | 监控项目相关优化 | business_site | project_monitor | `inputs/requirements/business_site/project_monitor/REQ-CPV-011.md` | `inputs/ui_design/REQ-CPV-011` | 模块详细功能说明 > 项目监控 > 监控项目（CPV-MI-01） > 监控项目相关优化 |
| REQ-CPV-012 | - | 监控项目增加编辑功能 | business_site | project_monitor | `inputs/requirements/business_site/project_monitor/REQ-CPV-012.md` | `inputs/ui_design/REQ-CPV-012` | 模块详细功能说明 > 项目监控 > 监控项目（CPV-MI-01） > 监控项目增加编辑功能 |
| REQ-CPV-013 | - | 工艺能力汇总 | business_site | process_capability_summary | `inputs/requirements/business_site/process_capability_summary/REQ-CPV-013.md` | `inputs/ui_design/REQ-CPV-013` | 模块详细功能说明 > 项目监控 > 工艺能力汇总 |
| REQ-CPV-014 | - | 工艺能力汇总支持导出PDF | business_site | process_capability_summary | `inputs/requirements/business_site/process_capability_summary/REQ-CPV-014.md` | `inputs/ui_design/REQ-CPV-014` | 模块详细功能说明 > 项目监控 > 工艺能力汇总 > 工艺能力汇总支持导出PDF |
| REQ-CPV-015 | - | 相关性分析 | business_site | correlation_analysis | `inputs/requirements/business_site/correlation_analysis/REQ-CPV-015.md` | `inputs/ui_design/REQ-CPV-015` | 模块详细功能说明 > 项目监控 > 相关性分析 |
| REQ-CPV-016 | CPV-RT-01 | 报告模版相关功能（CPV-RT-01） | business_site | report_template | `inputs/requirements/business_site/report_template/REQ-CPV-016.md` | `inputs/ui_design/REQ-CPV-016` | 模块详细功能说明 > 报告模版 > 报告模版相关功能（CPV-RT-01） |
| REQ-CPV-017 | CPV-RP-01 | 报告编制与审批相关（CPV-RP-01） | business_site | report_compile | `inputs/requirements/business_site/report_compile/REQ-CPV-017.md` | `inputs/ui_design/REQ-CPV-017` | 模块详细功能说明 > 报告编制 > 报告编制与审批相关（CPV-RP-01） |
| REQ-CPV-018 | - | ONLYOFFICE文档编辑权限汇总表 | business_site | report_compile | `inputs/requirements/business_site/report_compile/REQ-CPV-018.md` | `inputs/ui_design/REQ-CPV-018` | 模块详细功能说明 > 报告编制 > ONLYOFFICE文档编辑权限汇总表 |
| REQ-CPV-019 | - | 报告中插入分析结果相关优化 | business_site | report_compile | `inputs/requirements/business_site/report_compile/REQ-CPV-019.md` | `inputs/ui_design/REQ-CPV-019` | 模块详细功能说明 > 报告编制 > 报告中插入分析结果相关优化 |
| REQ-CPV-020 | - | 报告编制支持导出 | business_site | report_compile | `inputs/requirements/business_site/report_compile/REQ-CPV-020.md` | `inputs/ui_design/REQ-CPV-020` | 模块详细功能说明 > 报告编制 > 报告编制支持导出 |
| REQ-CPV-021 | - | 支持插入相关性分析模块产生的分析结果 | business_site | correlation_analysis | `inputs/requirements/business_site/correlation_analysis/REQ-CPV-021.md` | `inputs/ui_design/REQ-CPV-021` | 模块详细功能说明 > 报告编制 > 支持插入相关性分析模块产生的分析结果 |
| REQ-CPV-022 | - | 【审批流程优化】- 再次提交自动上次带出审批人 | business_site | report_compile | `inputs/requirements/business_site/report_compile/REQ-CPV-022.md` | `inputs/ui_design/REQ-CPV-022` | 模块详细功能说明 > 报告编制 > 【审批流程优化】- 再次提交自动上次带出审批人 |
| REQ-CPV-023 | - | 新增工艺参数配置功能 | business_site | general | `inputs/requirements/business_site/general/REQ-CPV-023.md` | `inputs/ui_design/REQ-CPV-023` | 模块详细功能说明 > 产品增删改查（CPV-PM-01） > 新增工艺参数配置功能 |
| REQ-CPV-024 | CPV-ATP-01 | 异步任务处理相关（CPV- ATP-01） | business_site | async_task | `inputs/requirements/business_site/async_task/REQ-CPV-024.md` | `inputs/ui_design/REQ-CPV-024` | 模块详细功能说明 > 异步任务处理 > 异步任务处理相关（CPV- ATP-01） |
| REQ-CPV-025 | CPV-UM-01 | 用户账号管理（CPV-UM-01） | public_site | user_manage | `inputs/requirements/public_site/user_manage/REQ-CPV-025.md` | `inputs/ui_design/REQ-CPV-025` | 模块详细功能说明 > 用户管理 > 用户账号管理（CPV-UM-01） |
| REQ-CPV-026 | CPV-DM-01 | 组织机构管理（CPV-DM-01） | public_site | department_manage | `inputs/requirements/public_site/department_manage/REQ-CPV-026.md` | `inputs/ui_design/REQ-CPV-026` | 模块详细功能说明 > 部门管理 > 组织机构管理（CPV-DM-01） |
| REQ-CPV-027 | CPV-POS-01 | 岗位信息维护（CPV-POS-01） | public_site | position_manage | `inputs/requirements/public_site/position_manage/REQ-CPV-027.md` | `inputs/ui_design/REQ-CPV-027` | 模块详细功能说明 > 岗位管理 > 岗位信息维护（CPV-POS-01） |
| REQ-CPV-028 | CPV-RM-01 | 角色权限分配（CPV-RM-01） | public_site | role_manage | `inputs/requirements/public_site/role_manage/REQ-CPV-028.md` | `inputs/ui_design/REQ-CPV-028` | 模块详细功能说明 > 角色管理 > 角色权限分配（CPV-RM-01） |
| REQ-CPV-029 | - | 工作流配置 | public_site | workflow_config | `inputs/requirements/public_site/workflow_config/REQ-CPV-029.md` | `inputs/ui_design/REQ-CPV-029` | 模块详细功能说明 > 工作流配置 > 工作流配置 |
| REQ-CPV-030 | - | 用户登录日志管理 | public_site | log_manage | `inputs/requirements/public_site/log_manage/REQ-CPV-030.md` | `inputs/ui_design/REQ-CPV-030` | 模块详细功能说明 > 日志管理 > 用户登录日志管理 |
| REQ-CPV-031 | - | 系统服务配置 | public_site | system_service | `inputs/requirements/public_site/system_service/REQ-CPV-031.md` | `inputs/ui_design/REQ-CPV-031` | 模块详细功能说明 > 系统服务配置 > 系统服务配置 |
| REQ-CPV-032 | - | 个人信息管理 | public_site | personal_center | `inputs/requirements/public_site/personal_center/REQ-CPV-032.md` | `inputs/ui_design/REQ-CPV-032` | 模块详细功能说明 > 个人中心 > 个人信息管理 |
| REQ-CPV-033 | - | 系统级审计追踪 | public_site | audit_trail | `inputs/requirements/public_site/audit_trail/REQ-CPV-033.md` | `inputs/ui_design/REQ-CPV-033` | 模块详细功能说明 > 审计追踪 > 系统级审计追踪 |
| REQ-CPV-034 | - | 各模块审计追踪详情 | public_site | audit_trail | `inputs/requirements/public_site/audit_trail/REQ-CPV-034.md` | `inputs/ui_design/REQ-CPV-034` | 模块详细功能说明 > 审计追踪 > 各模块审计追踪详情 |
| REQ-CPV-035 | - | 登录页 | public_site | tenant_config | `inputs/requirements/public_site/tenant_config/REQ-CPV-035.md` | `inputs/ui_design/REQ-CPV-035` | 模块详细功能说明 > 多租户配置 > 登录页 |
| REQ-CPV-036 | - | 统一门户管理 | public_site | portal_manage | `inputs/requirements/public_site/portal_manage/REQ-CPV-036.md` | `inputs/ui_design/REQ-CPV-036` | 模块详细功能说明 > 多租户配置 > 统一门户管理 |
| REQ-CPV-037 | - | 站点管理（公共管理内） | public_site | site_manage | `inputs/requirements/public_site/site_manage/REQ-CPV-037.md` | `inputs/ui_design/REQ-CPV-037` | 模块详细功能说明 > 多租户配置 > 站点管理（公共管理内） |
| REQ-CPV-038 | - | 用户管理（公共管理内） | public_site | user_manage | `inputs/requirements/public_site/user_manage/REQ-CPV-038.md` | `inputs/ui_design/REQ-CPV-038` | 模块详细功能说明 > 多租户配置 > 用户管理（公共管理内） |
| REQ-CPV-039 | - | 权限管理（公共管理内） | public_site | permission_manage | `inputs/requirements/public_site/permission_manage/REQ-CPV-039.md` | `inputs/ui_design/REQ-CPV-039` | 模块详细功能说明 > 多租户配置 > 权限管理（公共管理内） |
| REQ-CPV-040 | - | 公共管理系统与各业务站点的关系 | public_site | tenant_config | `inputs/requirements/public_site/tenant_config/REQ-CPV-040.md` | `inputs/ui_design/REQ-CPV-040` | 模块详细功能说明 > 多租户配置 > 公共管理系统与各业务站点的关系 |
| REQ-CPV-041 | - | 产品管理 | business_site | product_manage | `inputs/requirements/business_site/product_manage/REQ-CPV-041.md` | `inputs/ui_design/REQ-CPV-041` | 模块详细功能说明 > 产品工艺管理 > 产品管理 |
| REQ-CPV-042 | - | 工序 | business_site | process_step | `inputs/requirements/business_site/process_step/REQ-CPV-042.md` | `inputs/ui_design/REQ-CPV-042` | 模块详细功能说明 > 产品工艺管理 > 工序 |
| REQ-CPV-043 | - | 工序支持导入导出 | business_site | process_step | `inputs/requirements/business_site/process_step/REQ-CPV-043.md` | `inputs/ui_design/REQ-CPV-043` | 模块详细功能说明 > 产品工艺管理 > 工序 > 工序支持导入导出 |
| REQ-CPV-044 | - | 操作 | business_site | operation | `inputs/requirements/business_site/operation/REQ-CPV-044.md` | `inputs/ui_design/REQ-CPV-044` | 模块详细功能说明 > 产品工艺管理 > 操作 |
| REQ-CPV-045 | - | 操作支持导入导出 | business_site | operation | `inputs/requirements/business_site/operation/REQ-CPV-045.md` | `inputs/ui_design/REQ-CPV-045` | 模块详细功能说明 > 产品工艺管理 > 操作 > 操作支持导入导出 |
| REQ-CPV-046 | - | 关键设备 | business_site | critical_equipment | `inputs/requirements/business_site/critical_equipment/REQ-CPV-046.md` | `inputs/ui_design/REQ-CPV-046` | 模块详细功能说明 > 产品工艺管理 > 关键设备 |
| REQ-CPV-047 | - | 关键设备支持导入导出 | business_site | critical_equipment | `inputs/requirements/business_site/critical_equipment/REQ-CPV-047.md` | `inputs/ui_design/REQ-CPV-047` | 模块详细功能说明 > 产品工艺管理 > 关键设备 > 关键设备支持导入导出 |
| REQ-CPV-048 | - | 参数与属性维护 | business_site | parameter_attribute | `inputs/requirements/business_site/parameter_attribute/REQ-CPV-048.md` | `inputs/ui_design/REQ-CPV-048` | 模块详细功能说明 > 产品工艺管理 > 参数与属性维护 |
| REQ-CPV-049 | - | 关键物料属性 (CMA) | business_site | parameter_attribute | `inputs/requirements/business_site/parameter_attribute/REQ-CPV-049.md` | `inputs/ui_design/REQ-CPV-049` | 模块详细功能说明 > 产品工艺管理 > 参数与属性维护 > 关键物料属性 (CMA) |
| REQ-CPV-050 | - | 关键工艺参数 (CPP) | business_site | parameter_attribute | `inputs/requirements/business_site/parameter_attribute/REQ-CPV-050.md` | `inputs/ui_design/REQ-CPV-050` | 模块详细功能说明 > 产品工艺管理 > 参数与属性维护 > 关键工艺参数 (CPP) |
| REQ-CPV-051 | - | 关键质量属性 (CQA) | business_site | parameter_attribute | `inputs/requirements/business_site/parameter_attribute/REQ-CPV-051.md` | `inputs/ui_design/REQ-CPV-051` | 模块详细功能说明 > 产品工艺管理 > 参数与属性维护 > 关键质量属性 (CQA) |
| REQ-CPV-052 | - | 过程控制 (IPC) | business_site | parameter_attribute | `inputs/requirements/business_site/parameter_attribute/REQ-CPV-052.md` | `inputs/ui_design/REQ-CPV-052` | 模块详细功能说明 > 产品工艺管理 > 参数与属性维护 > 过程控制 (IPC) |
| REQ-CPV-053 | - | 工艺矩阵 | business_site | process_matrix | `inputs/requirements/business_site/process_matrix/REQ-CPV-053.md` | `inputs/ui_design/REQ-CPV-053` | 模块详细功能说明 > 产品工艺管理 > 工艺矩阵 |
| REQ-CPV-054 | - | 产品工艺管理模块兼容老数据 | business_site | product_process_manage | `inputs/requirements/business_site/product_process_manage/REQ-CPV-054.md` | `inputs/ui_design/REQ-CPV-054` | 模块详细功能说明 > 产品工艺管理 > 产品工艺管理模块兼容老数据 |
| REQ-CPV-055 | - | 参考限配置 | business_site | reference_limit | `inputs/requirements/business_site/reference_limit/REQ-CPV-055.md` | `inputs/ui_design/REQ-CPV-055` | 模块详细功能说明 > 质量规则配置 > 参考限配置 |
| REQ-CPV-056 | - | 能力分析等级配置 | business_site | capability_level | `inputs/requirements/business_site/capability_level/REQ-CPV-056.md` | `inputs/ui_design/REQ-CPV-056` | 模块详细功能说明 > 质量规则配置 > 能力分析等级配置 |
