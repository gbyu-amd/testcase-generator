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
    infer_case_difficulty,
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
        expected_difficulty = infer_case_difficulty(case)
        if not difficulty_tags:
            issues.append(
                case_issue(
                    case,
                    "WARN",
                    "missing_difficulty_tag",
                    f"用例标签缺少难度等级，按 difficulty_level_rules.md 推断应为：{expected_difficulty}",
                    "用例标签",
                )
            )
        elif expected_difficulty not in difficulty_tags:
            issues.append(
                case_issue(
                    case,
                    "WARN",
                    "mismatched_difficulty_tag",
                    f"用例标签中的难度为 {'、'.join(difficulty_tags)}，按 difficulty_level_rules.md 推断应为：{expected_difficulty}",
                    "用例标签",
                )
            )
        elif len(difficulty_tags) > 1:
            issues.append(
                case_issue(
                    case,
                    "WARN",
                    "multiple_difficulty_tags",
                    f"用例标签中存在多个难度等级：{'、'.join(difficulty_tags)}，仅应保留 {expected_difficulty}",
                    "用例标签",
                )
            )

        expectation = case["预期结果"]
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


def validate_core_flow_coverage(cases: list[dict[str, str]]) -> list[Issue]:
    """CPV 核心业务模块应覆盖约定的关键场景关键词，缺失时给出 WARN。"""
    issues: list[Issue] = []
    modules_present = {case_group(case) for case in cases if case_group(case)}

    for module, keyword_groups in CORE_FLOW_KEYWORDS.items():
        if not any(module in present for present in modules_present):
            continue
        module_text = "".join(
            f"{case['用例名称']}{case['前置条件']}{case['用例步骤']}{case['预期结果']}".lower()
            for case in cases
            if module in case_group(case)
        )
        missing_groups = [
            groups[0]
            for groups in keyword_groups
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
    issues.extend(validate_duplicates(cases))
    issues.extend(validate_core_flow_coverage(cases))

    if args.json:
        print_json_report(case_files, cases, issues, fixes)
    else:
        print_text_report(case_files, cases, issues, args.summary_only, fixes)

    return 1 if has_blocking_issues(issues) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
