# 用例生成与去重规则

本文件适用于所有生成场景（新建、追加、覆盖），每次生成必读。

## 输出文件冲突处理

**文件不存在** → 直接新建，使用标准表头写入新用例，不新增独立用例编号字段。新建时同样需执行去重规则，确保本次生成的用例内部无冗余。

**文件存在但为空或没有有效用例表** → 视为初始化占位文件，可直接覆盖写入标准表头和新生成用例，不需要触发追加 / 覆盖 / 另存确认。

**文件已存在且包含有效用例表** → 不得静默覆盖，必须向用户说明文件已存在，并等待用户从以下三个选项中明确选择：

| 选项 | 说明 | 字段处理 |
|---|---|---|
| **追加** | 保留现有用例，在文件末尾补充本次新场景 | 保持标准表头 |
| **覆盖** | 清空现有文件，重新生成全量用例 | 使用标准表头 |
| **另存** | 保留现有文件，本次用例另存为带时间戳的新文件 `<module_name>_testcases_YYYYMMDD_HHMMSS.md`（仅另存时才带时间戳） | 使用标准表头 |

收到用户明确选择后，再按对应规则继续生成。

带时间戳的另存文件不会被 `validate_cases.py` 和 `export_testcases.py` 的默认扫描逻辑命中；校验或导出另存文件时，必须通过 `--source` 显式指定该文件路径。

---

## 输出路径与模块命名规则

输出路径固定为：`outputs/origin_exports/<site_type>/<module_name>_testcases.md`。

确定输出文件时：

1. 先读取本次指定 PRD 章节。若 PRD 明确写出菜单入口、一级菜单、二级菜单或模块名称，以 PRD 原文为业务归属的第一依据。
2. 按下表确定默认 `<site_type>/<module_name>`；若需求已明确到具体分析方法或子功能，可在默认模块名后追加稳定英文子名，避免落到过宽的通用文件。
3. 同一个输出文件内，分组字段和需求覆盖率对照表中的模块引用必须保持一致。
4. 不修改 `testcase_templates/modules/` 目录。

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

命名只保留通用原则：具体分析方法或子功能可拆成更细文件；`<module_name>` 和追加子名必须使用小写英文 snake_case，不带空格，例如 `data_analysis_paired_t_testcases.md`、`data_analysis_p_control_chart_testcases.md`。PRD 未明确菜单路径且本表无命中时，按最接近的业务域命名，并在元信息块中记录“缺失明确菜单路径”的生成假设。

---

## 补充生成流程

1. 判断新需求所属站点分类和功能模块，确认模块名和输出文件路径。
2. 读取 `testcase_templates/modules/menu_index.md`，按 CPV 菜单路径匹配参考文件。
3. 读取索引命中的 `testcase_templates/modules/<site_type>/<level1_menu>/<level2_menu>.md` 或 `testcase_templates/modules/<site_type>/<level1_menu>/<level2_menu>_<requirement_or_submodule>.md`；具体以索引中的实际路径为准。若索引未命中，再读取该一级菜单目录下最相关的 `.md` 参考文件（只读参考，不修改）。
4. 若输出文件已存在，读取其中所有已有用例的分组、用例名称、前置条件、用例步骤和预期结果，用于去重判断。
5. 按去重规则（见下节）逐一判断新场景是否与已有用例重复。
6. 非重复的新场景，按标准表头在输出文件末尾追加；用例追踪使用"分组 + 用例名称"，不新增独立编号字段。
7. 重复场景不新增用例，在本次输出中注明"已有覆盖，参见 <用例名称>"。
8. 追加完成后运行 `validate_cases.py`，确认整个输出文件无 ERROR。
9. 校验通过后运行 `export_testcases.py` 导出完整的 Excel（含已有用例和本次追加用例）。

---

## 菜单参考文件匹配规则

- `testcase_templates/modules/` 按站点分类和 CPV 一级菜单组织。
- `public_site/` 和 `business_site/` 下只维护一级菜单目录。
- 参考用例维护在一级菜单目录下，同时支持 `<level2_menu>.md` 和 `<level2_menu>_<requirement_or_submodule>.md` 两种命名；二级菜单未拆分或本身已足够精确时用 `<level2_menu>.md`，同一二级菜单下按需求或子功能拆分时用 `<level2_menu>_<requirement_or_submodule>.md`。
- 目录名和文件名必须全部小写，不带空格，以 `_` 分隔单词。
- 新需求跨多个二级菜单时，必须读取所有相关 `.md` 参考文件，用于去重和补充场景判断。
- 找不到对应菜单参考文件时，不阻塞生成；应记录缺失参考资料和生成假设。

---

## 追加字段规则

- 追加用例必须使用与现有文件完全一致的标准表头。
- 同一输出文件的同一分组下 `用例名称` 不允许重复；不同需求拆分到不同 Markdown 文件时，可保留通用场景的相同用例名称。
- 新增用例的 `备注` 必须按 `generation_rules/testcase_writing_guidelines.md` 的“备注、标签和关联字段”记录具体来源。
- 新增用例的 `是否自动化`、`关联接口`、`用例测试类`、`关联项目` 字段必须留空。
- 追加前必须扫描已有文件，不能凭记忆或猜测已有场景。

---

## 去重规则

### 判断流程

```
新场景 → 检查同一分组下用例名称是否与已有用例完全相同？
  ↓ 是 → 重复，不新增
  ↓ 否 → 检查前置条件是否相同？
            ↓ 是 → 检查用例步骤是否高度相似（核心步骤一致）？
                      ↓ 是 → 检查预期结果是否相同？
                                ↓ 是 → 完全重复，不新增
                                ↓ 否 → 可能是场景变体，判断差异是否值得独立用例（见下方标准）
                      ↓ 否 → 不同操作路径，可以新增
            ↓ 否 → 不同前置数据，可以新增
```

### 差异是否值得独立用例的判断标准

以下差异**值得**独立用例（应新增）：
- 优先级不同（核心路径 vs 边界路径）
- 预期结果有实质差异（不同错误提示 / 不同跳转目标 / 不同数据状态）
- 前置条件涉及不同的用户类型、站点权限、产品数据权限或业务数据状态

以下差异**不值得**独立用例（应合并或忽略）：
- 仅步骤措辞不同，操作目标完全一致
- 数据值不同但验证目标相同（如密码 5 位 vs 密码 4 位，都是验证长度不足拦截）
- 与已有用例仅是顺序调整

### 重复时的处理

- 完全重复：不新增，注明"已有用例 <用例名称> 覆盖相同场景"。
- 部分重复但预期不同：可新增独立用例；差异说明写入本次回复或需求覆盖率对照表，新增用例的 `备注` 仍只写具体来源。
- 边界变体：若已有用例是最小值边界，新场景是最大值边界，则可以独立新增。

---

## 新模块处理

如果新需求不属于现有任何模块：

1. 按"输出路径与模块命名规则"确定站点分类、中文分组和输出文件名。
2. 不修改 `testcase_templates/modules/`（只读目录）。
3. 参考 `testcase_templates/common_templates/` 下的通用模板。
4. 基于用户提供的资料、`knowledge_base/` 和通用覆盖维度生成用例。
5. 保存到 `outputs/origin_exports/<site_type>/<new_module_name>_testcases.md`，使用标准表头，其中 `site_type` 只能为 `public_site` 或 `business_site`。
6. 在输出文件开头标注：
   - 该模块是扩展模块
   - 缺失的参考资料（如无 PRD、无 UI 设计图）
   - 生成假设（如"假设未登录用户访问该页面会跳转登录页"）

---

## 备注和标签记录

每条新增用例必须在 `备注` 中记录输入来源，具体写法以 `generation_rules/testcase_writing_guidelines.md` 的“备注、标签和关联字段”为准，本文件不重复维护来源枚举。

`用例标签` 只填写按 `difficulty_level_rules.md` 判定的难度等级。难度等级只能为 `简单`、`一般`、`困难`，不再保留业务筛选标签。
