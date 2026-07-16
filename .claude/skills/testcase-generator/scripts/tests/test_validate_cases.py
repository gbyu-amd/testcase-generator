# -*- coding: utf-8 -*-
"""validate_cases 核心纯函数单元测试。"""

from __future__ import annotations

from validate_cases import extract_one_click_reason


class TestExtractOneClickReason:
    def test_different_methods_normalize_to_same_reason(self) -> None:
        # 两个方法名（NP控制图 / P控制图）剥离后原因核心均为空
        np_reason = extract_one_click_reason("未分析NP控制图一键分析成功")
        p_reason = extract_one_click_reason("未分析P控制图一键分析成功")
        assert np_reason == p_reason == ""

    def test_reason_extracted_with_method_suffix(self) -> None:
        reason = extract_one_click_reason("字段缺失NP控制图未分析一键分析成功")
        assert reason == "字段缺失"

    def test_reason_extracted_with_abnormal_state(self) -> None:
        reason = extract_one_click_reason("数据源替换P控制图未分析一键分析异常")
        assert reason == "数据源替换"

    def test_pure_reason_without_structural_words(self) -> None:
        reason = extract_one_click_reason("字段缺失")
        assert reason == "字段缺失"

    def test_empty_string(self) -> None:
        assert extract_one_click_reason("") == ""
