#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用例脚本公共工具。

本模块集中维护测试用例表头、路径安全检查、Markdown 表格解析和文件发现逻辑。
`validate_cases.py` 和 `export_testcases.py` 都依赖这里的公共能力，避免脚本之间互相承担不属于自身职责的工具函数。
"""

from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path
from typing import Iterable


EXPECTED_HEADERS = [
    "一级分组",
    "二级分组",
    "三级分组",
    "用例名称",
    "优先级",
    "创建人",
    "用例描述",
    "前置条件",
    "用例步骤",
    "预期结果",
    "备注",
    "用例标签",
    "是否自动化",
    "关联接口",
    "用例测试类",
    "关联项目",
]

REQUIRED_HEADERS = [
    "一级分组",
    "用例名称",
    "优先级",
    "创建人",
    "用例描述",
    "前置条件",
    "用例步骤",
    "预期结果",
    "备注",
    "用例标签",
]

VALID_PRIORITIES = {"P0", "P1", "P2"}
DIFFICULTY_LEVELS = ("简单", "一般", "困难")


def configure_output_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def is_under(path: Path, root: Path) -> bool:
    # 使用 Path.is_relative_to() 进行路径包含判断，在 Windows 大小写不敏感
    # 的文件系统上也能正确处理大小写不一致的路径（Python 3.9+）。
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def ensure_under(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve()
    if not is_under(resolved, root):
        raise ValueError(f"{label} 必须位于项目目录内：{root}")
    return resolved


def build_source_path(source_arg: str, root: Path) -> Path:
    source_path = Path(source_arg)
    if not source_path.is_absolute():
        source_path = root / source_path
    return source_path


def windows_long_path(path: Path) -> str:
    """Return a filesystem path that works with long Windows paths."""
    resolved = str(path.resolve())
    if os.name != "nt" or resolved.startswith("\\\\?\\"):
        return resolved
    return "\\\\?\\" + resolved


def read_text_file(path: Path, encoding: str = "utf-8") -> str:
    with open(windows_long_path(path), encoding=encoding) as file:
        return file.read()


def write_text_file(path: Path, content: str, encoding: str = "utf-8") -> None:
    with open(windows_long_path(path), "w", encoding=encoding) as file:
        file.write(content)


def split_markdown_row(line: str) -> list[str]:
    text = line.strip()
    if not text.startswith("|") or not text.endswith("|"):
        return []

    text = text[1:-1]
    cells: list[str] = []
    current: list[str] = []

    for index, char in enumerate(text):
        if char == "|" and (index == 0 or text[index - 1] != "\\"):
            cells.append("".join(current).replace(r"\|", "|").strip())
            current = []
        else:
            current.append(char)

    cells.append("".join(current).replace(r"\|", "|").strip())
    return cells


def is_separator_row(cells: Iterable[str]) -> bool:
    normalized = ["".join(cell.split()) for cell in cells]
    return bool(normalized) and all(
        cell and set(cell) <= {"-", ":"} and "-" in cell for cell in normalized
    )


def normalize_cell(value: str) -> str:
    value = html.unescape(value.strip())
    # <br\s*/?> 的正则已能匹配所有变体（<br>、<br/>、<br />），无需额外 replace
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    return value.strip()


def split_case_tags(value: str) -> list[str]:
    """按项目约定拆分用例标签，兼容中文和英文分号。"""
    return [
        tag.strip()
        for tag in re.split(r"[;；]", value or "")
        if tag and tag.strip()
    ]


def count_effective_steps(value: str) -> int:
    """统计有效执行步骤，登录动作不计入。"""
    normalized = normalize_cell(value)
    lines = [line.strip() for line in normalized.splitlines() if line.strip()]
    numbered_lines = [
        line for line in lines if re.match(r"^\d+[.、]\s*", line)
    ]
    candidates = numbered_lines or lines
    return sum(1 for line in candidates if "登录" not in line)


def count_non_empty_lines(value: str) -> int:
    normalized = normalize_cell(value)
    return len([line for line in normalized.splitlines() if line.strip()])


def _contains_any(text: str, keywords: Iterable[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _contains_all(text: str, keywords: Iterable[str]) -> bool:
    return all(keyword in text for keyword in keywords)


def _normalize_keyword_text(*values: str) -> str:
    return "".join("\n".join(values).split()).lower()


def infer_case_difficulty(case: dict[str, str]) -> str:
    """根据 difficulty_level_rules.md 的关键字规则推断用例难度。"""
    title_text = case.get("用例名称", "")
    step_text = case.get("用例步骤", "")
    expectation_text = case.get("预期结果", "")

    normalized_title_text = _normalize_keyword_text(title_text)
    normalized_step_expectation_text = _normalize_keyword_text(step_text, expectation_text)
    normalized_combination_text = _normalize_keyword_text(title_text, step_text)
    normalized_simple_text = _normalize_keyword_text(title_text, step_text, expectation_text)

    difficult_high_confidence_keywords = [
        "一键分析",
        "一键更新",
        "数据迁移",
        "跨环境",
        "第三方",
        "minitab",
        "多角色",
        "多人",
        "会签",
        "电子签名",
        "审批",
        "审核",
        "转审",
        "加签",
        "批准",
        "工作流",
        "数据完整性",
        "一致性验证",
        "分析结果数据正确性校验",
        "报告审批",
        "报告批准",
        "报告生效",
        "报告回推",
        "报告链路",
    ]

    general_high_confidence_keywords = [
        "导入",
        "批量导出",
        "跨页面",
        "跨模块",
        "审计追踪详情",
        "批量删除",
        "组合搜索",
        "组合查询",
    ]

    if _contains_any(normalized_title_text, difficult_high_confidence_keywords):
        return "困难"
    if _contains_any(normalized_title_text, general_high_confidence_keywords):
        return "一般"

    if _contains_any(normalized_step_expectation_text, difficult_high_confidence_keywords):
        return "困难"

    general_step_expectation_keywords = [
        "导入",
        "跨页面",
        "跨模块",
    ]
    if _contains_any(normalized_step_expectation_text, general_step_expectation_keywords):
        return "一般"

    difficult_keyword_combinations = [
        ("报告", "审批"),
        ("报告", "审核"),
        ("报告", "批准"),
        ("报告", "生效"),
        ("报告", "回推"),
        ("跨模块", "校验"),
    ]
    if any(
        _contains_all(normalized_combination_text, combination)
        for combination in difficult_keyword_combinations
    ):
        return "困难"

    general_keyword_combinations = [
        ("批量", "删除"),
        ("批量", "导出"),
        ("组合", "搜索"),
        ("组合", "查询"),
        ("审计追踪", "详情"),
        ("查看", "详情"),
        ("报告", "生成"),
        ("报告", "导出"),
    ]
    if any(
        _contains_all(normalized_combination_text, combination)
        for combination in general_keyword_combinations
    ):
        return "一般"

    simple_keywords = [
        "列表页",
        "翻页",
        "排序",
        "筛选重置",
        "刷新",
        "启用/停用",
        "启用",
        "停用",
        "重置",
        "单项操作",
        "单页面提交",
        "新增",
        "增加",
        "添加",
        "编辑",
        "删除",
        "搜索",
        "查询",
        "单字段校验",
        "必填",
        "长度",
        "格式提示",
        "下拉多选",
        "下拉选项",
        "提示语校验",
        "导出",
        "单文件导出",
    ]
    if _contains_any(normalized_simple_text, simple_keywords):
        return "简单"

    precondition_count = count_non_empty_lines(case.get("前置条件", ""))
    step_count = count_effective_steps(case.get("用例步骤", ""))
    expectation_count = count_non_empty_lines(case.get("预期结果", ""))

    if precondition_count > 3 or step_count > 5 or expectation_count >= 3:
        return "困难"
    if precondition_count <= 1 and step_count <= 2 and expectation_count <= 1:
        return "简单"
    return "一般"


def merge_difficulty_tag(existing_tags: str, difficulty: str) -> str:
    """用例标签只保留难度等级。"""
    return difficulty


def apply_difficulty_tag(case: dict[str, str]) -> dict[str, str]:
    updated = dict(case)
    difficulty = infer_case_difficulty(updated)
    updated["用例标签"] = merge_difficulty_tag(updated.get("用例标签", ""), difficulty)
    return updated


def apply_difficulty_tags(cases: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [apply_difficulty_tag(case) for case in cases]


def parse_case_file(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    warnings: list[str] = []
    cases: list[dict[str, str]] = []

    try:
        lines = read_text_file(path, encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
        lines = read_text_file(path, encoding="utf-8").splitlines()

    index = 0
    found_table = False
    while index < len(lines):
        cells = [normalize_cell(cell) for cell in split_markdown_row(lines[index])]
        if cells != EXPECTED_HEADERS:
            index += 1
            continue

        found_table = True
        index += 1

        if index < len(lines):
            separator_cells = split_markdown_row(lines[index])
            if is_separator_row(separator_cells):
                index += 1

        # 遇到非表格行时停止当前表格的解析；外层 while 循环会继续向下
        # 扫描，因此同一文件中的多张表格（如追加记录、需求覆盖率对照表）
        # 都能被正确识别和解析。
        while index < len(lines):
            row_line = lines[index]
            if not row_line.strip().startswith("|"):
                break

            row_cells = split_markdown_row(row_line)
            if is_separator_row(row_cells):
                index += 1
                continue

            normalized_cells = [normalize_cell(cell) for cell in row_cells]
            if len(normalized_cells) != len(EXPECTED_HEADERS):
                warnings.append(
                    f"{path} 第 {index + 1} 行列数为 {len(normalized_cells)}，"
                    f"期望 {len(EXPECTED_HEADERS)}，已跳过"
                )
                index += 1
                continue

            case = dict(zip(EXPECTED_HEADERS, normalized_cells))
            case["_source_file"] = str(path)
            case["_source_line"] = str(index + 1)
            cases.append(case)
            index += 1

    if not found_table:
        warnings.append(f"{path} 未找到标准测试用例表格")

    return cases, warnings


def discover_case_files(source: Path) -> list[Path]:
    if source.is_file():
        return [source]
    if source.is_dir():
        if "testcase_templates" in source.parts and "modules" in source.parts:
            skipped_names = {"menu_index.md", "module_overview.md", "README.md"}
            return sorted(
                path
                for path in source.rglob("*.md")
                if path.name not in skipped_names
                and path.name.endswith("_template.md")
            )

        # 仅匹配以 _testcases.md 结尾的文件，带时间戳的"另存"文件
        # （如 login_testcases_20260613.md）不在默认扫描范围内，需要
        # 通过 --source 显式指定才能被处理。
        return sorted(source.rglob("*_testcases.md"))
    raise FileNotFoundError(f"输入路径不存在：{source}")
