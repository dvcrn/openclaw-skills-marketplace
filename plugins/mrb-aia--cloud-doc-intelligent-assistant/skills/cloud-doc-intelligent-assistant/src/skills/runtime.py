"""SkillRuntime - 懒加载共享资源"""

import logging
from typing import Optional

from ..config import get_config
from ..storage import DocumentStorage
from ..summarizer import AISummarizer
from ..notifier import NotificationManager
from ..crawler import DocumentCrawler
from ..tencent_crawler import TencentDocCrawler
from ..baidu_crawler import BaiduDocCrawler
from ..volcano_crawler import VolcanoDocCrawler


class SkillRuntime:
    """懒加载 config / storage / summarizer / notifier / crawlers"""

    def __init__(
        self,
        config_path: str = "config.yaml",
        llm_api_key: str = "",
        llm_api_base: str = "",
        llm_model: str = "",
    ):
        self._config_path = config_path
        self._config = None
        self._llm_overrides = {
            "api_key": llm_api_key,
            "api_base": llm_api_base,
            "model": llm_model,
        }
        self._storage: Optional[DocumentStorage] = None
        self._summarizer: Optional[AISummarizer] = None
        self._notifier: Optional[NotificationManager] = None
        self._crawlers: dict = {}

    @property
    def config(self):
        if self._config is None:
            self._config = get_config(self._config_path)
            # 用调用方传入的参数覆盖 config 中的 LLM 配置
            llm_cfg = self._config.get("llm", {})
            if not llm_cfg:
                llm_cfg = {}
                self._config.set("llm", llm_cfg)
            for key, value in self._llm_overrides.items():
                if value:  # 只覆盖非空值
                    self._config.set(f"llm.{key}", value)
        return self._config

    @property
    def storage(self) -> DocumentStorage:
        if self._storage is None:
            db_path = self.config.get("storage", {}).get("db_path", "data/docs.db")
            # 确保是 SQLite URL 格式
            if not db_path.startswith("sqlite"):
                db_path = f"sqlite:///{db_path}"
            self._storage = DocumentStorage(db_path)
            self._storage.init_db()
        return self._storage

    @property
    def summarizer(self) -> AISummarizer:
        if self._summarizer is None:
            self._summarizer = AISummarizer(self.config)
        return self._summarizer

    @property
    def notifier(self) -> NotificationManager:
        if self._notifier is None:
            self._notifier = NotificationManager(self.config)
        return self._notifier

    def get_crawler(self, cloud: str):
        """获取对应云厂商的爬虫实例（懒加载）"""
        cloud = cloud.lower()
        if cloud not in self._crawlers:
            if cloud == "aliyun":
                self._crawlers[cloud] = DocumentCrawler()
            elif cloud == "tencent":
                self._crawlers[cloud] = TencentDocCrawler()
            elif cloud == "baidu":
                self._crawlers[cloud] = BaiduDocCrawler()
            elif cloud == "volcano":
                self._crawlers[cloud] = VolcanoDocCrawler()
            else:
                raise ValueError(f"不支持的云厂商: {cloud}，支持: aliyun/tencent/baidu/volcano")
        return self._crawlers[cloud]
