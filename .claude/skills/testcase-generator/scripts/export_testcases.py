#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用途：
    将 Markdown 测试用例表格导出为 Excel xlsx 文件，便于评审、归档或交付。
    脚本会解析标准表头的测试用例表格，并生成带冻结表头、列宽和自动筛选的工作簿。

默认读取：
    outputs/origin_exports/**/*_testcases.md

默认输出：
    outputs/excel_exports/<site_type>/测试用例导出_YYYYMMDD_HHMMSS.xlsx

适用场景：
    - 将 Agent 生成在 outputs/origin_exports/ 的用例导出为 Excel。
    - 使用 --source 导出指定模块或指定目录的 Markdown 用例。
    - 未指定 --output 时，按 public_site / business_site 分类输出。
    - 导出前自动执行完整校验；存在 ERROR 时停止导出。
    - 使用 --strict 在存在 ERROR 或 WARN 时都停止导出。

导出前校验：
    复用 validate_cases.py 的完整校验规则，避免校验失败的用例被导出。

示例：
    python scripts/export_testcases.py
    python scripts/export_testcases.py --source outputs/origin_exports/business_site/data_analysis_testcases.md
    python scripts/export_testcases.py --strict -o data_analysis_testcases.xlsx

本脚本只使用 Python 标准库，不需要额外安装依赖。
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

from case_utils import (
    EXPECTED_HEADERS,
    build_source_path,
    configure_output_encoding,
    discover_case_files,
    ensure_under,
    parse_case_file,
    project_root,
)
from validate_cases import (
    format_issue,
    has_blocking_issues,
    text_issue,
    validate_case_rows,
    validate_core_flow_coverage,
    validate_duplicates,
    validate_id_sequence,
)

INVALID_XML_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")

# Excel 样式索引（对应 styles_xml 中 cellXfs 的顺序）
_STYLE_DEFAULT = 0   # 未使用的默认样式占位
_STYLE_HEADER = 1    # 表头：加粗、绿色背景、居中
_STYLE_DATA = 2      # 数据行：带边框、顶部对齐、自动换行
SITE_TYPES = ("public_site", "business_site")


def column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def safe_xml_text(value: str) -> str:
    value = INVALID_XML_CHARS.sub("", value)
    return escape(value, entities={'"': "&quot;"})


def cell_xml(row_index: int, column_index: int, value: str, style_index: int) -> str:
    reference = f"{column_name(column_index)}{row_index}"
    text = safe_xml_text(value)
    return (
        f'<c r="{reference}" t="inlineStr" s="{style_index}">'
        f'<is><t xml:space="preserve">{text}</t></is></c>'
    )


def row_xml(row_index: int, values: list[str], style_index: int) -> str:
    cells = [
        cell_xml(row_index, column_index, value, style_index)
        for column_index, value in enumerate(values, start=1)
    ]
    height = 24 if row_index == 1 else 64
    return f'<row r="{row_index}" ht="{height}" customHeight="1">{"".join(cells)}</row>'


def worksheet_xml(headers: list[str], cases: list[dict[str, str]]) -> str:
    max_row = len(cases) + 1
    max_col = len(headers)
    dimension = f"A1:{column_name(max_col)}{max_row}"
    rows = [row_xml(1, headers, _STYLE_HEADER)]
    rows.extend(
        row_xml(row_index, [case[header] for header in headers], _STYLE_DATA)
        for row_index, case in enumerate(cases, start=2)
    )

    column_widths = [16, 16, 16, 36, 10, 12, 16, 36, 48, 52, 24, 18, 14, 24, 18, 18]
    cols = "".join(
        f'<col min="{index}" max="{index}" width="{width}" customWidth="1"/>'
        for index, width in enumerate(column_widths, start=1)
    )

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <dimension ref="{dimension}"/>
  <sheetViews>
    <sheetView workbookViewId="0">
      <pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>
    </sheetView>
  </sheetViews>
  <cols>{cols}</cols>
  <sheetData>{"".join(rows)}</sheetData>
  <autoFilter ref="{dimension}"/>
</worksheet>'''


def styles_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2">
    <font><sz val="11"/><name val="Microsoft YaHei"/></font>
    <font><b/><sz val="11"/><name val="Microsoft YaHei"/><color rgb="FFFFFFFF"/></font>
  </fonts>
  <fills count="3">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF38761D"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border>
      <left style="thin"><color rgb="FFD9EAD3"/></left>
      <right style="thin"><color rgb="FFD9EAD3"/></right>
      <top style="thin"><color rgb="FFD9EAD3"/></top>
      <bottom style="thin"><color rgb="FFD9EAD3"/></bottom>
      <diagonal/>
    </border>
  </borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="3">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center" wrapText="1"/>
    </xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1">
      <alignment vertical="top" wrapText="1"/>
    </xf>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''


def write_xlsx(output_path: Path, cases: list[dict[str, str]]) -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    files = {
        "[Content_Types].xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>''',
        "_rels/.rels": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>''',
        "xl/workbook.xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="测试用例" sheetId="1" r:id="rId1"/></sheets>
</workbook>''',
        "xl/_rels/workbook.xml.rels": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>''',
        "xl/worksheets/sheet1.xml": worksheet_xml(EXPECTED_HEADERS, cases),
        "xl/styles.xml": styles_xml(),
        "docProps/core.xml": f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:dcmitype="http://purl.org/dc/dcmitype/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:creator>淘宝功能测试用例生成器</dc:creator>
  <cp:lastModifiedBy>淘宝功能测试用例生成器</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>''',
        "docProps/app.xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
    xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Python 标准库</Application>
  <DocSecurity>0</DocSecurity>
  <ScaleCrop>false</ScaleCrop>
  <HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>工作表</vt:lpstr></vt:variant><vt:variant><vt:i4>1</vt:i4></vt:variant></vt:vector></HeadingPairs>
  <TitlesOfParts><vt:vector size="1" baseType="lpstr"><vt:lpstr>测试用例</vt:lpstr></vt:vector></TitlesOfParts>
</Properties>''',
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for archive_path, content in files.items():
            archive.writestr(archive_path, content)


def default_output_path(output_dir: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return output_dir / f"测试用例导出_{timestamp}.xlsx"


def site_type_for_case_file(case_file: Path, origin_dir: Path) -> str | None:
    try:
        relative = case_file.resolve().relative_to(origin_dir.resolve())
    except ValueError:
        return None

    if relative.parts and relative.parts[0] in SITE_TYPES:
        return relative.parts[0]
    return None


def group_case_files_by_site(
    case_files: list[Path], origin_dir: Path
) -> dict[str | None, list[Path]]:
    groups: dict[str | None, list[Path]] = {}
    for case_file in case_files:
        site_type = site_type_for_case_file(case_file, origin_dir)
        groups.setdefault(site_type, []).append(case_file)
    return groups


def parse_args(argv: list[str]) -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description="将 Markdown 测试用例表格导出为 xlsx 文件"
    )
    parser.add_argument(
        "--source",
        default=str(root / "outputs" / "origin_exports"),
        help="输入文件或目录，默认扫描 outputs/origin_exports/**/*_testcases.md",
    )
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "输出文件名或路径。相对路径会保存到 outputs/excel_exports/；"
            "未指定时按 source 所属站点分类输出"
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="发现 ERROR 或 WARN 时都停止导出；默认只在 ERROR 时停止",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="导出成功后清理本次输出目录下的历史 xlsx，仅保留本次导出文件",
    )
    return parser.parse_args(argv)


def clean_old_exports(output_dir: Path, keep: Path) -> list[Path]:
    keep = keep.resolve()
    removed: list[Path] = []
    for existing in output_dir.glob("*.xlsx"):
        if existing.resolve() == keep:
            continue
        try:
            existing.unlink()
            removed.append(existing)
        except OSError as exc:
            # 文件可能被 Excel 等进程占用，跳过并提示，不中断导出流程
            print(f"警告：无法删除历史文件 {existing}：{exc}", file=sys.stderr)
    return removed


def build_output_path(output_arg: str | None, output_dir: Path) -> Path:
    if not output_arg:
        return default_output_path(output_dir)

    output_path = Path(output_arg)
    if not output_path.is_absolute():
        output_path = output_dir / output_path
    if output_path.suffix.lower() != ".xlsx":
        output_path = output_path.with_suffix(".xlsx")
    return output_path


def main(argv: list[str]) -> int:
    configure_output_encoding()
    root = project_root()
    output_dir = root / "outputs" / "excel_exports"
    origin_dir = root / "outputs" / "origin_exports"
    args = parse_args(argv)

    try:
        source = ensure_under(build_source_path(args.source, root), root, "输入路径")
        case_files = discover_case_files(source)
    except (FileNotFoundError, ValueError) as error:
        print(f"导出失败：{error}", file=sys.stderr)
        return 1

    if not case_files:
        print("导出失败：未找到任何测试用例 Markdown 文件", file=sys.stderr)
        return 1

    groups = group_case_files_by_site(case_files, origin_dir)
    if args.output:
        try:
            output_path = ensure_under(
                build_output_path(args.output, output_dir), output_dir, "输出路径"
            )
        except ValueError as error:
            print(f"导出失败：{error}", file=sys.stderr)
            return 1
        export_groups = [("all", case_files, output_path)]
    else:
        export_groups = []
        for site_type, files in sorted(groups.items(), key=lambda item: item[0] or ""):
            group_output_dir = output_dir / site_type if site_type else output_dir
            export_groups.append((site_type or "未分类", files, default_output_path(group_output_dir)))

    exported_count = 0
    for group_name, group_files, output_path in export_groups:
        cases: list[dict[str, str]] = []
        warnings: list[str] = []
        for case_file in group_files:
            parsed_cases, parse_warnings = parse_case_file(case_file)
            cases.extend(parsed_cases)
            warnings.extend(parse_warnings)

        if not cases:
            print(f"导出失败：{group_name} 未解析到测试用例", file=sys.stderr)
            for warning in warnings:
                print(f"- {warning}", file=sys.stderr)
            return 1

        validation_issues = [
            text_issue("ERROR", "parse_error", warning) for warning in warnings
        ]
        validation_issues.extend(validate_case_rows(cases))
        validation_issues.extend(validate_duplicates(cases))
        validation_issues.extend(validate_id_sequence(cases))
        validation_issues.extend(validate_core_flow_coverage(cases))

        if validation_issues:
            print(f"导出前校验结果（{group_name}）：")
            for issue in validation_issues:
                print(f"- {format_issue(issue)}")
            if has_blocking_issues(validation_issues, strict=args.strict):
                if args.strict:
                    print(
                        "已启用 --strict，存在 ERROR 或 WARN，停止导出。",
                        file=sys.stderr,
                    )
                else:
                    print("存在 ERROR，停止导出。", file=sys.stderr)
                return 1
            print()

        write_xlsx(output_path, cases)

        removed_files: list[Path] = []
        if args.clean:
            removed_files = clean_old_exports(output_path.parent, output_path)

        modules = sorted(
            {
                " / ".join(
                    group
                    for group in (
                        case.get("一级分组", ""),
                        case.get("二级分组", ""),
                        case.get("三级分组", ""),
                    )
                    if group
                )
                for case in cases
                if case.get("一级分组")
            }
        )
        print("已导出测试用例 Excel：")
        print(f"- 站点分类：{group_name}")
        print(f"- 文件路径：{output_path}")
        print(f"- 用例数量：{len(cases)}")
        print(f"- 覆盖模块：{', '.join(modules)}")
        if args.clean:
            print(f"- 已清理历史文件：{len(removed_files)} 个")
        exported_count += 1

    if exported_count > 1:
        print(f"共导出 {exported_count} 个 Excel 文件。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
