#!/usr/bin/env python3
"""
压缩 Word 文档中的嵌入图片，大幅减小文件体积
用法：python3 compress_docx.py <输入docx路径> <输出docx路径> [最大宽度] [图片质量]
默认：最大宽度600px，质量60%
"""

import sys
import os
import zipfile
import io
from PIL import Image

def compress_docx(src: str, dst: str, max_width: int = 600, quality: int = 60):
    size_before = os.path.getsize(src) / 1024 / 1024

    with zipfile.ZipFile(src, 'r') as zin:
        img_files = [f for f in zin.namelist() if f.startswith('word/media/')]
        print(f"📦 共 {len(img_files)} 张嵌入图片")

        with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.startswith('word/media/') and \
                   item.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        img = Image.open(io.BytesIO(data))
                        if img.width > max_width:
                            ratio = max_width / img.width
                            new_size = (max_width, int(img.height * ratio))
                            img = img.resize(new_size, Image.LANCZOS)
                        out_buf = io.BytesIO()
                        img.save(out_buf, format='JPEG', quality=quality)
                        data = out_buf.getvalue()
                    except Exception as e:
                        pass  # 压缩失败就保留原图
                zout.writestr(item, data)

    size_after = os.path.getsize(dst) / 1024 / 1024
    print(f"✅ 压缩完成: {size_before:.1f}MB → {size_after:.1f}MB")
    print(f"   输出: {dst}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 compress_docx.py <输入docx> <输出docx> [最大宽度=600] [质量=60]")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]
    max_width = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    quality = int(sys.argv[4]) if len(sys.argv) > 4 else 60

    if not os.path.exists(src):
        print(f"❌ 文件不存在: {src}")
        sys.exit(1)

    compress_docx(src, dst, max_width, quality)
