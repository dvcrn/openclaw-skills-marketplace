#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证码识别与解决脚本 / CAPTCHA Recognition and Solving Script
支持：图片验证码、滑动验证码、reCaptcha
"""

import os
import sys
import argparse
import base64
import json
import time
import subprocess
from pathlib import Path

# 配置 / Configuration
TESSERACT_CMD = "/usr/bin/tesseract"
LANG = "eng"
API_2CAPTCHA = os.getenv("API_2CAPTCHA", "")

class CaptchaSolver:
    """验证码解决器 / CAPTCHA Solver"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or API_2CAPTCHA
        self.tesseract_cmd = TESSERACT_CMD
        
    def solve_image(self, image_path, lang=None):
        """
        识别图片验证码 / Recognize image CAPTCHA
        """
        lang = lang or LANG
        
        # 预处理图像
        processed = self._preprocess(image_path)
        
        # OCR识别
        try:
            result = subprocess.run(
                [self.tesseract_cmd, processed, "stdout", 
                 "-l", lang, "--psm", "8"],
                capture_output=True, text=True, timeout=30
            )
            text = result.stdout.strip()
            # 清理结果
            text = self._clean_text(text)
            return text
        except Exception as e:
            print(f"OCR识别失败 / OCR failed: {e}")
            return None
    
    def _preprocess(self, image_path):
        """
        图像预处理 / Image preprocessing
        """
        # 尝试使用PIL进行预处理
        try:
            from PIL import Image, ImageEnhance, ImageFilter
            import numpy as np
            
            img = Image.open(image_path)
            
            # 灰度
            img = img.convert('L')
            
            # 对比度增强
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
            
            # 二值化
            img = img.point(lambda x: 0 if x < 128 else 255, '1')
            
            # 保存处理后的图像
            processed = "/tmp/captcha_processed.png"
            img.save(processed)
            return processed
            
        except ImportError:
            # 如果没有PIL，返回原图
            return image_path
    
    def _clean_text(self, text):
        """清理识别结果 / Clean OCR result"""
        # 只保留字母数字
        import re
        text = re.sub(r'[^a-zA-Z0-9]', '', text)
        return text.upper()
    
    def solve_slide(self, background_path, slider_path):
        """
        滑动验证码解决 / Solve slide CAPTCHA
        """
        try:
            from PIL import Image
            import numpy as np
            
            # 读取图片
            bg = Image.open(background_path)
            slider = Image.open(slider_path)
            
            # 转为numpy数组
            bg_arr = np.array(bg)
            slider_arr = np.array(slider)
            
            # 边缘检测找缺口
            import cv2
            bg_gray = cv2.cvtColor(bg_arr, cv2.COLOR_RGB2GRAY)
            slider_gray = cv2.cvtColor(slider_arr, cv2.COLOR_RGB2GRAY)
            
            # 模板匹配
            result = cv2.matchTemplate(bg_gray, slider_gray, cv2.TM_CCOEFF_NORMED)
            _, _, _, max_loc = cv2.minMaxLoc(result)
            
            distance = max_loc[0]
            
            # 生成滑动轨迹
            trajectory = self._generate_trajectory(distance)
            
            return {
                "distance": distance,
                "trajectory": trajectory
            }
            
        except ImportError as e:
            print(f"需要OpenCV / Need OpenCV: {e}")
            return None
    
    def _generate_trajectory(self, distance):
        """
        生成人类-like滑动轨迹 / Generate human-like slide trajectory
        """
        import random
        
        trajectory = []
        current = 0
        speed = random.randint(5, 15)
        
        while current < distance:
            # 添加一些随机波动
            step = speed + random.randint(-3, 3)
            current += step
            if current > distance:
                current = distance
            trajectory.append(current)
            time.sleep(random.uniform(0.01, 0.03))
        
        return trajectory
    
    def solve_recaptcha(self, site_key, url):
        """
        解决reCaptcha (通过API) / Solve reCaptcha (via API)
        """
        if not self.api_key:
            print("需要2Captcha API密钥 / Need 2Captcha API key")
            return None
        
        # 提交任务
        import urllib.request
        import urllib.parse
        
        # 1. 提交
        submit_url = f"http://2captcha.com/in.php?key={self.api_key}&method=userrecaptcha&googlekey={site_key}&pageurl={url}"
        resp = urllib.request.urlopen(submit_url, timeout=10)
        result = resp.read().decode()
        
        if not result.startswith("OK|"):
            print(f"提交失败 / Submit failed: {result}")
            return None
        
        captcha_id = result.split("|")[1]
        
        # 2. 等待结果
        for _ in range(30):
            time.sleep(5)
            result_url = f"http://2captcha.com/res.php?key={self.api_key}&action=get&id={captcha_id}"
            resp = urllib.request.urlopen(result_url, timeout=10)
            result = resp.read().decode()
            
            if result == "CAPCHA_NOT_READY":
                continue
            elif result.startswith("OK|"):
                return result.split("|")[1]
            else:
                print(f"识别失败 / Solve failed: {result}")
                return None
        
        return None
    
    def solve_2captcha(self, image_path):
        """
        通过2Captcha API识别 / Solve via 2Captcha API
        """
        if not self.api_key:
            print("需要API密钥 / Need API key")
            return None
        
        # 读取图片并转为base64
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        
        # 提交
        import urllib.request
        import urllib.parse
        
        submit_url = f"http://2captcha.com/in.php?key={self.api_key}&method=base64&body={img_data}"
        resp = urllib.request.urlopen(submit_url, timeout=10)
        result = resp.read().decode()
        
        if not result.startswith("OK|"):
            print(f"提交失败 / Submit failed: {result}")
            return None
        
        captcha_id = result.split("|")[1]
        
        # 等待结果
        for _ in range(20):
            time.sleep(3)
            result_url = f"http://2captcha.com/res.php?key={self.api_key}&action=get&id={captcha_id}"
            resp = urllib.request.urlopen(result_url, timeout=10)
            result = resp.read().decode()
            
            if result == "CAPCHA_NOT_READY":
                continue
            elif result.startswith("OK|"):
                return result.split("|")[1]
            else:
                print(f"识别失败 / Solve failed: {result}")
                return None
        
        return None


def main():
    parser = argparse.ArgumentParser(description='验证码识别 / CAPTCHA Solver')
    parser.add_argument("--image", help="图片验证码路径 / Image CAPTCHA path")
    parser.add_argument("--slide-bg", help="滑动验证码背景图 / Slide CAPTCHA background")
    parser.add_argument("--slide-slider", help="滑动验证码滑块 / Slide CAPTCHA slider")
    parser.add_argument("--recaptcha-key", help="reCaptcha site key")
    parser.add_argument("--recaptcha-url", help="reCaptcha page URL")
    parser.add_argument("--lang", default="eng", help="语言 / Language")
    parser.add_argument("--api-key", help="2Captcha API key")
    
    args = parser.parse_args()
    
    solver = CaptchaSolver(api_key=args.api_key)
    
    if args.image:
        print(f"识别图片验证码 / Recognizing image CAPTCHA: {args.image}")
        result = solver.solve_image(args.image, args.lang)
        print(f"结果 / Result: {result}")
        
    elif args.slide_bg and args.slide_slider:
        print(f"解决滑动验证码 / Solving slide CAPTCHA")
        result = solver.solve_slide(args.slide_bg, args.slide_slider)
        print(f"滑动距离 / Distance: {result.get('distance') if result else 'Failed'}")
        
    elif args.recaptcha_key and args.recaptcha_url:
        print(f"解决reCaptcha / Solving reCaptcha")
        result = solver.solve_recaptcha(args.recaptcha_key, args.recaptcha_url)
        print(f"Token: {result}")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
