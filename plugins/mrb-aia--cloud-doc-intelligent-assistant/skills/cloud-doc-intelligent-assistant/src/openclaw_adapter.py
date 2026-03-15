"""OpenClaw 适配层 - 将 DocAssistant 的 skill 注册到 OpenClaw"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .async_skills import AsyncDocAssistant
from .skills import DocAssistant
from .skills.runtime import SkillRuntime


# 包级别元数据，OpenClaw 用来验证一致性
PACKAGE_METADATA = {
    "name": "cloud-doc-intelligent-assistant",
    "version": "0.3.0",
    "description": "智能文档助手技能库，支持抓取阿里云、腾讯云、百度云、火山引擎的产品文档，进行变更检测、跨云对比分析、AI 摘要生成和定时巡检推送。",
    "author": "anthonybinaruth-dotcom",
    "license": "MIT",
    "repository": "https://github.com/anthonybinaruth-dotcom/cloud-doc-skill",
    "runtime": {
        "language": "python",
        "version": ">=3.10",
        "install": "pip install -r requirements.txt",
        "dependencies": [
            "requests>=2.31.0",
            "beautifulsoup4>=4.12.0",
            "lxml>=4.9.0",
            "sqlalchemy>=2.0.0",
            "pyyaml>=6.0.0",
            "click>=8.1.0",
        ],
    },
    "environment": {
        "required": [],
        "optional": [
            {"name": "LLM_API_KEY", "description": "LLM API Key，AI 摘要和对比分析功能需要"},
            {"name": "DASHSCOPE_API_KEY", "description": "通义千问 API Key（LLM_API_KEY 的备选）"},
            {"name": "LLM_API_BASE", "description": "LLM API 地址，默认通义千问 DashScope"},
            {"name": "LLM_MODEL", "description": "LLM 模型名称，默认 qwen-turbo"},
            {"name": "AIFLOW_WEBHOOK_URL", "description": "飞书通知 webhook 地址"},
            {"name": "RULIU_WEBHOOK_URL", "description": "如流通知 webhook 地址"},
        ],
    },
    "permissions": {
        "network": {
            "outbound": [
                "https://help.aliyun.com/*",
                "https://cloud.tencent.com/*",
                "https://cloud.baidu.com/*",
                "https://www.volcengine.com/*",
            ],
            "outbound_configurable": [
                "${LLM_API_BASE}/*",
                "${AIFLOW_WEBHOOK_URL}",
                "${RULIU_WEBHOOK_URL}",
            ],
            "description": "访问云厂商文档 API；文档内容会发送到用户配置的 LLM API 进行摘要分析；变更通知会发送到用户配置的 webhook",
        },
        "filesystem": {
            "read": ["config.yaml", ".env"],
            "write": ["data/*.db", "logs/*.log", "notifications/*.md"],
            "description": "读取配置和 .env；写入 SQLite 数据库、日志和通知文件",
        },
    },
    "security_notice": (
        "本 skill 会将抓取的云厂商文档内容发送到用户配置的 LLM API 进行 AI 摘要和对比分析。"
        "如果启用通知功能，变更摘要会发送到用户配置的 webhook 地址。"
        "代码会自动加载项目根目录的 .env 文件（如果存在）。"
        "建议在隔离环境中运行，并审查 src/summarizer.py 和 src/notifier.py 的数据流向。"
    ),
}


# skill 描述信息，OpenClaw 用来展示和路由
SKILL_SPECS = [
    {
        "name": "fetch_doc",
        "description": "抓取指定云厂商的产品文档，支持按产品发现或按链接直接抓取，可选 AI 摘要",
        "method": "fetch_doc",
        "parameters": {
            "cloud": {"type": "string", "required": True, "enum": ["aliyun", "tencent", "baidu", "volcano"], "description": "云厂商标识"},
            "product": {"type": "string", "required": False, "description": "产品名称，按产品批量发现文档"},
            "doc_ref": {"type": "string", "required": False, "description": "文档标识，直接抓取单篇"},
            "with_summary": {"type": "boolean", "required": False, "default": False, "description": "是否生成 AI 摘要（需要 LLM_API_KEY）"},
            "max_pages": {"type": "integer", "required": False, "default": 20, "description": "最多抓取篇数"},
        },
        "environment": ["LLM_API_KEY"],
        "network": ["https://help.aliyun.com/*", "https://cloud.tencent.com/*", "https://cloud.baidu.com/*", "https://www.volcengine.com/*"],
    },
    {
        "name": "fetch_doc_async",
        "description": "【异步】抓取文档，立即返回 task_id，避免超时。适合大量文档抓取",
        "method": "fetch_doc_async",
        "parameters": {
            "cloud": {"type": "string", "required": True, "enum": ["aliyun", "tencent", "baidu", "volcano"], "description": "云厂商标识"},
            "product": {"type": "string", "required": False, "description": "产品名称"},
            "doc_ref": {"type": "string", "required": False, "description": "文档标识"},
            "with_summary": {"type": "boolean", "required": False, "default": False, "description": "是否生成 AI 摘要"},
            "max_pages": {"type": "integer", "required": False, "default": 20, "description": "最多抓取篇数"},
        },
        "environment": ["LLM_API_KEY"],
        "network": ["https://help.aliyun.com/*", "https://cloud.tencent.com/*", "https://cloud.baidu.com/*", "https://www.volcengine.com/*"],
    },
    {
        "name": "check_changes",
        "description": "检测指定云厂商产品文档的变更，与历史版本对比，生成变更摘要",
        "method": "check_changes",
        "parameters": {
            "cloud": {"type": "string", "required": True, "enum": ["aliyun", "tencent", "baidu", "volcano"], "description": "云厂商标识"},
            "product": {"type": "string", "required": True, "description": "产品名称"},
            "days": {"type": "integer", "required": False, "default": 7, "description": "检查最近 N 天的变更"},
            "with_summary": {"type": "boolean", "required": False, "default": True, "description": "是否生成变更摘要（需要 LLM_API_KEY）"},
            "max_pages": {"type": "integer", "required": False, "default": 20, "description": "最多检查篇数"},
        },
        "environment": ["LLM_API_KEY"],
        "network": ["https://help.aliyun.com/*", "https://cloud.tencent.com/*", "https://cloud.baidu.com/*", "https://www.volcengine.com/*"],
    },
    {
        "name": "compare_docs",
        "description": "对比两个云厂商的产品文档，AI 分析差异点和侧重点",
        "method": "compare_docs",
        "parameters": {
            "left": {"type": "object", "required": True, "description": "左侧文档，包含 cloud + product 或 doc_ref"},
            "right": {"type": "object", "required": True, "description": "右侧文档，包含 cloud + product 或 doc_ref"},
            "focus": {"type": "string", "required": False, "description": "对比关注点"},
        },
        "environment": ["LLM_API_KEY"],
        "network": ["https://help.aliyun.com/*", "https://cloud.tencent.com/*", "https://cloud.baidu.com/*", "https://www.volcengine.com/*"],
    },
    {
        "name": "compare_docs_async",
        "description": "【异步】对比文档，立即返回 task_id，避免超时",
        "method": "compare_docs_async",
        "parameters": {
            "left": {"type": "object", "required": True, "description": "左侧文档"},
            "right": {"type": "object", "required": True, "description": "右侧文档"},
            "focus": {"type": "string", "required": False, "description": "对比关注点"},
        },
        "environment": ["LLM_API_KEY"],
        "network": ["https://help.aliyun.com/*", "https://cloud.tencent.com/*", "https://cloud.baidu.com/*", "https://www.volcengine.com/*"],
    },
    {
        "name": "get_task_status",
        "description": "查询异步任务的状态和进度",
        "method": "get_task_status",
        "parameters": {
            "task_id": {"type": "string", "required": True, "description": "任务 ID"},
        },
        "environment": [],
        "network": [],
    },
    {
        "name": "get_task_result",
        "description": "获取异步任务的结果",
        "method": "get_task_result",
        "parameters": {
            "task_id": {"type": "string", "required": True, "description": "任务 ID"},
            "wait": {"type": "boolean", "required": False, "default": False, "description": "是否等待任务完成"},
            "timeout": {"type": "number", "required": False, "default": 300, "description": "等待超时时间（秒）"},
        },
        "environment": [],
        "network": [],
    },
    {
        "name": "summarize_diff",
        "description": "对新旧两个版本的文档内容进行 diff 和 AI 摘要",
        "method": "summarize_diff",
        "parameters": {
            "title": {"type": "string", "required": True, "description": "文档标题"},
            "old_content": {"type": "string", "required": True, "description": "旧版本内容"},
            "new_content": {"type": "string", "required": True, "description": "新版本内容"},
            "focus": {"type": "string", "required": False, "description": "关注重点"},
        },
        "environment": ["LLM_API_KEY"],
        "network": [],
    },
    {
        "name": "run_monitor",
        "description": "批量巡检多云多产品文档，生成日报摘要，可推送通知",
        "method": "run_monitor",
        "parameters": {
            "clouds": {"type": "array", "required": True, "description": "云厂商列表"},
            "products": {"type": "array", "required": True, "description": "产品列表"},
            "mode": {"type": "string", "required": False, "default": "check_now", "enum": ["check_now", "scheduled"], "description": "巡检模式"},
            "days": {"type": "integer", "required": False, "default": 1, "description": "检查最近 N 天"},
            "send_notification": {"type": "boolean", "required": False, "default": False, "description": "是否发送通知"},
        },
        "environment": ["LLM_API_KEY", "AIFLOW_WEBHOOK_URL", "RULIU_WEBHOOK_URL"],
        "network": ["https://help.aliyun.com/*", "https://cloud.tencent.com/*", "https://cloud.baidu.com/*", "https://www.volcengine.com/*"],
    },
]


@dataclass(frozen=True)
class OpenClawSkillSpec:
    name: str
    handler: Callable[..., Any]
    description: str
    is_async: bool = False
    parameters: Dict[str, Any] = field(default_factory=dict)
    environment: List[str] = field(default_factory=list)
    network: List[str] = field(default_factory=list)


class OpenClawAdapter:
    """将 DocAssistant 暴露为 OpenClaw 可注册的 skill"""

    def __init__(
        self,
        assistant: Optional[DocAssistant] = None,
        llm_api_key: str = "",
        llm_api_base: str = "",
        llm_model: str = "",
        use_async: bool = True,  # 默认使用异步版本
    ) -> None:
        if use_async:
            # 使用异步版本，支持长时间运行的任务
            self.assistant = AsyncDocAssistant(
                llm_api_key=llm_api_key,
                llm_api_base=llm_api_base,
                llm_model=llm_model,
            )
        else:
            # 使用同步版本（兼容旧代码）
            self.assistant = assistant or DocAssistant(
                llm_api_key=llm_api_key,
                llm_api_base=llm_api_base,
                llm_model=llm_model,
            )

    @staticmethod
    def package_metadata() -> dict:
        """返回包级别元数据，供 OpenClaw 验证一致性"""
        return PACKAGE_METADATA

    def list_skills(self) -> List[OpenClawSkillSpec]:
        return [
            OpenClawSkillSpec(
                name=spec["name"],
                handler=getattr(self.assistant, spec["method"]),
                description=spec["description"],
                parameters=spec.get("parameters", {}),
                environment=spec.get("environment", []),
                network=spec.get("network", []),
            )
            for spec in SKILL_SPECS
        ]

    def registry(self) -> dict[str, Callable[..., Any]]:
        """返回 {skill_name: handler} 字典"""
        return {spec.name: spec.handler for spec in self.list_skills()}

    def register(self, register_fn: Callable[..., Any]) -> List[OpenClawSkillSpec]:
        """通过回调函数注册所有 skill，包含完整元数据"""
        specs = self.list_skills()
        for spec in specs:
            try:
                register_fn(
                    name=spec.name,
                    handler=spec.handler,
                    description=spec.description,
                    is_async=spec.is_async,
                    parameters=spec.parameters,
                    environment=spec.environment,
                    network=spec.network,
                )
            except TypeError:
                # 兼容只接受 (name, handler) 的旧版注册接口
                try:
                    register_fn(
                        name=spec.name,
                        handler=spec.handler,
                        description=spec.description,
                        is_async=spec.is_async,
                    )
                except TypeError:
                    register_fn(spec.name, spec.handler)
        return specs


def build_openclaw_registry(
    llm_api_key: str = "",
    llm_api_base: str = "",
    llm_model: str = "",
) -> dict[str, Callable[..., Any]]:
    """快捷方式：构建 skill registry 字典"""
    return OpenClawAdapter(
        llm_api_key=llm_api_key,
        llm_api_base=llm_api_base,
        llm_model=llm_model,
    ).registry()


def register_openclaw_skills(
    register_fn: Callable[..., Any],
    llm_api_key: str = "",
    llm_api_base: str = "",
    llm_model: str = "",
) -> List[OpenClawSkillSpec]:
    """快捷方式：通过回调注册所有 skill"""
    return OpenClawAdapter(
        llm_api_key=llm_api_key,
        llm_api_base=llm_api_base,
        llm_model=llm_model,
    ).register(register_fn)


def get_package_metadata() -> dict:
    """快捷方式：获取包级别元数据"""
    return PACKAGE_METADATA
