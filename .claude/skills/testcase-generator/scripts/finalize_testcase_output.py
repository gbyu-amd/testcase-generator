#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用途：
    完成单个 Markdown 测试用例文件的最终交付闭环：
    1. 运行 validate_cases.py 校验。
    2. 校验通过后运行 export_testcases.py 导出 Excel。
    3. 回填 Markdown 元信息中的实际生成耗时。

说明：
    本脚本只包装现有校验和导出脚本，不替代用例质量规则。
    如果只回填“生成耗时”，且回填前已达到 0 ERROR / 0 WARN，则跳过二次校验。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from case_utils import (
    build_source_path,
    configure_output_encoding,
    ensure_under,
    project_root,
    read_text_file,
    write_text_file,
)


DURATION_RE = re.compile(r"^(生成耗时：).*$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"生成耗时：(?:待回填|约|预计)")


def parse_started_at(value: str) -> datetime:
    text = value.strip()
    if text.isdigit():
        return datetime.fromtimestamp(int(text))

    normalized = text.replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            pass

    raise argparse.ArgumentTypeError(
        "开始时间格式必须为 Unix 秒级时间戳、YYYY-MM-DD HH:MM 或 YYYY-MM-DD HH:MM:SS"
    )


def format_duration(started_at: datetime, ended_at: datetime) -> str:
    elapsed_seconds = max(0, int((ended_at - started_at).total_seconds()))
    minutes, seconds = divmod(elapsed_seconds, 60)
    if minutes == 0:
        return f"{seconds} 秒"
    if seconds == 0:
        return f"{minutes} 分钟"
    return f"{minutes} 分 {seconds} 秒"


def relative_to_root(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def run_command(
    args: list[str], root: Path, label: str, echo_output: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if echo_output and result.stdout:
        print(result.stdout, end="")
    if echo_output and result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"{label}失败，退出码：{result.returncode}")
    return result


def validate_source(root: Path, source: Path) -> dict[str, object]:
    result = run_command(
        [
            sys.executable,
            "scripts/validate_cases.py",
            "--source",
            relative_to_root(source, root),
            "--json",
        ],
        root,
        "校验",
        echo_output=False,
    )
    report = json.loads(result.stdout)
    errors, warnings = count_issues(report)
    summary = report.get("summary", {})
    case_count = summary.get("case_count", 0) if isinstance(summary, dict) else 0
    print(
        "校验完成："
        f"用例数量 {case_count}，"
        f"ERROR {errors}，WARN {warnings}"
    )
    return report


def count_issues(report: dict[str, object]) -> tuple[int, int]:
    issues = report.get("issues", [])
    errors = sum(1 for issue in issues if isinstance(issue, dict) and issue.get("severity") == "ERROR")
    warnings = sum(1 for issue in issues if isinstance(issue, dict) and issue.get("severity") == "WARN")
    return errors, warnings


def export_source(root: Path, source: Path, strict: bool) -> None:
    args = [
        sys.executable,
        "scripts/export_testcases.py",
        "--source",
        relative_to_root(source, root),
    ]
    if strict:
        args.append("--strict")
    run_command(args, root, "Excel 导出")


def backfill_duration(source: Path, duration_text: str) -> bool:
    content = read_text_file(source)
    replacement = (
        f"生成耗时：{duration_text}（从开始读取资料到校验和 Excel 导出完成）"
    )

    if DURATION_RE.search(content):
        updated = DURATION_RE.sub(replacement, content, count=1)
    else:
        raise RuntimeError("未找到“生成耗时：”元信息行，无法回填耗时")

    if updated == content:
        return False

    write_text_file(source, updated)
    return True


def ensure_no_duration_placeholder(source: Path) -> None:
    content = read_text_file(source)
    if PLACEHOLDER_RE.search(content):
        raise RuntimeError("Markdown 中仍存在待回填、约或预计耗时，请检查生成耗时元信息")


def parse_args(argv: list[str]) -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description="校验、导出并回填测试用例生成耗时")
    parser.add_argument(
        "--source",
        required=True,
        help="单个 Markdown 用例文件路径，例如 outputs/origin_exports/business_site/demo_testcases.md",
    )
    parser.add_argument(
        "--started-at",
        required=True,
        type=parse_started_at,
        help="生成开始时间，支持 Unix 秒级时间戳、YYYY-MM-DD HH:MM 或 YYYY-MM-DD HH:MM:SS",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="存在 ERROR 或 WARN 时停止导出；默认只在 ERROR 时停止",
    )
    parser.add_argument(
        "--force-final-validate",
        action="store_true",
        help="回填耗时后强制再运行一次 validate_cases.py",
    )
    parser.set_defaults(root=root)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    configure_output_encoding()
    args = parse_args(argv)
    root: Path = args.root
    source = ensure_under(build_source_path(args.source, root), root, "source")

    if source.suffix.lower() != ".md":
        print("处理失败：--source 必须指向单个 Markdown 文件", file=sys.stderr)
        return 1

    try:
        validation_report = validate_source(root, source)
        errors, warnings = count_issues(validation_report)
        if errors:
            print(f"校验存在 {errors} 个 ERROR，停止导出和耗时回填。", file=sys.stderr)
            return 1
        if args.strict and warnings:
            print(f"严格模式下校验存在 {warnings} 个 WARN，停止导出和耗时回填。", file=sys.stderr)
            return 1

        export_source(root, source, args.strict)

        duration_text = format_duration(args.started_at, datetime.now())
        changed = backfill_duration(source, duration_text)
        ensure_no_duration_placeholder(source)

        if args.force_final_validate or warnings or not changed:
            validate_source(root, source)
        else:
            print("仅回填生成耗时，且回填前已达到 0 ERROR / 0 WARN，跳过二次校验。")

        print(f"已回填生成耗时：{duration_text}")
        return 0
    except Exception as error:
        print(f"处理失败：{error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
