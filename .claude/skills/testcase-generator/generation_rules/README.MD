# generation_rules 读取说明

`generation_rules` 用于维护测试用例生成规范，负责回答“测试用例应该怎么写”。生成测试用例时，应固定读取本目录下的全部核心规则文件，确保生成口径稳定一致。

## 读取原则

- 每次生成测试用例前固定读取：`case_append_rules.md`、`testcase_writing_guidelines.md`、`coverage_dimension_rules.md`、`priority_rules.md`、`difficulty_level_rules.md`。
- 各规则分别覆盖追加去重与输出路径、写法质量、覆盖维度、优先级和难度判定。
- `README.MD` 仅作为目录说明，不属于生成前必读规则。

## 使用方式

- 生成前先完整读取核心规则文件，再根据当前需求提取其中适用的字段、覆盖、优先级、难度和追加去重要求。
- 不因需求简单而跳过详细规则文件；简单需求也应按同一套质量口径生成。
- 规则文件只约束测试用例写法，不承载具体业务流程事实。

## 当前规则文件

- `testcase_writing_guidelines.md`：用例编写规范，包含字段写法、步骤和预期结果质量要求。
- `coverage_dimension_rules.md`：覆盖维度规则，包含正向、异常、边界、权限、状态、数据一致性、合规追溯等维度。
- `priority_rules.md`：优先级判定规则。
- `difficulty_level_rules.md`：用例难度等级判定规则。
- `case_append_rules.md`：已有用例追加、覆盖、另存和去重规则。
