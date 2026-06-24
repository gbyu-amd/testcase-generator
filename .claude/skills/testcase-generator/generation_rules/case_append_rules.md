# 用例生成、追加与去重规则

本文件适用于所有生成场景（新建、追加、覆盖），每次生成必读。

---

## 输出文件定位

站点分类、输出根目录和默认文件名均在本节维护，其他规则文件只引用本节。

| 站点分类 | `<site_type>` | Markdown 输出根目录 | Excel 输出根目录 | 适用范围 |
|---|---|---|---|---|
| 公共管理站点 | `public_site` | `outputs/origin_exports/public_site/` | `outputs/excel_exports/public_site/` | 统一门户、站点管理、全局用户、权限管理、系统服务管理、公共管理审计、登录日志 |
| 业务站点 | `business_site` | `outputs/origin_exports/business_site/` | `outputs/excel_exports/business_site/` | 产品与基础数据、年度计划与任务、方案编制、监控项目、数据分析、一键分析、报告编制、业务站点配置和异步任务 |

- 跨站点登录、站点切换、统一门户入口类用例，优先归入 `public_site`。
- 业务数据隔离、业务站点内权限和 CPV 主流程类用例，优先归入 `business_site`。
- 同一需求同时影响两个站点时，按主验证目标拆分或分别生成，避免公共管理菜单和业务站点菜单混写。

Markdown 输出路径固定为：

```text
outputs/origin_exports/<site_type>/<module_name>_testcases.md
```

确定输出文件时：

1. 先读取本次指定 PRD 章节。若 PRD 明确写出菜单入口、一级菜单、二级菜单或模块名称，以 PRD 原文作为业务归属第一依据。
2. 按下表确定默认 `<site_type>/<module_name>`。
3. 需求已明确到具体分析方法或子功能时，可在默认模块名后追加稳定英文子名，避免落到过宽的通用文件。
4. 同一个输出文件内，分组字段和需求覆盖率对照表中的模块引用必须保持一致。

| PRD 归属 / 需求类型 | 默认输出文件 |
|---|---|
| 登录、站点下拉、公共管理 / 自定义站点跳转、统一认证、会话失效 | `public_site/login_site_testcases.md` |
| 统一门户、站点管理、用户管理、权限管理、系统服务管理 | `public_site/public_site_testcases.md` |
| 产品、工艺路线、CPP、CQA、CMA、IPC、基础字典、导入导出 | `business_site/product_master_data_testcases.md` |
| 年度计划、周期性任务、任务日历、任务进度、任务关闭 | `business_site/annual_plan_task_testcases.md` |
| 方案模板、方案创建、提交、审批、退回、生效、升版 | `business_site/protocol_testcases.md` |
| 监控项目生成、状态流转、分析前置、结果确认、重新分析 | `business_site/monitoring_item_testcases.md` |
| 方案执行 / 工艺能力汇总 | `business_site/process_capability_summary_testcases.md` |
| 数据分析通用能力、文件上传校验、插件状态、算法配置、图表配置、结果保存 / 回传 | `business_site/data_analysis_testcases.md` |
| 一键分析、替换数据源、字段匹配、处理规则同步、批量分析、未分析原因 | `business_site/one_click_analysis_testcases.md` |
| 报告模板、报告创建、结果引用、审批、生效、导出、任务回推 | `business_site/report_testcases.md` |
| 审计追踪、电子签名、操作前后值、失败原因、合规追溯 | 按所属站点选择 `public_site/audit_esignature_testcases.md` 或 `business_site/audit_esignature_testcases.md` |
| 工作流配置、异步任务、导入导出、失败重试 | 按所属站点选择 `public_site/system_config_async_task_testcases.md` 或 `business_site/system_config_async_task_testcases.md` |

命名要求：

- `<module_name>` 和追加子名必须使用小写英文 snake_case，不带空格。
- 具体分析方法或子功能可拆成更细文件，例如 `data_analysis_paired_t_testcases.md`、`data_analysis_p_control_chart_testcases.md`。
- 模板文件名和输出文件名不要求一一对应：模板按菜单或参考场景命名并统一以 `_template.md` 结尾；输出文件按需求或子功能命名并统一以 `_testcases.md` 结尾。
- PRD 未明确菜单路径且上表无命中时，按最接近的业务域命名，并在元信息块中记录“缺失明确菜单路径”的生成假设。

---

## 目标文件处理

生成前必须检查目标 Markdown 文件状态。

| 文件状态 | 处理规则 |
|---|---|
| 文件不存在 | 直接新建，使用标准表头写入新用例，不新增独立用例编号字段；新建时也需执行去重，确保本次生成内部无冗余 |
| 文件存在但为空或没有有效用例表 | 视为初始化占位文件，可直接覆盖写入标准表头和新生成用例，不触发追加 / 覆盖 / 另存确认 |
| 文件已存在且包含有效用例表 | 不得静默覆盖，必须向用户说明文件已存在，并等待用户明确选择追加、覆盖或另存 |

用户选择后的处理：

| 选项 | 说明 | 字段处理 |
|---|---|---|
| 追加 | 保留现有用例，在文件末尾补充本次新场景 | 保持标准表头 |
| 覆盖 | 清空现有文件，重新生成全量用例 | 使用标准表头 |
| 另存 | 保留现有文件，本次用例另存为带时间戳的新文件 `<module_name>_testcases_YYYYMMDD_HHMMSS.md` | 使用标准表头 |

带时间戳的另存文件不会被 `validate_cases.py` 和 `export_testcases.py` 的默认扫描逻辑命中；校验或导出另存文件时，必须通过 `--source` 显式指定该文件路径。

---

## 参考模板匹配

- 生成前读取 `testcase_templates/modules/menu_index.md`，按 CPV 菜单路径匹配参考文件。
- 读取索引命中的 `testcase_templates/modules/<site_type>/<level1_menu>/<level2_menu>_template.md` 或 `testcase_templates/modules/<site_type>/<level1_menu>/<level2_menu>_<requirement_or_submodule>_template.md`；具体以索引中的实际路径为准。
- 若索引未命中，再读取该一级菜单目录下最相关的 `*_template.md` 参考文件。
- 新需求跨多个二级菜单时，读取所有相关 `*_template.md` 参考文件，用于去重和补充场景判断。
- 找不到对应菜单参考文件时，不阻塞生成，应记录缺失参考资料和生成假设。
- 参考模板只用于用例风格、分组、覆盖思路和去重判断，不作为业务归属依据；业务归属以 PRD 和“输出文件定位”为准。
- 参考模板只读，不修改 `testcase_templates/modules/`。

---

## 生成与追加流程

1. 判断新需求所属站点分类和功能模块，确认模块名和输出文件路径。
2. 按“参考模板匹配”读取参考用例；参考用例只读，不修改。
3. 若输出文件已存在，读取其中所有已有用例的分组、用例名称、前置条件、用例步骤和预期结果。
4. 按“去重规则”逐一判断新场景是否与已有用例重复。
5. 非重复的新场景，按标准表头在文件末尾追加；用例追踪使用“分组 + 用例名称”，不新增独立编号字段。
6. 重复场景不新增用例，在本次输出中注明“已有覆盖，参见 <用例名称>”。

---

## 去重规则

### 判断维度

按以下顺序判断是否重复：

1. 同一分组下 `用例名称` 是否完全相同。
2. 前置条件是否相同或高度相近。
3. 用例步骤的核心操作路径是否一致。
4. 预期结果是否相同。

四项均相同或高度相近时，视为重复，不新增。

### 可独立新增的差异

以下差异值得独立用例：

- 优先级不同，例如核心路径与边界路径。
- 预期结果有实质差异，例如错误提示、跳转目标、数据状态不同。
- 前置条件涉及不同用户类型、站点权限、产品数据权限或业务数据状态。
- 边界方向不同，例如已有最小值边界，新场景是最大值边界。
- 操作路径不同，且会影响验证目标或结果。

### 应合并或忽略的差异

以下差异不值得独立用例：

- 仅步骤措辞不同，操作目标完全一致。
- 数据值不同但验证目标相同，例如密码 5 位和 4 位都是验证长度不足拦截。
- 与已有用例仅是步骤顺序调整，且不影响业务结果。

### 重复时的处理

- 完全重复：不新增，注明“已有用例 <用例名称> 覆盖相同场景”。
- 部分重复但预期不同：可新增独立用例；差异说明写入本次回复或需求覆盖率对照表，新增用例的 `备注` 仍只写具体来源。

---

## 新模块处理

如果新需求不属于现有任何模块：

1. 按“输出文件定位”确定站点分类、中文分组和输出文件名。
2. 不修改 `testcase_templates/modules/`。
3. 参考 `testcase_templates/common_templates/` 下的通用模板。
4. 基于用户提供的资料、`knowledge_base/` 和通用覆盖维度生成用例。
5. 保存到 `outputs/origin_exports/<site_type>/<new_module_name>_testcases.md`，其中 `site_type` 只能为 `public_site` 或 `business_site`。
