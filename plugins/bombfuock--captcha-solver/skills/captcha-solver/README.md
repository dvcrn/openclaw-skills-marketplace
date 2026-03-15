# 验证码识别与解决 / CAPTCHA Solver

自动识别和解决各类验证码

## 功能 / Features

- 📷 图片验证码识别 (OCR)
- 🖱️ 滑动验证码解决
- 🤖 reCaptcha解决 (API)
- 🔧 支持本地识别和API调用

## 安装 / Install

```bash
# 安装依赖
pip install pillow numpy opencv-python

# 可选：安装Tesseract
# Ubuntu: apt install tesseract-ocr
# Mac: brew install tesseract
```

## 使用 / Usage

```bash
# 识别图片验证码
python scripts/solve.py --image captcha.png

# 解决滑动验证码
python scripts/solve.py --slide-bg bg.png --slide-slider slider.png

# 解决reCaptcha (需要API)
python scripts/solve.py --recaptcha-key "site_key" --recaptcha-url "https://..."
```

## API / API

```python
from solver import CaptchaSolver

solver = CaptchaSolver()

# 图片验证码
result = solver.solve_image("captcha.png")

# 滑动验证码
result = solver.solve_slide(bg.png, slider.png)
```

## 环境变量

```bash
export API_2CAPTCHA="your_api_key"
```

## 注意

仅供学习研究使用，请遵守网站服务条款。
