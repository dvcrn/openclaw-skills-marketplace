# 抖音数据采集 — 技术经验与踩坑记录

## 1. 登录与 Session

### Cookie 关键字段
登录成功的标志是 cookie 中出现：
- `passport_csrf_token`
- `sessionid`（部分环境）

### Cookie 有效期
Session 通常 7-30 天有效。若请求被重定向到登录页，需重新运行 `douyin_login.py`。

### 浏览器指纹
必须加以下反检测设置，否则极易触发验证码或被封：
```python
args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
# context init_script:
"Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
```

---

## 2. 数据采集

### API 拦截
- 搜索结果 API 端点包含：`search/item`
- 响应体结构：`{ "aweme_list": [...], "has_more": 1 }`
- `aweme_list[i]` 主要字段：
  - `aweme_id`：视频 ID
  - `desc`：标题（含 # 标签）
  - `statistics`: `{ digg_count, share_count, collect_count, comment_count }`
  - `author.uid`, `author.nickname`, `author.follower_count`
  - `video.duration`（毫秒）
  - `text_extra[].hashtag_name`：标签列表

### 滚动加载
- 每批滚动 8 次，每次 `window.scrollBy(0, 600)`，每次间隔 0.8s
- 滚动后等待 4s 让 API 响应完成
- 第1批直接导航，第2批起滚动

### 播放量解析
页面 DOM 中播放量为文本格式（如 `1.1万`），需要自行解析：
```python
def parse_count(text):
    text = text.strip().replace(",", "")
    if "万" in text: return int(float(text.replace("万","")) * 10000)
    if "亿" in text: return int(float(text.replace("亿","")) * 100000000)
    try: return int(text)
    except: return 0
```

---

## 3. 验证码处理（核心经验）

### 触发条件
- 详情页访问频繁时（约每5-10个视频触发一次）
- 验证码 iframe URL 包含 `verifycenter` 或 `captcha`

### 元素选择器
```python
bg_el  = frame.locator(".captcha-verify-image").first      # 背景图
sl_el  = frame.locator(".captcha-verify-image-slide").first  # 滑块图（叠在背景上）
btn_el = frame.locator(".captcha-slider-btn").first         # 滑块按钮
rb_el  = frame.locator(".vc-captcha-refresh,.captcha-refresh,[class*='refresh']").first  # 刷新按钮
```

### 缺口检测算法（已验证准确）

**关键发现**：
1. 模板匹配最准（检测缺口左边缘），用 `skimage.feature.match_template`
2. Sobel 双峰检测次之，左峰即缺口左边缘（右峰是缺口右边缘）
3. 注意遮掉背景图左上角的滑块叠加区域（用列均值填充），否则干扰检测

**遮掉滑块叠加区**：
```python
mask_w, mask_h = sl_w + 8, sl_h + 8
fill_col = np.mean(bg_arr[:, mask_w:mask_w+20], axis=1, keepdims=True)
bg_arr[:mask_h, :mask_w] = fill_col[:mask_h, :]
```

**搜索范围**：
```python
search_start = sl_w + 12   # 跳过初始滑块位置
search_end   = bg_w - 8
```

**决策逻辑**：
```python
if diff <= 25:
    gap_x = int(template_x * 0.7 + sobel_corrected * 0.3)
else:
    gap_x = template_x  # 差异大时纯用模板匹配
```

### 滑动距离公式
```python
# 中心对中心（不是左边缘对左边缘）
gap_center_abs = bg_bb["x"] + gap_x + sl_bb["width"] / 2
btn_center_abs = btn_bb["x"] + btn_bb["width"] / 2
slide_distance = gap_center_abs - btn_center_abs
```

### 仿真路径（ease-out + 过冲回拉）
- 使用 `ease_out_cubic(t) = 1 - (1-t)^3`（快启动，慢到位）
- 过冲 3-7px，最后 15% 线性回拉到正确位置
- Y 轴 ±2px 抖动，X 轴 ±1px 抖动
- 速度分段：前 50% 快（5-8ms），中间慢（10-18ms），最后最慢（25-45ms）

### 重试策略
- 最多 5 次重试
- 每次失败后点击刷新按钮换图，等待 1.5s
- 验证成功判断：captcha iframe 消失

---

## 4. 分析维度与关键结论

以「女性成长」100条视频为例，经实测：

| 因素 | 影响力 | 最优策略 |
|------|--------|---------|
| 视频时长 | 高 | 2-3 分钟（甜点区间，均赞高15×） |
| 标签数量 | 高 | 1-2个精准标签（堆标签反而差） |
| 标题感叹号 | 中高 | 含`！`平均赞提升约2× |
| 情感关键词 | 中 | 爱/婚姻/情绪等词提升转发 |
| 标题长度 | 中 | 11-20字最优 |
| 粉丝数 | 中 | log相关r=0.617，非决定因素 |
| 最佳标签 | 参考 | #自我成长 #个人成长 #认知 #女生必看 |

---

## 5. 常见问题

### Q: 采集时 API 返回空列表
- 可能是 session 过期 → 重新登录
- 可能是关键词无结果 → 换词

### Q: 验证码识别连续失败
- 检查 headless 是否为 False（截图必须有界面）
- 保存 debug_bg_*.png 截图肉眼确认缺口位置

### Q: 详情页数据为空
- 部分视频设置了隐私/仅粉丝可见
- 部分视频链接已失效（特别是发布时间久的）
