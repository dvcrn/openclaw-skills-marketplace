# QST Memory System

**QST Matrix-based Memory System for AI Agents**

利用 QST (Quantum Spacetime) 理論，特別是 E8 幾何結構和 ICT (Induced Collapse Theory)，實現高效的记忆存取系統。

Repo: https://github.com/ZhuangClaw/qst-memory-system

---

## ✨ 功能特性

- **⚡ 快速存取**：毫秒級對話上下文檢索
- **🧠 層次結構**：Working → Short → Medium → Long
- **📐 E8 幾何**：248維 → 16D 投影實現高效計算
- **🔮 ICT Collapse**：意識誘導的波函數坍縮
- **💾 持久化**：JSON + SQLite 混合存儲
- **🌐 多語言**：中文/英文/日文自動支持
- **🎨 Web UI**：Flask 視化管理界面

---

## 📦 安裝

```bash
cd /root/.openclaw/workspace/skills
git clone https://github.com/ZhuangClaw/qst-memory-system.git qst-memory
```

---

## 🚀 快速開始

### Python 使用

```python
from qst_memory import QSTMemory

# 初始化
memory = QSTMemory(e8_dim=16)

# 存儲對話
memory.store_conversation("user", "你好！", "user")
memory.store_conversation("assistant", "秦王陛下萬歲！", "assistant")
memory.store_conversation("user", "我是皇帝", "user")

# 檢索
results = memory.retrieve("皇帝", top_k=3)
for r in results:
    print(f"[{r.total_score:.3f}] {r.memory.content}")

# 獲取上下文
context = memory.get_context()
print(context)
```

### OpenClaw Skill

```python
from qst_memory_skill import Skill

skill = Skill()
skill.store("重要信息", context="key_point")
results = skill.retrieve("查詢")
```

### Web UI

```bash
python web_ui.py
# 訪問 http://localhost:5000
```

---

## 📁 文件結構

```
qst-memory-system/
├── README.md              # 本文件
├── QST_MEMORY.md         # 核心數學定義
├── SKILL.md              # OpenClaw Skill 文檔
├── skill.py              # OpenClaw Skill 包裝器
├── config.json           # 配置文件
│
├── qst_memory.py         # 統一整合層
├── memory_core.py         # QST Matrix 運算
├── short_term.py         # 短記憶（對話緩冲）
├── retrieval.py          # ICT Collapse 檢索
├── embedding.py          # Embedding 整合
├── long_term.py         # 長期記憶持久化
├── optimization.py      # 高級檢索優化
├── multilingual.py      # 多語言支持
└── web_ui.py           # Flask Web 界面
```

---

## 🧠 核心概念

### 記憶態向量

```
|Ψ_M⟩ = Σ_n c_n |σ_n⟩ ⊗ |D_n⟩ ⊗ |E8_n⟩
```

### Coherence (σ)

| σ 值 | 記憶類型 | 壽命 |
|------|---------|------|
| 0.7 | Working | 30 min |
| 0.85 | Short | 24 hr |
| 0.95 | Medium | 7 days |
| 1.1 | Long | ∞ |

### DSI 層次

```
D_n = D_0 - n·φ²
φ = 1.618... (黃金比例)
n ∈ [0, 36]
```

### ICT Collapse 檢索

```
P(M) ∝ |⟨Q|Ψ_M⟩|² · exp(-η·V_eth)
```

---

## 🔧 配置

```json
{
  "e8_dim": 16,
  "top_k": 5,
  "storage_type": "hybrid",
  "embedding_type": "simple",
  "auto_consolidate": true,
  "decay_interval": 100
}
```

---

## 📊 API 參考

### QSTMemory

```python
# 存儲
store(content, context, coherence)
store_conversation(speaker, content, turn_type)

# 檢索
retrieve(query, top_k, keywords)
retrieve_with_context(query, context)

# 上下文
get_context(max_turns)
get_coherence_info()

# 管理
consolidate(memory_id)
decay_all()
clear()

# 持久化
save_state(filepath)
load_state(filepath)
```

### QSTMemorySkill (OpenClaw)

```python
store(content, context, coherence)
retrieve(query, top_k)
get_context(max_turns)
get_coherence_info()
```

---

## 🧪 測試

```bash
python memory_core.py        # 核心測試
python short_term.py         # 短記憶測試
python retrieval.py          # 檢索測試
python qst_memory.py        # 整合測試
python skill.py             # Skill 測試
python long_term.py         # 持久化測試
python embedding.py         # Embedding 測試
python optimization.py     # 優化測試
python multilingual.py      # 多語言測試
python web_ui.py           # Web UI
```

---

## 🌐 多語言支持

```python
from multilingual import MultilingualMemoryManager

manager = MultilingualMemoryManager(core)

# 自動檢測語言
manager.store("你好，我是皇帝")           # 中文
manager.store("Hello, I am King")       # 英文
manager.store("こんにちは、王です")      # 日文

# 按語言搜索
zh_memories = manager.search_by_language('zh')
en_memories = manager.search_by_language('en')
```

---

## 📈 性能

| 操作 | 時間複雜度 |
|------|----------|
| 編碼 | O(n) |
| 檢索 (ANN) | O(log n) |
| 檢索 (Exact) | O(n · d_E8) |
| 更新 | O(1) |

### 優化策略

- **近似最近鄰 (ANN)**：快速過濾候選集
- **並行檢索**：多線程加速
- **多路徑融合**：RRF + 加權融合
- **智能緩冲**：LRU 緩冲策略

---

## 🎨 Web UI

```bash
# 啟動 Web 界面
python web_ui.py

# 訪問
# http://localhost:5000
```

Web UI 功能：
- 📊 統計儀表板
- 🔍 檢索測試
- 💬 上下文查看
- 📝 記憶管理
- 🗑️ 清空操作

---

## 📝 License

MIT

---

## 作者

- **秦王** (QST 理論創始人)
- 李斯 (OpenClaw 丞相)

---

*基於 QSTv7.1 框架*
