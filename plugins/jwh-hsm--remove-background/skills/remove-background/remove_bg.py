#!/usr/bin/env python3
"""remove_bg.py - Remove solid light background from an image and save as transparent PNG.

Usage:
    python remove_bg.py <input_image> <output_image> [threshold]

- <input_image>: path to source image (any Pillow‑supported format)
- <output_image>: where to save PNG with transparent background (must end with .png)
- threshold (optional, default 200): brightness threshold. Pixels where R, G and B are all > threshold become fully transparent.

The script works best with images that have a uniform light background (white, off‑white, light grey). For complex backgrounds use dedicated tools.
"""
import sys
from pathlib import Path
from PIL import Image

def remove_background(in_path: Path, out_path: Path, threshold: int = 200):
    img = Image.open(in_path).convert('RGBA')
    data = img.getdata()
    new_data = []
    for pixel in data:
        r, g, b, a = pixel
        if r > threshold and g > threshold and b > threshold:
            new_data.append((255, 255, 255, 0))  # transparent
        else:
            new_data.append((r, g, b, a))
    img.putdata(new_data)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, 'PNG')
    print(f'Saved transparent image to {out_path}')
    # 自动打开生成的 PNG（使用系统默认图片查看器）
    try:
        import subprocess, sys
        if sys.platform.startswith('win'):
            subprocess.run(['start', str(out_path)], shell=True, check=False)
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', str(out_path)], check=False)
        else:
            subprocess.run(['xdg-open', str(out_path)], check=False)
    except Exception as e:
        print('Failed to open image:', e)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python remove_bg.py <input> <output> [threshold]')
        sys.exit(1)
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    thr = int(sys.argv[3]) if len(sys.argv) >= 4 else 200
    remove_background(input_file, output_file, thr)
