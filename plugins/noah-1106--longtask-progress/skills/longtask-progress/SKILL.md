---
name: longtask_progress
description: "长任务强制进度报告系统。防止长时间执行任务时\"失去专注\"或\"睡着\"，\n 通过定时强制报告保持任务连续性。适用于文章写作、图片生成、数据分析、\n 文件下载等任何可能耗时较长的任务。"
---

# LongTask Progress - 长任务强制进度报告

防止长时间执行任务时失去专注，通过定时强制报告机制保持任务连续性。

## 问题场景

执行长任务时（如文章写作、批量配图、数据下载），容易出现：
- 任务执行中失去专注，进入"睡眠"状态
- 用户不知道当前进度，只能干等
- 任务中断后无法恢复上下文
- 长时间无反馈导致用户体验差

## 解决方案

**强制进度报告机制**：
- 定时自动报告（默认每5分钟）
- 步骤完成即时报告
- 精确显示进度百分比
- 后台线程运行，不阻塞主任务

## 安装

无需安装，直接导入使用：

```python
import sys
sys.path.insert(0, '~/.openclaw/workspace-bibi/skills/longtask_progress')
from longtask_progress import LongTaskProgress, track_progress
```

## 使用方式

### 方式1：上下文管理器（推荐）

最简洁的使用方式，自动处理启动和停止：

```python
from longtask_progress import LongTaskProgress

# 使用with语句，自动管理生命周期
with LongTaskProgress(
    task_name="文章写作",
    total_steps=6,
    interval=300  # 每5分钟报告一次
) as reporter:
    
    for section in ["引言", "背景", "分析", "结论"]:
        write_section(section)
        reporter.step(f"完成{section}")

# 离开with块时自动停止
```

### 方式2：装饰器

为函数自动添加进度追踪：

```python
from longtask_progress import track_progress

@track_progress(
    task_name="图片生成",
    total_steps=5,
    interval=120  # 每2分钟报告
)
def generate_images(reporter):
    for i in range(5):
        generate_image(i)
        reporter.step(f"生成第{i+1}张图片")

# 调用时自动追踪
generate_images()
```

### 方式3：手动调用

需要精细控制时使用：

```python
from longtask_progress import LongTaskProgress

reporter = LongTaskProgress(
    task_name="数据分析",
    total_steps=100,
    interval=60  # 每1分钟报告
)

reporter.start()

try:
    for i in range(100):
        process_data(i)
        
        # 每10个数据点报告一次
        if i % 10 == 0:
            reporter.step(f"处理{i}/100")
            
        # 阶段性更新（不计入步骤）
        if i == 50:
            reporter.update("已完成50%，过半了")
            
finally:
    reporter.stop()  # 确保停止
```

## 参数说明

### LongTaskProgress 类

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| task_name | str | 必填 | 任务名称，用于报告标识 |
| total_steps | int | None | 总步骤数，用于计算百分比 |
| interval | int | 300 | 强制报告间隔（秒） |
| callback | callable | None | 自定义回调函数 |

### 方法

| 方法 | 用途 |
|------|------|
| start() | 启动进度报告 |
| step(message) | 完成一步并报告 |
| update(message) | 更新状态（不增加步骤数） |
| stop() | 停止进度报告 |

## 报告格式

**强制报告输出（每5分钟自动触发）：**

```
【强制报告 - 19:33:08】
  任务: 文章写作
  已用时间: 12.5分钟
  距离上次报告: 5.0分钟
  进度: 3/6 (50%)
  状态: 仍在执行中...
```

**步骤完成报告：**

```
【步骤完成】文章写作 - 第3步完成
  详情: 完成GameStop逼空章节
  总进度: 50%
```

**任务完成报告：**

```
【任务完成】文章写作 - 总耗时25.3分钟
```

## 实际应用场景

### 场景1：文章写作流程

```python
# Step 4: 写作
with LongTaskProgress("文章写作", total_steps=6, interval=300) as reporter:
    for section in ["引言", "历史", "事件", "影响", "风险", "结论"]:
        write(section)
        reporter.step(f"{section}完成约800字")

# Step 5: humanizer润色
with LongTaskProgress("humanizer润色", total_steps=23, interval=180) as reporter:
    for check in check_list:
        humanize_check(check)
        reporter.step(check)

# Step 6: 配图
with LongTaskProgress("文章配图", total_steps=3, interval=120) as reporter:
    for img in ["头图", "章节1", "章节2"]:
        generate_and_download(img)
        reporter.step(f"{img}完成")
```

### 场景2：批量文件下载

```python
@track_progress(task_name="批量下载", total_steps=10, interval=60)
def batch_download(urls, reporter):
    for i, url in enumerate(urls, 1):
        download_file(url)
        reporter.step(f"下载 {url}")

batch_download(url_list)
```

### 场景3：API轮询等待

```python
with LongTaskProgress("API轮询", interval=30) as reporter:
    while True:
        status = check_api_status()
        
        if status == "completed":
            reporter.step("API返回完成")
            break
        elif status == "failed":
            reporter.step("API失败")
            raise Exception("API调用失败")
        else:
            reporter.update(f"状态: {status}，继续轮询...")
            time.sleep(5)
```

## 高级用法

### 自定义回调

将报告发送到其他地方（如日志文件、消息队列）：

```python
def my_callback(data):
    """自定义处理报告数据"""
    if data['event'] == 'progress':
        # 发送到日志系统
        logger.info(f"进度: {data.get('progress_percent', 'N/A')}%")
    elif data['event'] == 'step':
        # 发送到用户界面
        ui.update_status(data['message'])

with LongTaskProgress(
    task_name="自定义任务",
    total_steps=10,
    callback=my_callback
) as reporter:
    # ... 执行任务
```

### 嵌套使用

复杂任务可以嵌套多个进度报告器：

```python
with LongTaskProgress("文章写作", total_steps=3, interval=300) as outer:
    
    for article in ["文章1", "文章2", "文章3"]:
        
        with LongTaskProgress(f"{article}配图", total_steps=3, interval=120) as inner:
            for img in ["头图", "图1", "图2"]:
                generate_image(img)
                inner.step(f"{img}完成")
                
        outer.step(f"{article}完成")
```

## 最佳实践

1. **合理设置interval**
   - 写作任务：300秒（5分钟）
   - 配图任务：120秒（2分钟）
   - API轮询：30-60秒

2. **合理拆分步骤**
   - 步骤不宜过大（>10分钟）
   - 步骤不宜过小（<10秒）
   - 保持5-20个步骤为宜

3. **提供有意义的step消息**
   - ❌ "完成第1步"
   - ✅ "完成引言章节（约800字）"

4. **使用上下文管理器**
   - 确保stop()被调用
   - 异常时也能正确清理

5. **不要嵌套过深**
   - 最多2层嵌套
   - 过多嵌套会造成混乱

## 故障排除

**问题：报告没有输出**
- 检查是否调用了start()
- 检查interval是否设置过大
- 检查stderr是否被重定向

**问题：步骤计数错误**
- 确保正确调用step()
- 检查total_steps设置是否正确

**问题：线程不停止**
- 确保调用stop()或使用with语句
- 检查是否有异常未处理

## 技术细节

- 使用threading.Timer实现定时报告
- 后台线程为daemon线程，主线程退出时自动结束
- 线程安全，可在多线程环境中使用
- 支持嵌套使用，互不影响

## 更新日志

- **v1.0** (2026-03-08)
  - 初始版本
  - 支持三种使用方式
  - 支持自定义回调
  - 支持嵌套使用

---

*保持专注，让长任务不再"睡着"*
