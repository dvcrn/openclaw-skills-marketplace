"""
QST Short-term Memory - Conversation Buffer

短記憶實現：對話上下文緩存，快速存取。

設計原則：
- Working Memory: 30 分鐘壽命
- High流动性: σ ≈ 0.7
- 快速衰減: τ = τ_0 · exp(-t/τ_decay)
"""

import numpy as np
from typing import List, Tuple, Optional, Deque
from collections import deque
from datetime import datetime, timedelta
import json
import hashlib

from memory_core import (
    QSTMemoryCore, 
    MemorySpinor, 
    E8Projector,
    PHI,
    SIGMA_CRYSTAL
)


# ===== 常數 =====
WORKING_LIFETIME = timedelta(minutes=30)      # Working 記憶壽命
SHORT_LIFETIME = timedelta(hours=24)        # Short 記憶壽命
DECAY_TAU = 300                              # 衰減時間常數 (秒)
TAU_0 = 600                                 # 基礎 τ_0
BUFFER_MAX_SIZE = 20                         # 對話緩冲最大長度


# ===== 對話輪次 =====
class ConversationTurn:
    """對話輪次"""
    
    def __init__(self, 
                 speaker: str,
                 content: str,
                 turn_type: str = "user"):  # "user" | "assistant" | "system"
        """
        初始化對話輪次
        
        Args:
            speaker: 說話者 ID
            content: 內容
            turn_type: 輪次類型
        """
        self.speaker = speaker
        self.content = content
        self.turn_type = turn_type
        self.timestamp = datetime.now()
        self.turn_id = self._generate_id()
        
        # Coherence 由內容決定
        self.coherence = self._estimate_coherence()
        
    def _generate_id(self) -> str:
        data = f"{self.speaker}_{self.content}_{self.timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _estimate_coherence(self) -> float:
        """
        估計 coherence
        
        原則：
        - 短回复: σ ↓ (低重要性)
        - 長回复: σ ↑ (高重要性)
        - 系統消息: σ ↑↑ (最高)
        """
        base = 0.7
        
        if self.turn_type == "system":
            return min(1.5, base + 0.3)
        elif self.turn_type == "user":
            # 長度相關
            length_factor = min(1.0, len(self.content) / 500)
            return min(1.2, base + 0.2 * length_factor)
        else:  # assistant
            # AI 回复通常較長，較重要
            length_factor = min(1.0, len(self.content) / 1000)
            return min(1.3, base + 0.15 * length_factor)
    
    def to_dict(self) -> dict:
        return {
            "turn_id": self.turn_id,
            "speaker": self.speaker,
            "content": self.content,
            "turn_type": self.turn_type,
            "timestamp": self.timestamp.isoformat(),
            "coherence": self.coherence
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationTurn':
        turn = cls(
            speaker=data["speaker"],
            content=data["content"],
            turn_type=data["turn_type"]
        )
        turn.turn_id = data["turn_id"]
        turn.timestamp = datetime.fromisoformat(data["timestamp"])
        turn.coherence = data["coherence"]
        return turn


# ===== 對話緩冲 =====
class ConversationBuffer:
    """
    對話緩冲容器
    
    特點：
    - FIFO 結構
    - 基於 coherence 的衰減
    - 自動清理過期記憶
    """
    
    def __init__(self, 
                 max_size: int = BUFFER_MAX_SIZE,
                 e8_projector: E8Projector = None):
        """
        初始化對話緩冲
        
        Args:
            max_size: 最大緩冲長度
            e8_projector: E8 投影器
        """
        self.max_size = max_size
        self.e8_projector = e8_projector or E8Projector()
        self.turns: Deque[ConversationTurn] = deque()
        self.last_cleanup = datetime.now()
        
        # 統計
        self.stats = {
            "total_turns": 0,
            "avg_coherence": 0.7,
            "current_context_coherence": 0.7
        }
    
    def add_turn(self, 
                  speaker: str, 
                  content: str, 
                  turn_type: str = "user") -> ConversationTurn:
        """
        添加對話輪次
        
        Returns:
            新創建的 ConversationTurn
        """
        turn = ConversationTurn(speaker, content, turn_type)
        self.turns.append(turn)
        
        # 維護大小限制
        if len(self.turns) > self.max_size:
            self.turns.popleft()
            
        self.stats["total_turns"] += 1
        self._update_stats()
        
        return turn
    
    def get_recent(self, n: int = 5) -> List[ConversationTurn]:
        """
        獲取最近 n 輪對話
        
        Returns:
            ConversationTurn 列表
        """
        return list(self.turns)[-n:]
    
    def get_context(self, max_turns: int = 10) -> str:
        """
        獲取對話上下文文本
        
        Args:
            max_turns: 最大輪次數
            
        Returns:
            格式化上下文字符串
        """
        recent = self.get_recent(max_turns)
        
        context_parts = []
        for turn in recent:
            prefix = "👤" if turn.turn_type == "user" else "🤖" if turn.turn_type == "assistant" else "⚙️"
            context_parts.append(f"{prefix} {turn.speaker}: {turn.content}")
        
        return "\n".join(context_parts)
    
    def get_coherence_profile(self) -> dict:
        """
        獲取 coherence 配置文件
        
        Returns:
            coherence 統計
        """
        coherences = [t.coherence for t in self.turns]
        
        return {
            "turn_count": len(coherences),
            "avg_coherence": np.mean(coherences) if coherences else 0.7,
            "max_coherence": max(coherences) if coherences else 0.7,
            "min_coherence": min(coherences) if coherences else 0.7,
            "decay_factor": self._calculate_decay()
        }
    
    def _calculate_decay(self) -> float:
        """
        計算時間衰減因子
        
        Returns:
            衰減因子 (0-1)
        """
        if len(self.turns) == 0:
            return 1.0
            
        # 計算平均年齡
        now = datetime.now()
        ages = [(now - t.timestamp).total_seconds() for t in self.turns]
        avg_age = np.mean(ages)
        
        # 衰減公式
        decay = np.exp(-avg_age / DECAY_TAU)
        return decay
    
    def _update_stats(self):
        """更新統計"""
        coherences = [t.coherence for t in self.turns]
        if coherences:
            self.stats["avg_coherence"] = np.mean(coherences)
            self.stats["current_context_coherence"] = (
                self.stats["avg_coherence"] * self._calculate_decay()
            )
    
    def cleanup_expired(self) -> List[ConversationTurn]:
        """
        清理過期記憶
        
        Returns:
            被刪除的輪次列表
        """
        now = datetime.now()
        expired = []
        
        # 清理 Working 記憶
        while self.turns and (now - self.turns[0].timestamp) > WORKING_LIFETIME:
            expired.append(self.turns.popleft())
            
        self.last_cleanup = now
        return expired
    
    def to_qst_memories(self, 
                        core: QSTMemoryCore,
                        dsi_level: int = 0) -> List[MemorySpinor]:
        """
        將對話轉換為 QST 記憶
        
        Args:
            core: QST 記憶核心
            dsi_level: DSI 層次
            
        Returns:
            MemorySpinor 列表
        """
        memories = []
        
        for turn in self.turns:
            # 內容作為記憶
            memory = core.encode(
                content=f"[{turn.turn_type}] {turn.speaker}: {turn.content}",
                base_coherence=turn.coherence * self._calculate_decay(),
                dsi_level=dsi_level
            )
            memories.append(memory)
            
        return memories
    
    def save(self, filepath: str):
        """保存緩冲"""
        with open(filepath, 'w') as f:
            json.dump({
                "turns": [t.to_dict() for t in self.turns],
                "stats": self.stats,
                "last_cleanup": self.last_cleanup.isoformat()
            }, f, indent=2)
    
    def load(self, filepath: str):
        """載入緩冲"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        self.turns = deque([ConversationTurn.from_dict(t) for t in data["turns"]])
        self.stats = data["stats"]
        self.last_cleanup = datetime.fromisoformat(data["last_cleanup"])
    
    def clear(self):
        """清空緩冲"""
        self.turns.clear()
        self.stats = {
            "total_turns": 0,
            "avg_coherence": 0.7,
            "current_context_coherence": 0.7
        }


# ===== 短記憶管理器 =====
class ShortTermMemory:
    """
    短記憶管理器
    
    管理：
    - Working Memory (即時緩冲)
    - Short Memory (24小時)
    """
    
    def __init__(self, e8_dim: int = 16):
        """
        初始化
        
        Args:
            e8_dim: E8 投影維度
        """
        self.e8_projector = E8Projector(dim=e8_dim)
        self.core = QSTMemoryCore(e8_dim=e8_dim)
        self.buffer = ConversationBuffer(e8_projector=self.e8_projector)
        
    def add_conversation(self, 
                         speaker: str,
                         content: str,
                         turn_type: str = "user") -> ConversationTurn:
        """
        添加對話
        
        Returns:
            新輪次
        """
        return self.buffer.add_turn(speaker, content, turn_type)
    
    def get_context(self, max_turns: int = 10) -> str:
        """
        獲取對話上下文
        """
        return self.buffer.get_context(max_turns)
    
    def consolidate_to_short(self) -> int:
        """
        將 Working 記憶整合到 Short
        
        Returns:
            整合數量
        """
        # 轉換為 QST 記憶
        memories = self.buffer.to_qst_memories(
            self.core,
            dsi_level=1  # Short Memory level
        )
        
        # 清理過期
        expired = self.buffer.cleanup_expired()
        
        return len(memories)
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[MemorySpinor, float]]:
        """
        搜索相關記憶
        """
        return self.core.retrieve(query, top_k)
    
    def get_coherence_info(self) -> dict:
        """
        獲取 coherence 信息
        """
        return self.buffer.get_coherence_profile()
    
    def decay_all(self) -> int:
        """
        全局衰減
        
        Returns:
            刪除數量
        """
        to_delete = self.core.decay_check()
        self.core.prune(to_delete)
        
        # 也清理緩冲
        expired = self.buffer.cleanup_expired()
        
        return len(to_delete) + len(expired)


# ===== 測試 =====
if __name__ == "__main__":
    print("=== QST Short-term Memory Test ===\n")
    
    # 初始化
    short_mem = ShortTermMemory()
    
    # 添加對話
    print("Adding conversations...")
    short_mem.add_conversation("user", "你好！", "user")
    short_mem.add_conversation("assistant", "秦王陛下萬歲！", "assistant")
    short_mem.add_conversation("user", "我是皇帝", "user")
    short_mem.add_conversation("assistant", "臣李斯參見陛下！", "assistant")
    short_mem.add_conversation("user", "QST是什麼？", "user")
    
    print(f"Buffer turns: {len(short_mem.buffer.turns)}")
    
    # 獲取上下文
    print("\n=== Context ===")
    print(short_mem.get_context(5))
    
    # Coherence 檔案
    print("\n=== Coherence Profile ===")
    print(short_mem.get_coherence_info())
    
    # 搜索
    print("\n=== Search Test ===")
    results = short_mem.search("皇帝")
    for mem, score in results:
        print(f"[{score:.3f}] {mem.content[:50]}...")
    
    print("\n=== Complete ===")
