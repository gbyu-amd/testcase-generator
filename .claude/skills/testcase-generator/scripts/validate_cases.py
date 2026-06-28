#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用途：
    校验 Markdown 测试用例表格是否符合本项目的固定格式和质量规则。
    这是生成用例后、导出 Excel 前的质量门禁。

默认读取：
    outputs/origin_exports/**/*_testcases.md

适用场景：
    - 校验 Agent 新生成的输出用例。
    - 导出 Excel 前确认字段、优先级、用例描述和追踪信息可用。
    - 通过 --source 显式校验某个文件或参考用例目录。
    - 通过 --fix 自动修复 outputs/origin_exports/ 下的 Markdown 表格格式，不修改业务语义。
    - 通过 --json 输出结构化结果，便于 Agent 根据问题明细修复用例。

校验内容：
    - 是否存在标准测试用例表格
    - 字段是否完整
    - 优先级是否只使用 P0、P1、P2
    - 生成用例的备注是否写明来源
    - 生成用例的是否自动化、关联接口、用例测试类、关联项目是否留空
    - 测试场景是否重复
    - 操作步骤和预期结果是否过于空泛
    - 用例步骤和预期结果是否包含“按...规则”等抽象不可验证表达
    - 备注和元信息是否错误引用 outputs 下已生成用例作为来源
    - UI 图来源与 UI 用例是否一致
    - 展示类用例是否误标为正例、同一区域 UI 展示用例是否疑似重复拆分

结果规则：
    - ERROR 表示必须修复，脚本退出码为 1。
    - WARN 表示建议修复，默认不阻断脚本成功退出。

示例：
    python scripts/validate_cases.py
    python scripts/validate_cases.py --source outputs/origin_exports/business_site/report_testcases.md
    python scripts/validate_cases.py --fix
    python scripts/validate_cases.py --json
    python scripts/validate_cases.py --source testcase_templates/modules
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from case_utils import (
    DIFFICULTY_LEVELS,
    EXPECTED_HEADERS,
    REQUIRED_HEADERS,
    VALID_PRIORITIES,
    build_source_path,
    configure_output_encoding,
    discover_case_files,
    ensure_under,
    infer_case_difficulty_with_reason,
    is_separator_row,
    normalize_cell,
    parse_case_file,
    project_root,
    read_text_file,
    split_case_tags,
    split_markdown_row,
    write_text_file,
)


VAGUE_EXPECTATION_PATTERNS = [
    re.compile(r"^页面展示正常[。.]?$"),
    re.compile(r"^功能可用[。.]?$"),
    re.compile(r"^结果正确[。.]?$"),
    re.compile(r"^按需求展示[。.]?$"),
    re.compile(r"^显示正确[。.]?$"),
    re.compile(r"^展示成功[。.]?$"),
    re.compile(r"^操作成功[。.]?$"),
    re.compile(r"^操作完成[。.]?$"),
    re.compile(r"^符合预期[。.]?$"),
    re.compile(r"^正常显示[。.]?$"),
    re.compile(r"^展示正确[。.]?$"),
    re.compile(r"^正常展示[。.]?$"),
    re.compile(r"^页面正常[。.]?$"),
    re.compile(r"^成功[。.]?$"),
    re.compile(r"^通过[。.]?$"),
]

FORBIDDEN_ABSTRACT_PATTERNS = [
    (re.compile(r"按[^。；;\n]*规则"), "按...规则"),
    (re.compile(r"根据[^。；;\n]*规则"), "根据...规则"),
    (re.compile(r"符合[^。；;\n]*规则"), "符合...规则"),
    (re.compile(r"按需求"), "按需求"),
    (re.compile(r"对照\s*PRD", re.IGNORECASE), "对照 PRD"),
    (re.compile(r"检查是否符合"), "检查是否符合"),
]

WEAK_EXPECTATION_PHRASE_RE = re.compile(
    r"(显示正确|展示正确|展示完整|内容正确|数据正确|结果正确|页面正确)"
)
CONCRETE_EXPECTATION_CONTEXT_RE = re.compile(
    r"(<br|\n|[、；;：:]|包含|提示|更新为|变为|不可|不生成|为空|"
    r"回显|置灰|字段|列表|按钮|弹窗|名称|数值|文件|图表|过程数据|"
    r"UCL|LCL|状态)"
)

OUTPUT_REFERENCE_RE = re.compile(r"(?:^|[\\/])outputs[\\/]|outputs[\\/]|_testcases\.md", re.IGNORECASE)

UI_DISPLAY_SIGNAL_RE = re.compile(
    r"(UI|页面|区域|布局|元素|按钮|文案|说明|标题|字段|列|列表|卡片|"
    r"弹窗|页签|标签|默认值|展示|显示|回显|置灰)"
)
UI_DISPLAY_TITLE_RE = re.compile(
    r"(UI校验|基础元素显示|元素显示|按钮展示|文案展示|布局展示|"
    r"页面展示|区域展示|整体展示)"
)
BUSINESS_RESULT_SIGNAL_RE = re.compile(
    r"(保存|提交|新增|编辑|删除|导入|导出|下载|上传|生成|创建|更新|"
    r"推送|写入|生效|审批|确认|发布|退回|关闭|拦截|阻止|失败|成功|"
    r"状态|记录|审计|计算|校验通过|校验失败|提示“|提示\")"
)
UI_REGION_SUFFIX_RE = re.compile(
    r"(基础元素显示|元素显示|按钮展示|文案展示|布局展示|页面展示|区域展示|"
    r"整体展示|UI校验|显示|展示|校验)$"
)

# 预期结果建议的最少字符数，过短通常说明缺少可验证的页面/数据/业务状态描述
MIN_EXPECTATION_LENGTH = 10

INVALID_SOURCE_REMARKS = {"", "无", "待填", "来源：待填"}
INVALID_SOURCE_ATTRIBUTION_PATTERNS = [
    (
        re.compile(r"来源：[^；;\n]*?(?:未明确|需要确认|需确认|待确认)"),
        "备注中的“来源：”后只能填写真实来源，不能填写“未明确/需确认”等说明；"
        "请改为“来源：<规则或资料>；说明：需求文档未明确需要确认”",
    ),
    (
        re.compile(r"来源：[^；;\n]*?需求文档"),
        "PRD 来源备注必须写为“来源：prd”，不得写为“来源：需求文档”",
    ),
    (
        re.compile(r"来源：[^；;\n]*?UI设计图"),
        "UI 图来源备注必须写为“来源：UI图”，不得写为“来源：UI设计图”",
    ),
    (
        re.compile(r"来源：[^；;\n]*?核心流程"),
        "核心流程来源必须写具体 .md 文件名，例如“来源：data_analysis_flow.md”，不得写为“来源：数据分析核心流程”",
    ),
    (
        re.compile(r"来源：[^；;\n]*?用例模板"),
        "用例模板来源必须写具体 .md 文件名，例如“来源：monitoring_items_paired_t_template.md”，不得写为“来源：监控项目用例模板”",
    ),
]
EMPTY_GENERATED_HEADERS = ["是否自动化", "关联接口", "用例测试类", "关联项目"]

# CPV 核心业务模块需要覆盖的关键场景关键词（任一同义词命中即算覆盖）
CORE_FLOW_KEYWORDS = {
    "年度计划": [
        ["生效"],
        ["生成任务", "周期性任务"],
        ["状态", "流转"],
    ],
    "任务管理": [
        ["执行", "提交"],
        ["状态", "流转"],
        ["关联方案", "方案"],
    ],
    "方案编制": [
        ["审批", "审核", "批准"],
        ["生效"],
        ["监控项目", "报告"],
    ],
    "监控项目": [
        ["分析", "数据分析"],
        ["确认"],
        ["报告", "结论"],
    ],
    "数据分析": [
        ["导入", "数据源"],
        ["字段", "配置"],
        ["结果", "图表"],
    ],
    "一键分析": [
        ["全部成功", "成功"],
        ["部分失败", "失败"],
        ["未分析原因", "未分析"],
    ],
    "报告编制": [
        ["审批", "审核", "批准"],
        ["生效"],
        ["导出", "回推"],
    ],
    "权限管理": [
        ["新增"],
        ["编辑"],
        ["删除", "批量删除"],
        ["配置", "菜单权限", "按钮权限"],
        ["停用", "启用"],
    ],
    "审计追踪": [
        ["操作人"],
        ["操作时间"],
        ["操作类型"],
        ["受影响对象"],
        ["详情", "导出"],
    ],
}

ONE_CLICK_REPAIR_INVALID_STATE_RE = re.compile(
    r"(字段删减|字段缺失|字段不存在|字段匹配失败|字段未匹配|未匹配|匹配上定类变量|变量缺失|清空)"
)
ONE_CLICK_REPAIR_FIELD_RE = re.compile(r"(纵轴变量|横轴变量|子组大小|样本量字段|变量)")
ONE_CLICK_REPAIR_FIELD_PRESERVED_RE = re.compile(
    r"(字段仍保留|变量仍保留|仍保留在配置中|未被清空|未清空|没有清空)"
)


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    file: str = ""
    line: int | None = None
    case_name: str = ""
    field: str = ""


def case_location(case: dict[str, str]) -> str:
    return f"{case['_source_file']} 第 {case['_source_line']} 行"


def case_group(case: dict[str, str]) -> str:
    groups = [
        case.get("一级分组", ""),
        case.get("二级分组", ""),
        case.get("三级分组", ""),
    ]
    return " / ".join(group for group in groups if group) or "未分组"


def case_text(case: dict[str, str]) -> str:
    return "\n".join(
        normalize_cell(case.get(field, ""))
        for field in [
            "一级分组",
            "二级分组",
            "三级分组",
            "用例名称",
            "前置条件",
            "用例步骤",
            "预期结果",
            "备注",
        ]
    )


def case_issue(
    case: dict[str, str],
    severity: str,
    code: str,
    message: str,
    field: str = "",
) -> Issue:
    source_line = case.get("_source_line", "")
    return Issue(
        severity=severity,
        code=code,
        message=message,
        file=case.get("_source_file", ""),
        line=int(source_line) if source_line.isdigit() else None,
        case_name=case.get("用例名称", ""),
        field=field,
    )


def text_issue(severity: str, code: str, message: str) -> Issue:
    return Issue(severity=severity, code=code, message=message)


def format_issue(issue: Issue) -> str:
    location = ""
    if issue.file and issue.line is not None:
        location = f"{issue.file} 第 {issue.line} 行 "
    elif issue.file:
        location = f"{issue.file} "

    field = f" [{issue.field}]" if issue.field else ""
    case_name = f" ({issue.case_name})" if issue.case_name else ""
    return f"[{issue.severity}] {issue.code}: {location}{issue.message}{field}{case_name}"


def has_blocking_issues(issues: list[Issue], strict: bool = False) -> bool:
    # strict=True 时 WARN 也视为阻塞；将来若新增 INFO 等级别，此处不会误判。
    return any(
        issue.severity == "ERROR" or (strict and issue.severity == "WARN")
        for issue in issues
    )


def escape_markdown_cell(value: str) -> str:
    value = value.strip().replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    value = value.replace("\\", "\\\\")
    value = value.replace("|", r"\|")
    value = value.replace("\n", "<br>")
    return value


def markdown_row(values: list[str]) -> str:
    return "| " + " | ".join(escape_markdown_cell(value) for value in values) + " |"


def markdown_separator() -> str:
    return "| " + " | ".join("---" for _ in EXPECTED_HEADERS) + " |"


def fix_case_file(path: Path) -> dict[str, object]:
    # 统一以无 BOM 的 utf-8 读写，去除 BOM 是有意为之，保证后续处理的一致性。
    original_text = read_text_file(path, encoding="utf-8-sig")
    lines = original_text.splitlines()
    updated_lines: list[str] = []
    changed_rows = 0
    fixed_headers = 0
    fixed_separators = 0
    removed_blank_lines = 0

    index = 0
    while index < len(lines):
        cells = [normalize_cell(cell) for cell in split_markdown_row(lines[index])]
        is_known_header = (
            len(cells) == len(EXPECTED_HEADERS) and set(cells) == set(EXPECTED_HEADERS)
        )

        if not is_known_header:
            updated_lines.append(lines[index].rstrip())
            index += 1
            continue

        canonical_header = markdown_row(EXPECTED_HEADERS)
        if lines[index].rstrip() != canonical_header:
            fixed_headers += 1
        updated_lines.append(canonical_header)
        index += 1

        if index < len(lines) and is_separator_row(split_markdown_row(lines[index])):
            if lines[index].rstrip() != markdown_separator():
                fixed_separators += 1
            index += 1
        else:
            fixed_separators += 1
        updated_lines.append(markdown_separator())

        while index < len(lines) and lines[index].strip().startswith("|"):
            row_cells = split_markdown_row(lines[index])
            if is_separator_row(row_cells):
                fixed_separators += 1
                index += 1
                continue

            normalized_cells = [normalize_cell(cell) for cell in row_cells]
            if len(normalized_cells) == len(cells):
                row_by_header = dict(zip(cells, normalized_cells))
                fixed_row = markdown_row(
                    [row_by_header.get(header, "") for header in EXPECTED_HEADERS]
                )
                if lines[index].rstrip() != fixed_row:
                    changed_rows += 1
                updated_lines.append(fixed_row)
            else:
                updated_lines.append(lines[index].rstrip())
            index += 1

    compact_lines: list[str] = []
    previous_blank = False
    for line in updated_lines:
        is_blank = not line.strip()
        if is_blank and previous_blank:
            removed_blank_lines += 1
            continue
        compact_lines.append("" if is_blank else line)
        previous_blank = is_blank

    updated_text = "\n".join(compact_lines).rstrip() + "\n"
    changed = updated_text != original_text
    if changed:
        write_text_file(path, updated_text, encoding="utf-8")

    return {
        "file": str(path),
        "changed": changed,
        "fixed_headers": fixed_headers,
        "fixed_separators": fixed_separators,
        "changed_rows": changed_rows,
        "removed_blank_lines": removed_blank_lines,
    }


def fix_case_files(case_files: list[Path]) -> list[dict[str, object]]:
    return [fix_case_file(case_file) for case_file in case_files]


def duplicate_values(
    cases: list[dict[str, str]], key_func
) -> dict[tuple[str, ...], list[dict[str, str]]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = {}
    for case in cases:
        key = key_func(case)
        if any(not value for value in key):
            continue
        grouped.setdefault(key, []).append(case)
    return {key: value for key, value in grouped.items() if len(value) > 1}


def is_vague_expectation(value: str) -> bool:
    normalized = "".join(value.split())
    return any(pattern.match(normalized) for pattern in VAGUE_EXPECTATION_PATTERNS)


def is_too_short_expectation(value: str) -> bool:
    return len("".join(value.split())) < MIN_EXPECTATION_LENGTH


def requires_source_remark(case: dict[str, str]) -> bool:
    source_file = case.get("_source_file", "")
    if not source_file:
        return False

    try:
        Path(source_file).resolve().relative_to(
            (project_root() / "outputs" / "origin_exports").resolve()
        )
        return True
    except ValueError:
        return False


def has_valid_source_remark(value: str) -> bool:
    normalized = value.strip()
    return normalized not in INVALID_SOURCE_REMARKS and "来源：" in normalized


def invalid_source_attribution_reason(value: str) -> str:
    normalized = value.strip()
    for pattern, message in INVALID_SOURCE_ATTRIBUTION_PATTERNS:
        if pattern.search(normalized):
            return message
    return ""


def first_forbidden_abstract_expression(value: str) -> str:
    normalized = normalize_cell(value)
    for pattern, label in FORBIDDEN_ABSTRACT_PATTERNS:
        if pattern.search(normalized):
            return label
    return ""


def has_weak_contextless_expectation(value: str) -> bool:
    normalized = normalize_cell(value)
    return bool(
        WEAK_EXPECTATION_PHRASE_RE.search(normalized)
        and not CONCRETE_EXPECTATION_CONTEXT_RE.search(normalized)
    )


def is_ui_case(case: dict[str, str]) -> bool:
    return (
        normalize_cell(case.get("用例描述", "")).upper() == "UI"
        or "UI校验" in case.get("用例名称", "")
    )


def is_display_only_candidate(case: dict[str, str]) -> bool:
    name = normalize_cell(case.get("用例名称", ""))
    expectation = normalize_cell(case.get("预期结果", ""))
    display_signal = UI_DISPLAY_TITLE_RE.search(name)
    business_signal = BUSINESS_RESULT_SIGNAL_RE.search(expectation)
    return bool(display_signal and not business_signal)


def ui_region_key(case: dict[str, str]) -> str:
    name = normalize_cell(case.get("用例名称", ""))
    name = name.replace(" ", "")
    name = UI_REGION_SUFFIX_RE.sub("", name)
    name = re.sub(r"[，,；;：:。.\-_/]+", "", name)
    return name


def is_generated_output_path(path: Path) -> bool:
    try:
        path.resolve().relative_to((project_root() / "outputs" / "origin_exports").resolve())
        return True
    except ValueError:
        return False


def file_metadata_block(path: Path) -> str:
    text = read_text_file(path, encoding="utf-8-sig")
    stripped = text.lstrip()
    if stripped.startswith("<!--"):
        end_index = stripped.find("-->")
        if end_index != -1:
            return stripped[: end_index + 3]

    table_index = text.find("| 一级分组 |")
    return text[:table_index] if table_index != -1 else ""


def validate_case_rows(cases: list[dict[str, str]]) -> list[Issue]:
    issues: list[Issue] = []

    for case in cases:
        missing_fields = [header for header in REQUIRED_HEADERS if not case[header]]
        if missing_fields:
            issues.append(
                case_issue(
                    case,
                    "ERROR",
                    "missing_fields",
                    f"字段缺失：{', '.join(missing_fields)}",
                )
            )

        priority = case["优先级"]
        if priority and priority not in VALID_PRIORITIES:
            issues.append(
                case_issue(
                    case,
                    "ERROR",
                    "invalid_priority",
                    f"优先级为 {priority}，应为 P0、P1 或 P2",
                    "优先级",
                )
            )

        steps = case["用例步骤"]
        if steps and not re.search(r"(^|\n|<br\s*/?>)\s*\d+[.、]", steps, re.IGNORECASE):
            issues.append(
                case_issue(
                    case,
                    "WARN",
                    "unordered_steps",
                    "用例步骤建议使用 1. 2. 3. 的有序步骤",
                    "用例步骤",
                )
            )
        forbidden_steps = first_forbidden_abstract_expression(steps)
        if forbidden_steps:
            issues.append(
                case_issue(
                    case,
                    "ERROR",
                    "abstract_step_expression",
                    f"用例步骤包含不可直接执行的抽象表达：{forbidden_steps}，请改为具体页面、字段或操作对象",
                    "用例步骤",
                )
            )

        remark = case["备注"]
        if requires_source_remark(case) and not has_valid_source_remark(remark):
            issues.append(
                case_issue(
                    case,
                    "ERROR",
                    "missing_source_remark",
                    "生成用例的备注必须写明来源，例如 来源：prd、来源：UI图、来源：data_analysis_flow.md 或 来源：coverage_dimension_rules.md-合规追溯",
                    "备注",
                )
            )
        elif requires_source_remark(case):
            invalid_source_reason = invalid_source_attribution_reason(remark)
            if invalid_source_reason:
                issues.append(
                    case_issue(
                        case,
                        "ERROR",
                        "invalid_source_attribution",
                        invalid_source_reason,
                        "备注",
                    )
                )
            if OUTPUT_REFERENCE_RE.search(remark):
                issues.append(
                    case_issue(
                        case,
                        "ERROR",
                        "output_file_used_as_source",
                        "备注不得引用 outputs 下已生成用例或 *_testcases.md 作为来源；参考用例只能来自 testcase_templates 下模板文件",
                        "备注",
                    )
                )

        if requires_source_remark(case):
            filled_empty_headers = [
                header for header in EMPTY_GENERATED_HEADERS if case.get(header, "")
            ]
            if filled_empty_headers:
                issues.append(
                    case_issue(
                        case,
                        "ERROR",
                        "generated_fields_must_be_empty",
                        "生成用例的以下字段必须留空："
                        + "、".join(filled_empty_headers),
                    )
                )

        tags = split_case_tags(case.get("用例标签", ""))
        difficulty_tags = [tag for tag in tags if tag in DIFFICULTY_LEVELS]
        expected_difficulty, difficulty_reasons = infer_case_difficulty_with_reason(case)
        difficulty_reason_text = (
            f"；原因：{'；'.join(difficulty_reasons)}" if difficulty_reasons else ""
        )
        if not difficulty_tags:
            issues.append(
                case_issue(
                    case,
                    "WARN",
                    "missing_difficulty_tag",
                    f"用例标签缺少难度等级，按 difficulty_level_rules.md 推断应为：{expected_difficulty}{difficulty_reason_text}",
                    "用例标签",
                )
            )
        elif expected_difficulty not in difficulty_tags:
            issues.append(
                case_issue(
                    case,
                    "WARN",
                    "mismatched_difficulty_tag",
                    f"用例标签中的难度为 {'、'.join(difficulty_tags)}，按 difficulty_level_rules.md 推断应为：{expected_difficulty}{difficulty_reason_text}",
                    "用例标签",
                )
            )
        elif len(difficulty_tags) > 1:
            issues.append(
                case_issue(
                    case,
                    "WARN",
                    "multiple_difficulty_tags",
                    f"用例标签中存在多个难度等级：{'、'.join(difficulty_tags)}，仅应保留 {expected_difficulty}{difficulty_reason_text}",
                    "用例标签",
                )
            )

        if not is_ui_case(case) and is_display_only_candidate(case):
            issues.append(
                case_issue(
                    case,
                    "WARN",
                    "ui_case_misclassified",
                    "该用例主要验证页面元素、按钮、文案或布局展示，建议改为 UI 用例并在名称中包含 UI校验；若同一区域已有 UI校验 用例，应合并去重",
                    "用例描述",
                )
            )

        expectation = case["预期结果"]
        forbidden_expectation = first_forbidden_abstract_expression(expectation)
        if forbidden_expectation:
            issues.append(
                case_issue(
                    case,
                    "ERROR",
                    "abstract_expectation_expression",
                    f"预期结果包含抽象不可验证表达：{forbidden_expectation}，请直接写最终可观察结果",
                    "预期结果",
                )
            )
        if expectation and is_vague_expectation(expectation):
            issues.append(
                case_issue(
                    case,
                    "ERROR",
                    "vague_expectation",
                    f"预期结果过于空泛：{expectation}",
                    "预期结果",
                )
            )
        elif expectation and has_weak_contextless_expectation(expectation):
            issues.append(
                case_issue(
                    case,
                    "WARN",
                    "weak_expectation_context",
                    f"预期结果包含“显示正确/展示完整”等弱表达，建议列出具体字段、状态、页面元素或数据变化：{expectation}",
                    "预期结果",
                )
            )
        elif expectation and is_too_short_expectation(expectation):
            issues.append(
                case_issue(
                    case,
                    "WARN",
                    "short_expectation",
                    f"预期结果过短，建议补充页面表现、数据状态或业务状态：{expectation}",
                    "预期结果",
                )
            )

    return issues


def validate_ui_case_deduplication(cases: list[dict[str, str]]) -> list[Issue]:
    issues: list[Issue] = []
    ui_cases_by_scope: dict[tuple[str, str, str], list[dict[str, str]]] = {}

    for case in cases:
        key = ui_region_key(case)
        if not key or not is_ui_case(case):
            continue
        ui_cases_by_scope.setdefault(
            (case.get("_source_file", ""), case_group(case), key), []
        ).append(case)

    for case in cases:
        if is_ui_case(case) or not is_display_only_candidate(case):
            continue
        key = ui_region_key(case)
        matched_ui_cases = ui_cases_by_scope.get(
            (case.get("_source_file", ""), case_group(case), key), []
        )
        if not matched_ui_cases:
            continue
        matched_names = "、".join(
            matched_case["用例名称"] for matched_case in matched_ui_cases
        )
        issues.append(
            case_issue(
                case,
                "WARN",
                "ui_case_duplicate_split",
                f"同一分组下已存在相同页面区域的 UI校验 用例：{matched_names}；建议把本用例的展示校验项合并到 UI 用例中",
                "用例名称",
            )
        )

    return issues


def validate_file_sources(case_files: list[Path], cases: list[dict[str, str]]) -> list[Issue]:
    issues: list[Issue] = []
    cases_by_file: dict[str, list[dict[str, str]]] = {}
    for case in cases:
        cases_by_file.setdefault(case.get("_source_file", ""), []).append(case)

    for case_file in case_files:
        if not is_generated_output_path(case_file):
            continue

        metadata = file_metadata_block(case_file)
        normalized_metadata = metadata.replace("\\", "/")
        if OUTPUT_REFERENCE_RE.search(normalized_metadata):
            issues.append(
                Issue(
                    severity="ERROR",
                    code="output_file_used_as_input_source",
                    message=(
                        "元信息输入文件不得引用 outputs 下已生成用例或 *_testcases.md；"
                        "参考用例只能来自 testcase_templates 下模板文件"
                    ),
                    file=str(case_file),
                )
            )

        file_cases = cases_by_file.get(str(case_file), [])
        has_ui_source = bool(
            re.search(
                r"inputs/ui_design/.*\.(?:png|jpg|jpeg|webp|gif)",
                normalized_metadata,
                re.IGNORECASE,
            )
        )
        has_ui_remark = any("UI图" in case.get("备注", "") for case in file_cases)
        has_ui_case = any(
            normalize_cell(case.get("用例描述", "")).upper() == "UI"
            or "UI校验" in case.get("用例名称", "")
            for case in file_cases
        )

        if has_ui_remark and not has_ui_source:
            issues.append(
                Issue(
                    severity="ERROR",
                    code="ui_source_missing_in_metadata",
                    message="用例备注引用了 UI图，但文件元信息输入文件未列出 inputs/ui_design 下的图片",
                    file=str(case_file),
                )
            )
        if has_ui_source and not has_ui_case:
            issues.append(
                Issue(
                    severity="WARN",
                    code="ui_source_without_ui_case",
                    message="文件元信息包含 UI 图，但未发现用例描述为 UI 或用例名称包含 UI校验 的用例",
                    file=str(case_file),
                )
            )

    return issues


def validate_core_flow_coverage(cases: list[dict[str, str]]) -> list[Issue]:
    """CPV 核心业务模块应覆盖约定的关键场景关键词，缺失时给出 WARN。"""
    issues: list[Issue] = []
    modules_present = {case_group(case) for case in cases if case_group(case)}

    for module, keyword_groups in CORE_FLOW_KEYWORDS.items():
        if not any(module in present for present in modules_present):
            continue
        module_cases = [case for case in cases if module in case_group(case)]
        if module == "报告编制":
            module_cases = [
                case for case in module_cases if "影响范围" not in case_group(case)
            ]
            if not module_cases:
                continue
        scoped_keyword_groups = keyword_groups
        if module == "报告编制" and module_cases and all(
            "导出" in case_group(case) for case in module_cases
        ):
            scoped_keyword_groups = [
                groups for groups in keyword_groups if groups[0] not in {"审批", "生效"}
            ]
        module_text = "".join(
            f"{case['用例名称']}{case['前置条件']}{case['用例步骤']}{case['预期结果']}".lower()
            for case in module_cases
        )
        missing_groups = [
            groups[0]
            for groups in scoped_keyword_groups
            if not any(keyword.lower() in module_text for keyword in groups)
        ]
        if missing_groups:
            issues.append(
                text_issue(
                    "WARN",
                    "core_flow_coverage_gap",
                    f"核心链路模块“{module}”疑似缺少关键场景覆盖：{'、'.join(missing_groups)}",
                )
            )

    return issues


def validate_data_analysis_one_click_rules(cases: list[dict[str, str]]) -> list[Issue]:
    """校验数据分析一键分析专项规则中容易漏掉或误判的语义场景。"""
    issues: list[Issue] = []
    cases_by_file: dict[str, list[dict[str, str]]] = {}
    for case in cases:
        cases_by_file.setdefault(case.get("_source_file", ""), []).append(case)

    for case in cases:
        group = case_group(case)
        name = normalize_cell(case.get("用例名称", ""))
        if "一键分析" not in group and "一键分析" not in name:
            continue

        text = case_text(case)
        if "修复后" in name and "成功" in name and "一键分析成功" not in name:
            issues.append(
                case_issue(
                    case,
                    "WARN",
                    "one_click_repair_name_missing_success",
                    "一键分析修复成功类用例名称必须明确包含“一键分析成功”，不得只写“修复后成功”",
                    "用例名称",
                )
            )

        is_repair_success = "修复后" in name and "一键分析成功" in name
        invalid_field_state = ONE_CLICK_REPAIR_INVALID_STATE_RE.search(text)
        affected_field = ONE_CLICK_REPAIR_FIELD_RE.search(text)
        field_preserved = ONE_CLICK_REPAIR_FIELD_PRESERVED_RE.search(text)
        if is_repair_success and invalid_field_state and affected_field and not field_preserved:
            issues.append(
                case_issue(
                    case,
                    "WARN",
                    "one_click_invalid_cleared_field_repair",
                    "字段删减、字段缺失、字段未匹配、匹配上定类变量或变量已清空时，不能生成一键分析修复成功用例；应改为未分析/需手动配置类用例",
                    "用例名称",
                )
            )

    for source_file, file_cases in cases_by_file.items():
        one_click_cases = [
            case
            for case in file_cases
            if "一键分析" in case_group(case)
            or "一键分析" in normalize_cell(case.get("用例名称", ""))
        ]
        if not one_click_cases:
            continue

        file_text = "\n".join(case_text(case) for case in file_cases)
        one_click_names = "\n".join(
            normalize_cell(case.get("用例名称", "")) for case in one_click_cases
        )

        if (
            "字段删减" in file_text
            and "控制图" in file_text
            and not any("字段删减" in case_group(case) for case in one_click_cases)
        ):
            issues.append(
                Issue(
                    severity="WARN",
                    code="one_click_missing_field_deletion_case",
                    message="控制图一键分析已出现字段删减风险，但缺少三级分组为“字段删减”的独立用例",
                    file=source_file,
                )
            )

        has_non_integer_failure = (
            "纵轴变量不包含整数时一键分析未分析" in one_click_names
            or ("纵轴变量不包含整数" in one_click_names and "一键分析未分析" in one_click_names)
        )
        has_non_integer_repair = (
            "纵轴变量不包含整数修复后一键分析成功" in one_click_names
        )
        if has_non_integer_failure and not has_non_integer_repair:
            issues.append(
                Issue(
                    severity="WARN",
                    code="one_click_missing_non_integer_repair_case",
                    message="存在“纵轴变量不包含整数”的一键分析未分析用例，但缺少“纵轴变量不包含整数修复后一键分析成功”用例",
                    file=source_file,
                )
            )

    return issues


def validate_duplicates(cases: list[dict[str, str]]) -> list[Issue]:
    issues: list[Issue] = []

    duplicated_names = duplicate_values(
        cases,
        lambda case: (
            case.get("_source_file", ""),
            case_group(case),
            case["用例名称"],
        ),
    )
    for key, duplicated_cases in duplicated_names.items():
        _, group, case_name = key
        locations = "；".join(case_location(case) for case in duplicated_cases)
        issues.append(
            text_issue(
                "ERROR",
                "duplicate_case_name",
                f"用例名称重复：{group} / {case_name}，位置：{locations}",
            )
        )

    duplicated_flows = duplicate_values(
        cases,
        lambda case: (
            case.get("_source_file", ""),
            case_group(case),
            case["前置条件"],
            case["用例步骤"],
            case["预期结果"],
        ),
    )
    for key, duplicated_cases in duplicated_flows.items():
        group = key[1]
        locations = "；".join(case_location(case) for case in duplicated_cases)
        issues.append(
            text_issue(
                "WARN",
                "duplicate_flow",
                f"疑似重复流程：{group}，位置：{locations}",
            )
        )

    return issues


def build_summary(
    case_files: list[Path],
    cases: list[dict[str, str]],
    issues: list[Issue],
    fixes: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    modules = Counter(case_group(case) for case in cases if case_group(case))
    errors = [issue for issue in issues if issue.severity == "ERROR"]
    warnings = [issue for issue in issues if issue.severity == "WARN"]
    fixes = fixes or []
    return {
        "file_count": len(case_files),
        "case_count": len(cases),
        "modules": sorted(modules),
        "issue_count": len(issues),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "fixed_file_count": sum(1 for fix in fixes if fix["changed"]),
    }


def print_text_report(
    case_files: list[Path],
    cases: list[dict[str, str]],
    issues: list[Issue],
    summary_only: bool = False,
    fixes: list[dict[str, object]] | None = None,
) -> None:
    summary = build_summary(case_files, cases, issues, fixes)
    if fixes is not None:
        print("格式修复结果：")
        print(f"- 处理文件数量：{len(fixes)}")
        print(f"- 更新文件数量：{summary['fixed_file_count']}")
        changed_fixes = [fix for fix in fixes if fix["changed"]]
        if changed_fixes and not summary_only:
            for fix in changed_fixes:
                print(
                    "- "
                    f"{fix['file']}：表头 {fix['fixed_headers']}，"
                    f"分隔行 {fix['fixed_separators']}，"
                    f"用例行 {fix['changed_rows']}，"
                    f"重复空行 {fix['removed_blank_lines']}"
                )
        print()

    print("测试用例校验结果：")
    print(f"- 文件数量：{summary['file_count']}")
    print(f"- 用例数量：{summary['case_count']}")
    print(f"- 覆盖模块：{', '.join(summary['modules'])}")
    print(f"- 问题数量：{summary['issue_count']}")
    print(f"- 错误数量：{summary['error_count']}")
    print(f"- 警告数量：{summary['warning_count']}")

    if issues and not summary_only:
        print("\n问题明细：")
        for issue in issues:
            print(f"- {format_issue(issue)}")


def print_json_report(
    case_files: list[Path],
    cases: list[dict[str, str]],
    issues: list[Issue],
    fixes: list[dict[str, object]] | None = None,
) -> None:
    payload = {
        "summary": build_summary(case_files, cases, issues, fixes),
        "issues": [asdict(issue) for issue in issues],
        "fixes": fixes or [],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def parse_args(argv: list[str]) -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description="校验 Markdown 测试用例表格")
    parser.add_argument(
        "--source",
        default=str(root / "outputs" / "origin_exports"),
        help="输入文件或目录，默认扫描 outputs/origin_exports/**/*_testcases.md",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="只输出汇总，不逐条输出问题明细",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="只修复 outputs/origin_exports/ 内的 Markdown 表格格式，不修改用例业务语义",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出校验结果，便于 Agent 或自动化流程解析",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    configure_output_encoding()
    root = project_root()
    args = parse_args(argv)

    try:
        source = ensure_under(build_source_path(args.source, root), root, "输入路径")
        if args.fix:
            output_cases_dir = root / "outputs" / "origin_exports"
            ensure_under(source, output_cases_dir, "--fix 输入路径")
        case_files = discover_case_files(source)
    except (FileNotFoundError, ValueError) as error:
        issues = [text_issue("ERROR", "source_error", str(error))]
        if args.json:
            print_json_report([], [], issues)
        else:
            print(f"校验失败：{error}", file=sys.stderr)
        return 1

    if not case_files:
        issues = [
            text_issue("ERROR", "no_case_files", "未找到任何测试用例 Markdown 文件")
        ]
        if args.json:
            print_json_report([], [], issues)
        else:
            print("校验失败：未找到任何测试用例 Markdown 文件", file=sys.stderr)
        return 1

    fixes: list[dict[str, object]] | None = None
    if args.fix:
        fixes = fix_case_files(case_files)

    cases: list[dict[str, str]] = []
    issues: list[Issue] = []
    for case_file in case_files:
        parsed_cases, parse_issues = parse_case_file(case_file)
        cases.extend(parsed_cases)
        issues.extend(text_issue("ERROR", "parse_error", issue) for issue in parse_issues)

    if not cases:
        issues.append(text_issue("ERROR", "no_cases", "未解析到测试用例"))
        if args.json:
            print_json_report(case_files, cases, issues, fixes)
        else:
            print_text_report(case_files, cases, issues, args.summary_only, fixes)
        return 1

    issues.extend(validate_case_rows(cases))
    issues.extend(validate_ui_case_deduplication(cases))
    issues.extend(validate_file_sources(case_files, cases))
    issues.extend(validate_duplicates(cases))
    issues.extend(validate_core_flow_coverage(cases))
    issues.extend(validate_data_analysis_one_click_rules(cases))

    if args.json:
        print_json_report(case_files, cases, issues, fixes)
    else:
        print_text_report(case_files, cases, issues, args.summary_only, fixes)

    return 1 if has_blocking_issues(issues) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
