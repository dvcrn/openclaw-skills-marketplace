"""Skills 包 - DocAssistant facade"""

from .runtime import SkillRuntime
from .fetch_doc_skill import FetchDocSkill
from .check_changes_skill import CheckChangesSkill
from .compare_docs_skill import CompareDocsSkill
from .summarize_diff_skill import SummarizeDiffSkill
from .run_monitor_skill import RunMonitorSkill


class DocAssistant:
    """统一入口，暴露 5 个 skill

    Args:
        config_path: 配置文件路径
        llm_api_key: LLM API Key，传入后覆盖 config.yaml 中的值
        llm_api_base: LLM API Base URL，传入后覆盖 config.yaml 中的值
        llm_model: LLM 模型名称，传入后覆盖 config.yaml 中的值
    """

    def __init__(
        self,
        config_path: str = "config.yaml",
        llm_api_key: str = "",
        llm_api_base: str = "",
        llm_model: str = "",
    ):
        self._runtime = SkillRuntime(
            config_path,
            llm_api_key=llm_api_key,
            llm_api_base=llm_api_base,
            llm_model=llm_model,
        )
        self._fetch_doc = FetchDocSkill(self._runtime)
        self._check_changes = CheckChangesSkill(self._runtime)
        self._compare_docs = CompareDocsSkill(self._runtime)
        self._summarize_diff = SummarizeDiffSkill(self._runtime)
        self._run_monitor = RunMonitorSkill(self._runtime)

    def fetch_doc(self, **kwargs):
        return self._fetch_doc.run(**kwargs)

    def check_changes(self, **kwargs):
        return self._check_changes.run(**kwargs)

    def compare_docs(self, **kwargs):
        return self._compare_docs.run(**kwargs)

    def summarize_diff(self, **kwargs):
        return self._summarize_diff.run(**kwargs)

    def run_monitor(self, **kwargs):
        return self._run_monitor.run(**kwargs)


__all__ = ["DocAssistant", "SkillRuntime"]
