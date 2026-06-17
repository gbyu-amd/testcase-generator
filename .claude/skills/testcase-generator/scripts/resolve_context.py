#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按 REQ 编号解析生成测试用例所需的最小上下文。

用途：
    python scripts/resolve_context.py --req REQ-CPV-017
    python scripts/resolve_context.py --req REQ-CPV-017 --json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from case_utils import build_source_path, configure_output_encoding, ensure_under, project_root
from context_config import (
    CORE_FLOW_BY_MODULE,
    DEFAULT_RULES,
    DETAIL_RULES_ON_DEMAND,
    REFERENCE_BY_MODULE,
)


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(project_root().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def split_markdown_table_row(line: str) -> list[str]:
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


def clean_cell(value: str) -> str:
    value = value.strip()
    match = re.fullmatch(r"`(.+)`", value)
    return match.group(1) if match else value


def parse_requirements_index(index_path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    header: list[str] = []
    for line in index_path.read_text(encoding="utf-8-sig").splitlines():
        cells = split_markdown_table_row(line)
        if not cells:
            continue
        compact = ["".join(cell.split()) for cell in cells]
        if all(set(cell) <= {"-", ":"} for cell in compact):
            continue
        if "需求编号" in cells:
            header = cells
            continue
        if header and len(cells) == len(header):
            rows.append({name: clean_cell(value) for name, value in zip(header, cells)})
    return rows


def find_requirement(rows: list[dict[str, str]], req_id: str) -> dict[str, str]:
    normalized = req_id.strip().upper()
    for row in rows:
        if row.get("需求编号", "").upper() == normalized:
            return row
    raise SystemExit(f"未在 requirements_index.md 中找到需求编号：{req_id}")


def existing_paths(relative_paths: list[str]) -> list[str]:
    root = project_root()
    result: list[str] = []
    for relative_path in relative_paths:
        path = root / relative_path
        if path.exists():
            result.append(display_path(path))
    return result


def ui_has_assets(ui_dir: Path) -> bool:
    if not ui_dir.exists() or not ui_dir.is_dir():
        return False
    return any(path.is_file() and path.name.lower() != "readme.md" for path in ui_dir.iterdir())


def build_context(req_id: str, index_path: Path) -> dict[str, object]:
    root = project_root()
    row = find_requirement(parse_requirements_index(index_path), req_id)
    module_slug = row.get("模块", "")
    site_type = row.get("站点", "")
    requirement_file = root / row["需求文件"]
    ui_dir = root / row["UI 目录"]
    output_file = root / row.get("输出文件", "")

    reference_files = existing_paths(REFERENCE_BY_MODULE.get(module_slug, []))
    core_flows = existing_paths(CORE_FLOW_BY_MODULE.get(module_slug, []))
    rules = existing_paths(DEFAULT_RULES)
    detail_rules = existing_paths(DETAIL_RULES_ON_DEMAND)

    return {
        "req_id": row.get("需求编号", req_id),
        "original_id": row.get("原始编号", "-"),
        "title": row.get("需求标题", ""),
        "site_type": site_type,
        "module_slug": module_slug,
        "requirement_file": display_path(requirement_file),
        "ui_dir": display_path(ui_dir),
        "ui_available": ui_has_assets(ui_dir),
        "output_file": display_path(output_file),
        "reference_files": reference_files,
        "core_flow_files": core_flows,
        "rules_to_read": rules,
        "detail_rules_on_demand": detail_rules,
        "validate_command": f'python scripts/validate_cases.py --source "{display_path(output_file)}"',
        "export_command": f'python scripts/export_testcases.py --source "{display_path(output_file)}"',
        "notes": [
            "单 REQ 生成时优先读取 rules_to_read、requirement_file、ui_dir（仅 ui_available=true 时）和 reference_files。",
            "除非信息不足，不主动读取 current_prd.md 或全量 generation_rules。",
            "输出文件存在但无有效用例时，可视为初始化占位文件处理。",
        ],
    }


def print_markdown(context: dict[str, object]) -> None:
    print(f"# {context['req_id']} 生成上下文")
    print()
    print(f"- 需求标题：{context['title']}")
    print(f"- 站点分类：{context['site_type']}")
    print(f"- 模块：{context['module_slug']}")
    print(f"- 需求文件：`{context['requirement_file']}`")
    print(f"- UI 目录：`{context['ui_dir']}`")
    print(f"- UI 是否有实际素材：{context['ui_available']}")
    print(f"- 输出文件：`{context['output_file']}`")
    print()
    print("## 优先读取")
    for path in context["rules_to_read"]:
        print(f"- `{path}`")
    print(f"- `{context['requirement_file']}`")
    if context["ui_available"]:
        print(f"- `{context['ui_dir']}`")
    for path in context["reference_files"]:
        print(f"- `{path}`")
    for path in context["core_flow_files"]:
        print(f"- `{path}`")
    print()
    print("## 按需读取")
    for path in context["detail_rules_on_demand"]:
        print(f"- `{path}`")
    print()
    print("## 命令")
    print(f"- 校验：`{context['validate_command']}`")
    print(f"- 导出：`{context['export_command']}`")


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description="按 REQ 编号解析测试用例生成上下文。")
    parser.add_argument("--req", required=True, help="需求编号，例如 REQ-CPV-017")
    parser.add_argument(
        "--index",
        default=str(root / "inputs" / "requirements" / "requirements_index.md"),
        help="需求索引路径，默认 inputs/requirements/requirements_index.md",
    )
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    return parser.parse_args()


def main() -> int:
    configure_output_encoding()
    args = parse_args()
    root = project_root()
    index_path = ensure_under(build_source_path(args.index, root), root, "需求索引")
    context = build_context(args.req, index_path)
    if args.json:
        print(json.dumps(context, ensure_ascii=False, indent=2))
    else:
        print_markdown(context)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
