#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试用例生成上下文映射配置。

本文件只维护静态映射，供 `split_requirements.py` 和
`resolve_context.py` 复用，避免同一份模块/输出/参考文件映射散落在多个脚本中。
"""

from __future__ import annotations

from pathlib import Path

from case_utils import project_root


MODULE_SLUGS = {
    "首页工作台": "home_workspace",
    "年度计划设置": "annual_plan",
    "任务管理": "task_manage",
    "方案模版": "plan_template",
    "方案模板": "plan_template",
    "方案编制": "plan_compile",
    "项目监控": "project_monitor",
    "监控项目": "project_monitor",
    "工艺能力汇总": "process_capability_summary",
    "相关性分析": "correlation_analysis",
    "报告模版": "report_template",
    "报告模板": "report_template",
    "报告编制": "report_compile",
    "产品管理": "product_manage",
    "异步任务处理": "async_task",
    "用户管理": "user_manage",
    "部门管理": "department_manage",
    "岗位管理": "position_manage",
    "角色管理": "role_manage",
    "工作流配置": "workflow_config",
    "日志管理": "log_manage",
    "系统服务配置": "system_service",
    "个人中心": "personal_center",
    "审计追踪": "audit_trail",
    "多租户配置": "tenant_config",
    "统一门户管理": "portal_manage",
    "站点管理": "site_manage",
    "权限管理": "permission_manage",
    "数据分析工作台": "data_analysis",
    "数据分析": "data_analysis",
    "一键分析": "one_click_analysis",
    "产品工艺管理": "product_process_manage",
    "工序": "process_step",
    "操作": "operation",
    "关键设备": "critical_equipment",
    "参数与属性维护": "parameter_attribute",
    "工艺矩阵": "process_matrix",
    "质量规则配置": "quality_rule_config",
    "参考限配置": "reference_limit",
    "能力分析等级配置": "capability_level",
}

SITE_PUBLIC_KEYWORDS = (
    "公共管理",
    "统一门户",
    "站点管理",
    "系统服务",
    "用户登录日志",
    "日志管理",
    "用户管理",
    "部门管理",
    "岗位管理",
    "角色管理",
    "权限管理",
    "工作流配置",
    "个人中心",
    "多租户",
    "审计追踪",
    "登录页",
)

OUTPUT_FILE_BY_MODULE = {
    "home_workspace": "business_site/home_workspace_testcases.md",
    "annual_plan": "business_site/annual_plan_task_testcases.md",
    "task_manage": "business_site/annual_plan_task_testcases.md",
    "plan_template": "business_site/protocol_testcases.md",
    "plan_compile": "business_site/protocol_testcases.md",
    "project_monitor": "business_site/monitoring_item_testcases.md",
    "process_capability_summary": "business_site/monitoring_item_testcases.md",
    "correlation_analysis": "business_site/monitoring_item_testcases.md",
    "report_template": "business_site/report_testcases.md",
    "report_compile": "business_site/report_testcases.md",
    "product_manage": "business_site/product_master_data_testcases.md",
    "product_process_manage": "business_site/product_master_data_testcases.md",
    "process_step": "business_site/product_master_data_testcases.md",
    "operation": "business_site/product_master_data_testcases.md",
    "critical_equipment": "business_site/product_master_data_testcases.md",
    "parameter_attribute": "business_site/product_master_data_testcases.md",
    "process_matrix": "business_site/product_master_data_testcases.md",
    "quality_rule_config": "business_site/product_master_data_testcases.md",
    "reference_limit": "business_site/product_master_data_testcases.md",
    "capability_level": "business_site/product_master_data_testcases.md",
    "async_task": "business_site/system_config_async_task_testcases.md",
    "data_analysis": "business_site/data_analysis_testcases.md",
    "one_click_analysis": "business_site/one_click_analysis_testcases.md",
    "audit_trail": "public_site/audit_esignature_testcases.md",
    "tenant_config": "public_site/public_site_testcases.md",
    "portal_manage": "public_site/public_site_testcases.md",
    "site_manage": "public_site/public_site_testcases.md",
    "user_manage": "public_site/public_site_testcases.md",
    "department_manage": "public_site/public_site_testcases.md",
    "position_manage": "public_site/public_site_testcases.md",
    "role_manage": "public_site/public_site_testcases.md",
    "permission_manage": "public_site/public_site_testcases.md",
    "workflow_config": "public_site/system_config_async_task_testcases.md",
    "log_manage": "public_site/audit_esignature_testcases.md",
    "system_service": "public_site/system_config_async_task_testcases.md",
    "personal_center": "public_site/public_site_testcases.md",
    "general": "business_site/general_testcases.md",
}

REFERENCE_BY_MODULE = {
    "annual_plan": ["testcase_templates/modules/business_site/plan_manage/annual_plan_settings.md"],
    "task_manage": ["testcase_templates/modules/business_site/plan_manage/task_manage.md"],
    "plan_template": ["testcase_templates/modules/business_site/scheme_manage/scheme_templates.md"],
    "plan_compile": ["testcase_templates/modules/business_site/scheme_manage/scheme_formulation.md"],
    "project_monitor": ["testcase_templates/modules/business_site/scheme_execution/monitoring_items.md"],
    "process_capability_summary": ["testcase_templates/modules/business_site/scheme_execution/monitoring_items.md"],
    "correlation_analysis": ["testcase_templates/modules/business_site/scheme_execution/correlation_analysis.md"],
    "report_template": ["testcase_templates/modules/business_site/report_manage/report_templates.md"],
    "report_compile": ["testcase_templates/modules/business_site/report_manage/report_generation.md"],
    "audit_trail": [
        "testcase_templates/modules/public_site/audit_trail/audit_trail_permission_manage.md",
        "testcase_templates/modules/business_site/configuration_manage/audit_trail.md",
    ],
}

CORE_FLOW_BY_MODULE = {
    "data_analysis": ["knowledge_base/core_flows/data_analysis_flow.md"],
    "one_click_analysis": ["knowledge_base/core_flows/one_click_analysis_flow.md"],
    "project_monitor": ["knowledge_base/core_flows/cpv_business_flow.md"],
    "plan_compile": ["knowledge_base/core_flows/cpv_business_flow.md"],
    "report_compile": ["knowledge_base/core_flows/cpv_business_flow.md"],
    "annual_plan": ["knowledge_base/core_flows/cpv_business_flow.md"],
    "task_manage": ["knowledge_base/core_flows/cpv_business_flow.md"],
}

DEFAULT_RULES = [
    "generation_rules/quick_rules.md",
]

DETAIL_RULES_ON_DEMAND = [
    "generation_rules/testcase_writing_guidelines.md",
    "generation_rules/coverage_dimension_rules.md",
    "generation_rules/priority_rules.md",
    "generation_rules/difficulty_level_rules.md",
    "generation_rules/case_append_rules.md",
]


def output_file_for(site_type: str, module_slug: str) -> Path:
    relative = OUTPUT_FILE_BY_MODULE.get(module_slug)
    if relative:
        return project_root() / "outputs" / "origin_exports" / relative
    return project_root() / "outputs" / "origin_exports" / site_type / f"{module_slug}_testcases.md"
