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
    "用例编号",
    "功能模块",
    "测试场景",
    "优先级",
    "前置条件",
    "操作步骤",
    "预期结果",
    "用例类型",
    "来源",
]

VALID_PRIORITIES = {"P0", "P1", "P2"}


def configure_output_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def is_under(path: Path, root: Path) -> bool:
    path = path.resolve()
    root = root.resolve()
    return os.path.commonpath([str(path), str(root)]) == str(root)


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
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    value = value.replace("<br />", "\n")
    return value.strip()


def parse_case_file(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    warnings: list[str] = []
    cases: list[dict[str, str]] = []

    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
        lines = path.read_text(encoding="utf-8").splitlines()

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
        case_files = set(source.rglob("*_testcases.md"))
        case_files.update(source.rglob("testcases.md"))
        return sorted(case_files)
    raise FileNotFoundError(f"输入路径不存在：{source}")
