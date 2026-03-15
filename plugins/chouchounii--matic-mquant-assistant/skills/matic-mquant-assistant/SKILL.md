---
name: matic-mquant-assistant
description: "MQuant Python strategy development assistant. Generates runnable Python strategy code for MQuant platform."
---

# MQuant Strategy Development Assistant

## Overview

This skill generates **runnable** Python strategy code for the MQuant quantitative trading platform.

**核心理念**：
- 代码**可直接运行**优先，策略逻辑可由用户后续调整
- 生成代码经过模板验证，确保语法正确、API调用无误
- 用户可在实盘前通过Matic模拟盘验证策略效果

**⚠️ 注意**：Matic平台**不支持回测**，策略验证需通过模拟盘或极小仓位实盘测试。

## Reference Structure

```
reference/
├── mquantFAQ.md                    # 常见问题
├── mquant_inside_python_document/  # Python API文档
│   ├── python template.py          # Python策略模板
│   ├── mquant_api.py               # API接口定义
│   ├── mquant_struct.py            # 数据结构定义
│   ├── HTSACsvReader.py
│   └── HTSADbAccess.py
└── mquant_inside_python_strategy/  # Python策略示例
    ├── DualThrust/                 # DualThrust策略
    ├── 日频报单场景/               # 日频报单示例
    ├── 算法交易/                   # 算法交易示例
    ├── ETF轮动.py
    ├── Insight_Demo.py
    ├── R-Breaker.py
    ├── 两融接口调用示例.py
    ├── 交易数据下载.py
    ├── 增强网格策略.py
    ├── 定时撤单.py
    ├── 快捷参数多产品.py
    ├── 快捷参数示例.py
    ├── 横盘突破.py
    ├── 用户参数示例.py
    ├── 算法接口调用示例.py
    └── 调仓策略.py
```

## Workflow

### Step 0: User Environment Initialization (First Run)

**首次使用时，自动创建用户个人文档：**

检查以下文件是否存在，不存在则自动创建：

`
✓ COMMON_ERRORS.user.md      (个人错误笔记)
✓ TRADING_RULES.user.md      (个人交易规则)  
✓ TRADING_PHILOSOPHY.user.md (个人交易理念)
`

**每个文件包含模板：**
- My Coding Habits (编码习惯)
- My Common Mistakes (常见错误)
- My Debugging Tips (调试技巧)
- Personal Notes (个人笔记)

**说明：**
- .user.md 文件永远不会被Skill 更新覆盖
- 用户可随时编辑，记录个人习惯和心得
- Skill 文档更新时，.md 和 .user.md 各自独立维护

---

### Step 1: Directory Detection (Auto Scan)

Automatically locate the M-quant strategy directory:

```
全盘扫描 maticupdate.exe
    |
找到Matic安装目录，例如 D:\Matic\maticupdate.exe 或者其他形式
    |
在同级目录找 M-quant\ 文件夹
    |
在 M-quant\ 下找类似用户名的文件夹，比如：
    ├── userA\
    ├── userB\
    └── trader001\
    |
询问用户将策略代码保存到哪个目录
```

**Scan Rules:**
- 全盘搜索 `maticupdate.exe`
- 在其所在目录下找 `M-quant\` 子目录
- 在 `M-quant\` 下识别用户名文件夹（排除系统文件夹如 .git, backup, log, template）

**Failure Handling:**
- 未找到 `maticupdate.exe` 或 `M-quant` -> 提示用户手动输入路径
- 用户不提供路径 -> 直接输出代码到对话，不保存文件

### Step 2: Language Selection

询问用户选择编程语言：

```
请选择要生成的策略代码类型：
1. Python (推荐，快速开发、易于调试)
2. C++ (高性能，需要自行编译为DLL)
```

**⚠️ 重要提醒**：AI生成的代码请务必在Matic测试环境中充分调试验证后再用于实盘交易。

### Step 3: Version Control

Auto-generate versioned filenames:

命名格式: `xxxxx_vN.py` （MQuant限制：py文件名不能超过11个字符）

```
首次生成:  duoma_v1.py      + duoma_v1.log      (version: 1)
再次生成:  duoma_v2.py      + duoma_v2.log      (version: 2)
第三次:   duoma_v3.py      + duoma_v3.log      (version: 3)
```

**命名规则**：
- 文件名（不含扩展名）≤ 11个字符
- 建议格式：`策略缩写_v版本号`
- 只能使用：字母、数字、下划线

实际示例：
- `duoma_v1.py` (双均线策略)
- `wangge_v1.py` (网格交易)
- `tiaojian_v2.py` (条件单策略)

**Retention Rules:**
- 最多保留 5 个版本
- 超出时自动删除最旧版本

**Version Diff（版本对比）**

当生成新版本时，自动对比上一版本的变更：

```
===== VERSION DIFF: v1 → v2 =====
变更摘要举例：
+ 增加了止损逻辑（固定金额止损）
+ 修改了入场条件（由金叉改为量价齐升）
- 删除了冗余的日志输出
~ 调整了网格间距（由1%改为2%）

详细对比：
[可选：展示关键代码差异]
```

用户可通过对比快速了解迭代改进了什么。

### Step 4: Strategy Parameter Wizard

在生成代码前，主动引导用户配置策略参数：

**询问方式**：
```
您选择了[策略名称]，请配置以下参数：
1. 交易标的：[股票代码/期货合约] 
2. [参数1]：[默认值]，建议范围[min-max]
3. [参数2]：[默认值]，建议范围[min-max]
...
```


**说明**：提供默认值和合理范围，用户可直接使用或自行调整。

### Step 5: Code Generation

**生成原则：可运行 > 完美**

1. 基于模板生成策略代码，确保：
   - 语法正确，可直接运行
   - API调用符合Matic规范
   - **必须包含日志写入功能**
   - 包含基本的异常处理
   
**重要API限制（必须遵守）**：
- `subscribe()` 只支持 Tick 和 分钟K线，**不支持日线订阅**
- 策略需使用 `MarketDataType.KLINE_1M` 订阅1分钟K线，在代码中累积数据
- 错误示例：`subscribe(symbol, '1d')` ❌ 
- 正确示例：`subscribe(symbol, MarketDataType.KLINE_1M)` ✅

2. 保存 `.py` 文件到选定目录
3. 同步保存 `.log` 文件（包含生成元数据）

**代码验证清单**：
- [ ] 所有导入的模块正确
- [ ] API函数参数正确
- [ ] 变量初始化完整
- [ ] 日志功能正常工作
- [ ] 无语法错误

**严格遵守文档定义（避免运行时错误）**：

生成代码时，必须严格按照 `mquant_api.py` 和 `mquant_struct.py` 中的定义，不得凭记忆或推测。

**API调用必须核对：**
| API | 文档定义 | 常见错误 |
|-----|----------|----------|
| subscribe | `subscribe(security, MarketDataType.XXX)` | 使用字符串'1d' ❌ |
| handle_tick | `handle_tick(context, tick, msg_type)` | 参数顺序错误 ❌ |
| handle_data | `handle_data(context, kline_data)` | 参数名错误 ❌ |
| order | `order(symbol, amount)` | 参数类型错误 ❌ |
| get_positions | `get_positions()` | 无参数 ✅ |

**结构体字段必须核对：**
| 结构体 | 正确字段 | 常见错误 |
|--------|----------|----------|
| Tick | `tick.code`, `tick.current` | `tick.last` ❌ |
| Tick | `tick.open`, `tick.high`, `tick.low` | - |
| Position | `pos.symbol`, `pos.amount` | `pos.code` ❌ |
| KLineDataPush | `kline.close`, `kline.high` | - |

**重要：get_positions() 返回类型**

`get_positions()` 返回 **字典** `dict<symbol, Position>`，不是列表！

**错误用法：**
```python
positions = get_positions()
for pos in positions:  # ❌ 这样遍历得到的是symbol字符串
    if pos.symbol == g_security:  # ❌ 'str' object has no attribute 'symbol'
```

**正确用法：**
```python
# 方法1: 使用get()从字典获取
positions = get_positions()
pos = positions.get(g_security)
amount = pos.amount if pos else 0

# 方法2: 遍历字典的值
positions = get_positions()
for symbol, pos in positions.items():
    if symbol == g_security:
        amount = pos.amount
```

**替代方案：**
如需列表，使用 `get_positions_ex()` 返回 `list<Position>`

**生成前必读：**
1. 查阅 `reference/mquant_inside_python_document/mquant_api.py` 确认API签名
2. 查阅 `reference/mquant_inside_python_document/mquant_struct.py` 确认字段名
3. 不确定的API或字段，禁止在代码中使用

**Generated code must include:**

```python
from mquant_api import *
from mquant_struct import *
import os
from datetime import datetime


LOG_FILE = None

def write_log(level, msg):
    """Write log to .log file, synced with Matic log window"""
    global LOG_FILE
    if LOG_FILE is None:
        current_file = os.path.abspath(__file__)
        base_name = os.path.splitext(current_file)[0]
        LOG_FILE = base_name + '.log'
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] [{level}] {msg}\n"
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
    except:
        pass  # Write failure should not affect strategy execution
```

**详细日志记录要求（便于问题排查）：**

所有策略必须记录以下信息到日志：

**1. 初始化阶段：**
- 策略启动时间
- 订阅的标的和行情类型
- 策略参数值（网格价格、数量等）
- 初始状态（持仓、资金等）

**2. 行情数据阶段：**
- 每次接收到的行情数据（tick价格/kline收盘价）
- 计算的中间值（均线、网格索引等）
- 当前持仓状态

**3. 判断逻辑阶段：**
- 每个判断条件的结果（True/False）
- 触发交易的具体条件
- 未触发交易的原因

**4. 交易执行阶段：**
- 下单参数（标的、数量、价格）
- 下单返回值（成功/失败）
- 错误信息（如有）

**示例日志格式：**
```python
def handle_tick(context, tick, msg_type):
    # 1. 记录原始数据
    write_log('DEBUG', f'Tick received: code={tick.code}, price={tick.current}')
    
    # 2. 计算逻辑
    current_price = tick.current
    grid_idx = calculate_grid(current_price)
    write_log('DEBUG', f'Calculated: price={current_price}, grid_idx={grid_idx}, last_idx={g_last_idx}')
    
    # 3. 判断逻辑
    if grid_idx < g_last_idx:
        write_log('INFO', f'Trigger BUY: idx {g_last_idx}->{grid_idx}, price={current_price}')
        # 4. 执行结果
        result = order(g_security, g_amount)
        write_log('INFO', f'Order result: {result}')
    else:
        write_log('DEBUG', f'No trade: idx={grid_idx}, last_idx={g_last_idx}, condition=False')
```

**日志级别规范：**
- `DEBUG` - 详细数据（tick价格、计算过程、判断条件）
- `INFO` - 关键事件（初始化、交易触发、参数变化）
- `WARN` - 警告（数据异常、条件不满足但仍继续）
- `ERROR` - 错误（API调用失败、异常抛出）

**排查问题时的日志检查点：**
1. 行情数据是否接收？→ 检查DEBUG日志的tick/kline数据
2. 计算是否正确？→ 检查计算的索引、均线值等
3. 判断条件是否满足？→ 检查条件判断的True/False
4. 交易是否执行？→ 检查order()调用和返回值


## API Quick Reference

### Market Data
- `subscribe(symbol, frequency)` - 订阅行情推送
  - `MarketDataType.TICK` - Tick行情 (handle_tick)
  - `MarketDataType.KLINE_1M` - 1分钟K线 (handle_data) ✅ 最常用
  - `MarketDataType.RECORD_ORDER` - 逐笔委托
  - `MarketDataType.RECORD_TRANSACTION` - 逐笔成交
  - **注意：不支持日线订阅，需用1分钟K线累积**
- `get_kline_data()` - 查询历史K线数据

### Trading
- order(symbol, amount, style)
- cancel_order(order_id)
- get_open_orders()

### Query
- get_positions()
- get_fund_info()

### Step 6: Code Explanation Mode (Optional)

用户可要求"解释这段代码"，提供以下输出：

**1. 策略逻辑概述**
- 策略类型：[趋势跟踪/均值回归/事件驱动等]
- 核心思想：用1-2句话概括
- 适用场景：什么市场条件下表现较好

**2. 关键代码行注释**
```python
# 初始化：设置日志和变量
initialize(context):
    
# 订阅行情：监听指定股票的分钟线
subscribe('000001.SZ', '1m')
    
# 交易逻辑：当短期均线上穿长期均线时买入
if short_ma > long_ma:
    order(...)
```

**3. 风险提示**
- 该策略的主要风险点
- 建议的风控措施

## Language Support

### Python Strategy
- Full auto-generation: code + log files
- Auto-save to M-quant user directory
- Version control (max 5 versions)


## Unified Log Format

每次生成策略时，创建一个 `.log` 文件，策略运行时将日志追加到同一文件：
```
strategy_name.py
strategy_name.log  <- Generation metadata + Runtime logs (unified)
```

**.log File Structure:**

```
===== GENERATION META =====
{
  "version": 1,
  "previous": null,
  "generated_at": "2026-03-05 18:00:00",
  "model": "moonshot/kimi-k2.5",
  "template": "Dual MA",
  "params": {"fast_ma": 5, "slow_ma": 20},
  "target_path": "D:\\Matic\\M-quant\\userA\\",
  "matic_exe_path": "D:\\Matic\\maticupdate.exe",
  "changelog": "Initial version"
}

===== RUNTIME LOG =====
[2026-03-05 22:20:01] [INFO] Strategy started
[2026-03-05 22:20:01] [INFO] Target price: 18.50, Order amount: 100
[2026-03-05 22:20:05] [INFO] Condition triggered! Current 18.45 <= Target 18.50
[2026-03-05 22:20:05] [INFO] Buy order sent: 601688.SH, Order ID 12345
```

**Runtime Debugging:**
- After strategy runs in Matic, user can paste error logs
- I read the `.log` file to see generation parameters and runtime logs
- Quickly identify if issue is in generation or runtime environment


### Step 1: 错误识别
分析错误日志，分类问题类型：
- **Syntax Error**：语法错误（括号不匹配、缩进错误等）
- **Import Error**：模块导入失败
- **API Error**：Matic API调用错误（参数错误、未订阅行情等）
- **Logic Error**：逻辑错误（变量未定义、除零等）
- **Runtime Error**：运行时错误（内存、超时等）

### Step 2: 定位问题
根据错误堆栈定位到具体代码行，结合`.log`文件中的生成元数据：
- 查看代码版本
- 查看使用的模板类型
- 查看用户自定义参数

### Step 3: 一键修复
提供修复方案：

``
