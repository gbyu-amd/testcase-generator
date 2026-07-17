# -*- coding: utf-8 -*-
"""case_utils 核心纯函数单元测试。"""

from __future__ import annotations

from case_utils import (
    FIXED_CASE_HEADERS,
    infer_case_difficulty_with_reason,
    is_case_header,
)


# ---------------------------------------------------------------------------
# is_case_header
# ---------------------------------------------------------------------------


class TestCaseHeader:
    def test_standard_three_level_header(self) -> None:
        cells = ["一级分组", "二级分组", "三级分组"] + FIXED_CASE_HEADERS
        assert is_case_header(cells) is True

    def test_extended_four_level_header(self) -> None:
        cells = [
            "一级分组",
            "二级分组",
            "三级分组",
            "四级分组",
        ] + FIXED_CASE_HEADERS
        assert is_case_header(cells) is True

    def test_missing_case_name_returns_false(self) -> None:
        # 用例名称被移除后，表头尾部不再等于 FIXED_CASE_HEADERS
        cells = ["一级分组", "二级分组", "三级分组"] + FIXED_CASE_HEADERS[1:]
        assert is_case_header(cells) is False

    def test_duplicate_cell_returns_false(self) -> None:
        cells = [
            "一级分组",
            "一级分组",
            "二级分组",
            "三级分组",
        ] + FIXED_CASE_HEADERS
        assert is_case_header(cells) is False

    def test_group_level_out_of_order_returns_false(self) -> None:
        cells = [
            "二级分组",
            "一级分组",
            "三级分组",
        ] + FIXED_CASE_HEADERS
        assert is_case_header(cells) is False

    def test_empty_list_returns_false(self) -> None:
        assert is_case_header([]) is False


# ---------------------------------------------------------------------------
# infer_case_difficulty_with_reason
# ---------------------------------------------------------------------------


def _case(
    title: str = "",
    description: str = "",
    precondition: str = "",
    steps: str = "",
    expectation: str = "",
) -> dict[str, str]:
    """构造最小可用的 case dict，只填难度推断读取的字段。"""
    return {
        "用例名称": title,
        "用例描述": description,
        "前置条件": precondition,
        "用例步骤": steps,
        "预期结果": expectation,
    }


def _numbered_steps(count: int) -> str:
    return "\n".join(f"{index}. 步骤{index}" for index in range(1, count + 1))


def _lines(count: int, prefix: str = "前置") -> str:
    return "\n".join(f"{prefix}{index}" for index in range(1, count + 1))


class TestInferCaseDifficulty:
    def test_difficult_high_confidence_keyword_in_title(self) -> None:
        case = _case(title="数据迁移到新环境", steps=_numbered_steps(2))
        difficulty, reasons = infer_case_difficulty_with_reason(case)
        assert difficulty == "困难"
        assert reasons

    def test_difficult_high_confidence_keyword_in_step(self) -> None:
        case = _case(
            title="使用外部工具对比",
            steps="1. 使用minitab对比数据",
        )
        difficulty, reasons = infer_case_difficulty_with_reason(case)
        assert difficulty == "困难"
        assert reasons

    def test_difficult_combination_import_and_cross_env(self) -> None:
        case = _case(
            title="导入数据校验",
            steps="1. 跨环境验证数据一致性",
        )
        difficulty, reasons = infer_case_difficulty_with_reason(case)
        assert difficulty == "困难"
        assert reasons

    def test_difficult_title_only_keyword(self) -> None:
        case = _case(title="超出参考线检查展示", steps=_numbered_steps(2))
        difficulty, reasons = infer_case_difficulty_with_reason(case)
        assert difficulty == "困难"
        assert reasons

    def test_simple_field_validation_priority(self) -> None:
        case = _case(
            title="必填字段校验",
            precondition=_lines(1),
            steps=_numbered_steps(2),
            expectation=_lines(1, prefix="结果"),
        )
        difficulty, reasons = infer_case_difficulty_with_reason(case)
        assert difficulty == "简单"
        assert reasons

    def test_simple_import_template_download_priority(self) -> None:
        case = _case(
            title="导入模板下载",
            precondition=_lines(1),
            steps=_numbered_steps(2),
            expectation=_lines(2, prefix="结果"),
        )
        difficulty, reasons = infer_case_difficulty_with_reason(case)
        assert difficulty == "简单"
        assert reasons

    def test_score_difficult_non_ui_non_import(self) -> None:
        case = _case(
            title="综合场景验证",
            precondition=_lines(4),
            steps=_numbered_steps(6),
            expectation=_lines(4, prefix="结果"),
        )
        difficulty, reasons = infer_case_difficulty_with_reason(case)
        assert difficulty == "困难"
        assert reasons

    def test_score_normal_medium_complexity(self) -> None:
        case = _case(
            title="常规业务流程验证",
            precondition=_lines(2),
            steps=_numbered_steps(3),
            expectation=_lines(2, prefix="结果"),
        )
        difficulty, reasons = infer_case_difficulty_with_reason(case)
        assert difficulty == "一般"
        assert reasons

    def test_score_simple_low_complexity(self) -> None:
        case = _case(
            title="常规查看操作",
            precondition=_lines(1),
            steps=_numbered_steps(2),
            expectation=_lines(1, prefix="结果"),
        )
        difficulty, reasons = infer_case_difficulty_with_reason(case)
        assert difficulty == "简单"
        assert reasons

    def test_ui_case_capped_at_normal(self) -> None:
        case = _case(
            title="UI校验页面展示",
            description="UI",
            precondition=_lines(4),
            steps=_numbered_steps(6),
            expectation=_lines(2, prefix="结果"),
        )
        difficulty, reasons = infer_case_difficulty_with_reason(case)
        assert difficulty == "一般"
        assert reasons
