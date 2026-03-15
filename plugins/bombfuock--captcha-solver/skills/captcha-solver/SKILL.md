---
name: captcha-solver
description: "验证码识别与解决 - 本地OCR识别 + 第三方API / CAPTCHA Recognition and Solving - Local OCR + Third-party APIs"
---

# 验证码识别与解决 / CAPTCHA Solver

自动识别和解决各类验证码 / Automatically recognize and solve various CAPTCHAs

## 支持类型 / Supported Types

### 本地OCR识别 / Local OCR (免费/Free)
- 🔤 简单文本验证码 / Simple text CAPTCHA
- 🔢 数字验证码 / Numeric CAPTCHA
- ➕ 数学运算验证码 / Math CAPTCHA
- 🖼️ 滑动验证码(缺口检测) / Slide CAPTCHA (gap detection)

### API解决 / API Solving (付费/APIs)
- reCAPTCHA v2/v3
- hCaptcha
- Cloudflare Turnstile
- 2Captcha / Anti-Captcha

## 使用方法 / Usage

```bash
# 识别图片验证码
python solve.py --image captcha.png

# 解决reCaptcha
python solve.py --recaptcha "site_key" --url "page_url"

# 滑动验证码
python solve.py --slide background.png --template slider.png
```

## 配置 / Configuration

### 本地OCR
```python
# 默认使用Tesseract
TESSERACT_CMD = "/usr/bin/tesseract"
LANG = "eng+chi_sim"  # 支持中英文
```

### API服务 (可选)
```python
# 2Captcha
API_2CAPTCHA = "your_api_key"

# Anti-Captcha  
API_ANTI_CAPTCHA = "your_api_key"
```

## 算法 / Algorithms

### 1. 图像预处理
- 灰度转换 / Grayscale
- 二值化 / Binarization
- 去噪 / Denoising
- 锐化 / Sharpening

### 2. 字符分割
- 连通域分析 / Connected component analysis
- 投影法 / Projection method

### 3. 字符识别
- 模板匹配 / Template matching
- 机器学习 / ML-based OCR

### 4. 滑动验证码
- 边缘检测 / Edge detection
- 缺口定位 / Gap localization
- 轨迹生成 / Trajectory generation

## 示例 / Examples

### 简单文本识别
```python
from solver import CaptchaSolver

solver = CaptchaSolver()
result = solver.solve_image("captcha.png")
print(result)  # 输出识别的字符
```

### 滑动验证码
```python
result = solver.solve_slide(bg_img, slider_img)
print(result)  # 输出滑动距离
```

### reCaptcha
```python
result = solver.solve_recaptcha(site_key, page_url)
print(result)  # 输出token
```

## 服务对比 / Service Comparison

| 服务 | 价格 | 成功率 | 速度 |
|------|------|--------|------|
| 本地OCR | 免费 | 60-80% | 快 |
| 2Captcha | $2.99/1000 | 95%+ | 慢 |
| Anti-Captcha | $2.00/1000 | 95%+ | 中 |

## 注意事项 / Notes

1. 优先使用本地OCR，失败再调用API
2. 遵守网站使用条款
3. 不要用于非法用途
