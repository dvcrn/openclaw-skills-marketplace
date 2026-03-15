# scripts/parser/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import ast
import re

@dataclass
class ParsedComponent:
    name: str
    type: str  # form/table/chart/action
    props: Dict[str, Any]
    events: List[str]
    children: List['ParsedComponent']
    source_range: tuple  # (start_line, end_line)
    business_semantic: Optional[str] = None  # 推断的业务语义

@dataclass
class ParsedAPI:
    method: str
    endpoint: str
    params: Dict[str, Any]
    response_handler: Optional[str]
    business_purpose: Optional[str] = None

@dataclass
class ParsedRule:
    rule_type: str  # validation/permission/calculation/flow
    expression: str
    source: str  # 原始代码片段
    confidence: float  # 0-1
    business_meaning: Optional[str] = None

class BaseCodeParser(ABC):
    """代码解析器抽象基类"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = self._read_file()
        self.ast = None
        
    def _read_file(self) -> str:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """主解析入口"""
        pass
    
    @abstractmethod
    def extract_components(self) -> List[ParsedComponent]:
        """提取UI组件"""
        pass
    
    @abstractmethod
    def extract_apis(self) -> List[ParsedAPI]:
        """提取API调用"""
        pass
    
    @abstractmethod
    def extract_business_rules(self) -> List[ParsedRule]:
        """提取业务规则"""
        pass
    
    def calculate_complexity(self) -> Dict[str, int]:
        """计算代码复杂度指标"""
        return {
            "lines_of_code": len(self.content.splitlines()),
            "cyclomatic_complexity": self._calc_cyclomatic(),
            "component_count": len(self.extract_components()),
            "api_count": len(self.extract_apis())
        }
    
    def _calc_cyclomatic(self) -> int:
        """计算圈复杂度"""
        # 简化实现：统计if/for/while/switch/catch
        patterns = [r'\bif\b', r'\bfor\b', r'\bwhile\b', 
                   r'\bswitch\b', r'\bcatch\b', r'\?.*:']
        count = sum(len(re.findall(p, self.content)) for p in patterns)
        return count + 1