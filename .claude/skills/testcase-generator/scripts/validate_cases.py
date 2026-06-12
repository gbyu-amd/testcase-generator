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
    - 导出 Excel 前确认字段、编号、优先级和用例类型可用。
    - 通过 --source 显式校验某个文件或参考用例目录。
    - 通过 --fix 自动修复 outputs/origin_exports/ 下的 Markdown 表格格式，不修改业务语义。
    - 通过 --json 输出结构化结果，便于 Agent 根据问题明细修复用例。

校验内容：
    - 是否存在标准测试用例表格
    - 字段是否完整
    - 优先级是否只使用 P0、P1、P2
    - 用例类型是否在约定范围内
    - 用例编号是否重复
    - 测试场景是否重复
    - 操作步骤和预期结果是否过于空泛

结果规则：
    - ERROR 表示必须修复，脚本退出码为 1。
    - WARN 表示建议修复，默认不阻断脚本成功退出。

示例：
    python scripts/validate_cases.py
    python scripts/validate_cases.py --source outputs/origin_exports/cart_testcases.md
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
    CASE_ID_PATTERN,
    EXPECTED_HEADERS,
    ID_TYPE_TO_CASE_TYPE,
    VALID_ID_TYPES,
    VALID_PRIORITIES,
    build_source_path,
    configure_output_encoding,
    discover_case_files,
    ensure_under,
    is_separator_row,
    normalize_cell,
    parse_case_file,
    project_root,
    split_markdown_row,
)


VALID_CASE_TYPES = {"正向", "异常", "边界", "权限", "回归", "兼容", "联动"}
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

# 核心交易链路模块需要覆盖的关键场景关键词（任一同义词命中即算覆盖）
CORE_FLOW_KEYWORDS = {
    "登录": [
        ["登录态", "登录失效", "登录过期", "token过期", "token 过期"],
        ["未登录"],
        ["多页签", "多tab", "多 tab", "页签"],
    ],
    "购物车": [
        ["库存"],
        ["失效商品", "商品失效", "下架"],
        ["金额", "合计", "优惠"],
    ],
    "结算下单": [
        ["重复提交", "重复点击", "重复下单", "重复订单"],
        ["库存"],
        ["价格变化", "价格变动", "价格"],
        ["地址"],
    ],
}


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    file: str = ""
    line: int | None = None
    case_id: str = ""
    field: str = ""


def case_location(case: dict[str, str]) -> str:
    return f"{case['_source_file']} 第 {case['_source_line']} 行"


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
        case_id=case.get("用例编号", ""),
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
    case_id = f" ({issue.case_id})" if issue.case_id else ""
    return f"[{issue.severity}] {issue.code}: {location}{issue.message}{field}{case_id}"


def has_blocking_issues(issues: list[Issue], strict: bool = False) -> bool:
    return any(issue.severity == "ERROR" or strict for issue in issues)


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
    original_text = path.read_text(encoding="utf-8-sig")
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
        path.write_text(updated_text, encoding="utf-8")

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


def validate_case_rows(cases: list[dict[str, str]]) -> list[Issue]:
    issues: list[Issue] = []

    for case in cases:
        missing_fields = [header for header in EXPECTED_HEADERS if not case[header]]
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

        case_type = case["用例类型"]
        if case_type and case_type not in VALID_CASE_TYPES:
            issues.append(
                case_issue(
                    case,
                    "ERROR",
                    "invalid_case_type",
                    f"用例类型为 {case_type}，应为 {', '.join(sorted(VALID_CASE_TYPES))}",
                    "用例类型",
                )
            )

        case_id = case["用例编号"]
        id_match = CASE_ID_PATTERN.match(case_id) if case_id else None
        if case_id and not id_match:
            issues.append(
                case_issue(
                    case,
                    "ERROR",
                    "invalid_case_id_format",
                    f"用例编号格式不正确：{case_id}，应为 模块名-类型-三位序号，"
                    f"类型取值 {', '.join(VALID_ID_TYPES)}，例如 登录-功能-001",
                    "用例编号",
                )
            )
        elif id_match and case_type:
            expected_case_type = ID_TYPE_TO_CASE_TYPE.get(id_match.group("type"))
            if expected_case_type and expected_case_type != case_type:
                issues.append(
                    case_issue(
                        case,
                        "ERROR",
                        "case_id_type_mismatch",
                        f"编号类型“{id_match.group('type')}”应对应用例类型“{expected_case_type}”，"
                        f"但用例类型为“{case_type}”",
                        "用例类型",
                    )
                )

        steps = case["操作步骤"]
        if steps and not re.search(r"(^|\n|<br\s*/?>)\s*\d+[.、]", steps, re.IGNORECASE):
            issues.append(
                case_issue(
                    case,
                    "WARN",
                    "unordered_steps",
                    "操作步骤建议使用 1. 2. 3. 的有序步骤",
                    "操作步骤",
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


def validate_id_sequence(cases: list[dict[str, str]]) -> list[Issue]:
    """同模块同类型下三位序号应从 001 连续递增，缺号或不从 001 开始时给出 WARN。"""
    issues: list[Issue] = []
    grouped: dict[tuple[str, str], list[tuple[int, dict[str, str]]]] = {}

    for case in cases:
        match = CASE_ID_PATTERN.match(case["用例编号"] or "")
        if not match:
            continue
        key = (match.group("module"), match.group("type"))
        grouped.setdefault(key, []).append((int(match.group("seq")), case))

    for (module, id_type), entries in grouped.items():
        sequences = sorted(seq for seq, _ in entries)
        expected = list(range(1, len(sequences) + 1))
        if sequences != expected:
            missing = sorted(set(expected) - set(sequences))
            missing_text = "、".join(f"{value:03d}" for value in missing)
            issues.append(
                text_issue(
                    "WARN",
                    "non_continuous_id_sequence",
                    f"{module}-{id_type} 编号序号不连续，缺少：{missing_text or '（起始号或顺序异常）'}",
                )
            )

    return issues


def validate_core_flow_coverage(cases: list[dict[str, str]]) -> list[Issue]:
    """核心交易链路模块应覆盖约定的关键场景关键词，缺失时给出 WARN。"""
    issues: list[Issue] = []
    modules_present = {case["功能模块"] for case in cases if case["功能模块"]}

    for module, keyword_groups in CORE_FLOW_KEYWORDS.items():
        if module not in modules_present:
            continue
        module_text = "".join(
            f"{case['测试场景']}{case['前置条件']}{case['操作步骤']}{case['预期结果']}".lower()
            for case in cases
            if case["功能模块"] == module
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

    duplicated_ids = duplicate_values(cases, lambda case: (case["用例编号"],))
    for case_id, duplicated_cases in duplicated_ids.items():
        locations = "；".join(case_location(case) for case in duplicated_cases)
        issues.append(
            text_issue(
                "ERROR",
                "duplicate_case_id",
                f"用例编号重复：{case_id[0]}，位置：{locations}",
            )
        )

    duplicated_scenarios = duplicate_values(
        cases, lambda case: (case["功能模块"], case["测试场景"])
    )
    for key, duplicated_cases in duplicated_scenarios.items():
        module, scenario = key
        locations = "；".join(case_location(case) for case in duplicated_cases)
        issues.append(
            text_issue(
                "ERROR",
                "duplicate_scenario",
                f"测试场景重复：{module} / {scenario}，位置：{locations}",
            )
        )

    duplicated_flows = duplicate_values(
        cases,
        lambda case: (
            case["功能模块"],
            case["前置条件"],
            case["操作步骤"],
            case["预期结果"],
        ),
    )
    for key, duplicated_cases in duplicated_flows.items():
        module = key[0]
        locations = "；".join(case_location(case) for case in duplicated_cases)
        issues.append(
            text_issue(
                "WARN",
                "duplicate_flow",
                f"疑似重复流程：{module}，位置：{locations}",
            )
        )

    return issues


def build_summary(
    case_files: list[Path],
    cases: list[dict[str, str]],
    issues: list[Issue],
    fixes: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    modules = Counter(case["功能模块"] for case in cases if case["功能模块"])
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
    issues.extend(validate_id_sequence(cases))
    issues.extend(validate_core_flow_coverage(cases))

    if args.json:
        print_json_report(case_files, cases, issues, fixes)
    else:
        print_text_report(case_files, cases, issues, args.summary_only, fixes)

    return 1 if has_blocking_issues(issues) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
