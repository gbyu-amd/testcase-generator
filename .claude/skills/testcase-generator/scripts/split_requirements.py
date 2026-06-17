#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将整份 Markdown PRD 按章节拆成独立需求文件，并为每个需求创建对应 UI 目录。

脚本只做机械拆分和目录初始化，不尝试替代人工确认需求边界。首次拆分后，
建议先检查 requirements_index.md，再按需调整单个需求文件和 UI 归属。
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from case_utils import build_source_path, configure_output_encoding, ensure_under, project_root
from context_config import MODULE_SLUGS, SITE_PUBLIC_KEYWORDS, output_file_for


HEADING_PATTERN = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$")
CPV_CODE_PATTERN = re.compile(r"CPV[\s-]*[A-Z]+[\s-]*\d+", re.IGNORECASE)


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(project_root().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    line_index: int
    path: tuple[str, ...]


@dataclass(frozen=True)
class RequirementSection:
    req_id: str
    title: str
    source_heading: str
    original_code: str
    site_type: str
    module_slug: str
    file_stem: str
    source_path: Path
    source_start_line: int
    source_end_line: int
    content: str


def strip_markdown_emphasis(value: str) -> str:
    value = value.replace("**", "").replace("__", "")
    return value.strip()


def normalize_code(value: str) -> str:
    return re.sub(r"[\s]+", "", value.upper()).replace("CPV-", "CPV-")


def slugify(value: str, fallback: str = "requirement") -> str:
    text = strip_markdown_emphasis(value).lower()
    text = re.sub(r"（.*?）|\(.*?\)", "", text)
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    if not text:
        return fallback
    if re.fullmatch(r"[\u4e00-\u9fff_]+", text):
        return fallback
    return text[:60].strip("_") or fallback


def detect_original_code(title: str) -> str:
    match = CPV_CODE_PATTERN.search(title)
    return normalize_code(match.group(0)) if match else ""


def detect_site_type(path: tuple[str, ...], title: str) -> str:
    full_text = " / ".join((*path, title))
    if any(keyword in full_text for keyword in SITE_PUBLIC_KEYWORDS):
        return "public_site"
    return "business_site"


def detect_module_slug(path: tuple[str, ...], title: str) -> str:
    candidates = [title, *reversed(path)]
    for candidate in candidates:
        clean = strip_markdown_emphasis(candidate)
        for keyword, slug in MODULE_SLUGS.items():
            if keyword in clean:
                return slug
    return slugify(path[-1] if path else title, fallback="general")


def parse_headings(lines: list[str]) -> list[Heading]:
    headings: list[Heading] = []
    stack: list[Heading] = []
    for index, line in enumerate(lines):
        match = HEADING_PATTERN.match(line)
        if not match:
            continue
        level = len(match.group("marks"))
        title = strip_markdown_emphasis(match.group("title"))
        while stack and stack[-1].level >= level:
            stack.pop()
        path = tuple(item.title for item in stack)
        heading = Heading(level=level, title=title, line_index=index, path=path)
        headings.append(heading)
        stack.append(heading)
    return headings


def should_split_heading(heading: Heading, min_level: int, max_level: int) -> bool:
    if heading.level < min_level or heading.level > max_level:
        return False
    title = heading.title.strip()
    if title in {"示例", "说明", "目录"}:
        return False
    return True


def find_section_end(lines: list[str], heading: Heading) -> int:
    for index in range(heading.line_index + 1, len(lines)):
        match = HEADING_PATTERN.match(lines[index])
        if match and len(match.group("marks")) <= heading.level:
            return index
    return len(lines)


def build_sections(
    prd_path: Path,
    lines: list[str],
    min_level: int,
    max_level: int,
    id_prefix: str,
    include_title_in_name: bool,
) -> list[RequirementSection]:
    headings = parse_headings(lines)
    selected = [
        heading
        for heading in headings
        if should_split_heading(heading, min_level=min_level, max_level=max_level)
    ]
    sections: list[RequirementSection] = []
    used_stems: set[str] = set()
    for sequence, heading in enumerate(selected, start=1):
        end_index = find_section_end(lines, heading)
        body = "\n".join(lines[heading.line_index:end_index]).strip()
        if not body:
            continue
        req_id = f"{id_prefix}-{sequence:03d}"
        original_code = detect_original_code(heading.title)
        module_slug = detect_module_slug(heading.path, heading.title)
        title_slug = slugify(heading.title, fallback=module_slug)
        file_stem = f"{req_id}_{title_slug}" if include_title_in_name else req_id
        if file_stem in used_stems:
            file_stem = f"{file_stem}_{sequence:03d}"
        used_stems.add(file_stem)
        sections.append(
            RequirementSection(
                req_id=req_id,
                title=heading.title,
                source_heading=" > ".join((*heading.path, heading.title)),
                original_code=original_code,
                site_type=detect_site_type(heading.path, heading.title),
                module_slug=module_slug,
                file_stem=file_stem,
                source_path=prd_path,
                source_start_line=heading.line_index + 1,
                source_end_line=end_index,
                content=body,
            )
        )
    return sections


def requirement_text(section: RequirementSection, requirements_root: Path, ui_root: Path) -> str:
    relative_source = display_path(section.source_path)
    ui_relative = display_path(ui_root / section.file_stem)
    return "\n".join(
        [
            f"# {section.req_id} {section.title}",
            "",
            "## 元信息",
            "",
            f"- 来源文档：`{relative_source}`",
            f"- 原始章节：{section.source_heading}",
            f"- 原始行号：{section.source_start_line}-{section.source_end_line}",
            f"- 原始需求编号：{section.original_code or '未识别'}",
            f"- 所属站点：{section.site_type}",
            f"- 模块目录：{section.module_slug}",
            f"- 关联 UI：`{ui_relative}`",
            "",
            "## 原始需求内容",
            "",
            section.content,
            "",
            "## 拆分确认",
            "",
            "- [ ] 章节边界已确认",
            "- [ ] 所属站点和模块已确认",
            "- [ ] 关联 UI 图已确认",
            "- [ ] 验收标准已确认",
            "",
        ]
    )


def ui_readme_text(section: RequirementSection, requirements_root: Path) -> str:
    requirement_path = (
        requirements_root / section.site_type / section.module_slug / f"{section.file_stem}.md"
    )
    return "\n".join(
        [
            f"# {section.req_id} {section.title} UI",
            "",
            f"- 关联需求：`{display_path(requirement_path)}`",
            f"- 原始章节：{section.source_heading}",
            "- 图片清单：",
            "  - 待补充",
            "- 页面说明：",
            "  - 待补充",
            "- 交互说明：",
            "  - 待补充",
            "",
        ]
    )


def index_text(sections: list[RequirementSection], requirements_root: Path, ui_root: Path) -> str:
    lines = [
        "# 需求拆分索引",
        "",
        "本文件由 `scripts/split_requirements.py` 生成，用于记录整份 PRD 拆分后的需求文件和 UI 目录映射。首次生成后请人工确认章节边界、模块归属和 UI 归属。",
        "",
        "| 需求编号 | 原始编号 | 需求标题 | 站点 | 模块 | 输出文件 | 需求文件 | UI 目录 | 原始章节 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for section in sections:
        req_file = (
            requirements_root
            / section.site_type
            / section.module_slug
            / f"{section.file_stem}.md"
        )
        ui_dir = ui_root / section.file_stem
        output_file = output_file_for(section.site_type, section.module_slug)
        lines.append(
            "| "
            + " | ".join(
                [
                    section.req_id,
                    section.original_code or "-",
                    section.title.replace("|", "\\|"),
                    section.site_type,
                    section.module_slug,
                    f"`{display_path(output_file)}`",
                    f"`{display_path(req_file)}`",
                    f"`{display_path(ui_dir)}`",
                    section.source_heading.replace("|", "\\|"),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def write_text_file(path: Path, content: str, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description="按 Markdown 标题拆分整份 PRD，并创建需求文件和 UI 目录。"
    )
    parser.add_argument("--prd", required=True, help="整份 PRD Markdown 文件路径")
    parser.add_argument(
        "--requirements-root",
        default=str(root / "inputs" / "requirements"),
        help="拆分需求输出目录，默认 inputs/requirements",
    )
    parser.add_argument(
        "--ui-root",
        default=str(root / "inputs" / "ui_design"),
        help="UI 目录输出位置，默认 inputs/ui_design",
    )
    parser.add_argument("--id-prefix", default="REQ-CPV", help="生成需求编号前缀")
    parser.add_argument("--min-level", type=int, default=3, help="参与拆分的最小标题级别")
    parser.add_argument("--max-level", type=int, default=4, help="参与拆分的最大标题级别")
    parser.add_argument(
        "--index-name",
        default="requirements_index.md",
        help="需求索引文件名",
    )
    parser.add_argument("--overwrite", action="store_true", help="覆盖已存在的拆分文件")
    parser.add_argument(
        "--include-title-in-name",
        action="store_true",
        help="文件名中追加标题 slug；长路径 Windows 环境不建议开启",
    )
    return parser.parse_args()


def main() -> int:
    configure_output_encoding()
    args = parse_args()
    root = project_root()

    prd_path = ensure_under(build_source_path(args.prd, root), root, "PRD 文件")
    requirements_root = ensure_under(
        build_source_path(args.requirements_root, root), root, "需求输出目录"
    )
    ui_root = ensure_under(build_source_path(args.ui_root, root), root, "UI 输出目录")

    lines = prd_path.read_text(encoding="utf-8-sig").splitlines()
    sections = build_sections(
        prd_path=prd_path,
        lines=lines,
        min_level=args.min_level,
        max_level=args.max_level,
        id_prefix=args.id_prefix,
        include_title_in_name=args.include_title_in_name,
    )
    if not sections:
        raise SystemExit("未识别到可拆分的需求章节，请调整 --min-level/--max-level。")

    written_requirements = 0
    written_ui_readmes = 0
    for section in sections:
        req_path = (
            requirements_root / section.site_type / section.module_slug / f"{section.file_stem}.md"
        )
        ui_dir = ui_root / section.file_stem
        if write_text_file(
            req_path,
            requirement_text(section, requirements_root=requirements_root, ui_root=ui_root),
            overwrite=args.overwrite,
        ):
            written_requirements += 1
        if write_text_file(
            ui_dir / "README.md",
            ui_readme_text(section, requirements_root=requirements_root),
            overwrite=args.overwrite,
        ):
            written_ui_readmes += 1

    index_path = requirements_root / args.index_name
    write_text_file(
        index_path,
        index_text(sections, requirements_root=requirements_root, ui_root=ui_root),
        overwrite=True,
    )

    print("需求拆分完成：")
    print(f"- PRD：{prd_path.relative_to(root)}")
    print(f"- 识别需求章节：{len(sections)}")
    print(f"- 新写入需求文件：{written_requirements}")
    print(f"- 新写入 UI README：{written_ui_readmes}")
    print(f"- 需求索引：{index_path.relative_to(root)}")
    if written_requirements < len(sections) or written_ui_readmes < len(sections):
        print("- 提示：部分文件已存在，未覆盖；如需重建请增加 --overwrite。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
