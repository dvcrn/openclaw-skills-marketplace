"""Pattern Miner - Automatic pattern detection and template generation."""

__version__ = "0.1.0"
__author__ = "Pearl Workspace"

from .analyzer import CodeAnalyzer
from .history import HistoryAnalyzer
from .template import TemplateGenerator

__all__ = ["CodeAnalyzer", "HistoryAnalyzer", "TemplateGenerator"]
