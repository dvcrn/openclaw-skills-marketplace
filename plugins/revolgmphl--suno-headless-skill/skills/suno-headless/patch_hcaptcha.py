#!/usr/bin/env python3
"""修改 hcaptcha-challenger 源码以支持 Suno 自定义 hCaptcha 域名"""
import hcaptcha_challenger.agent.challenger as mod

CHALLENGER_FILE = mod.__file__
print(f"📂 文件: {CHALLENGER_FILE}")

with open(CHALLENGER_FILE, "r") as f:
    lines = f.readlines()

changes = 0
new_lines = []
for i, line in enumerate(lines):
    ln = i + 1
    new_line = line

    if ln == 303:
        # XPath: starts-with(@src,'https://newassets.hcaptcha.com/captcha/v1/') → contains(@src, '/captcha/v1/')
        new_line = line.replace(
            "starts-with(@src,'https://newassets.hcaptcha.com/captcha/v1/')",
            "contains(@src, '/captcha/v1/')"
        )
    elif ln == 304:
        new_line = line.replace(
            "starts-with(@src,'https://newassets.hcaptcha.com/captcha/v1/')",
            "contains(@src, '/captcha/v1/')"
        )
    elif ln == 330:
        # Python: frame.url.startswith("https://...") → ("/captcha/v1/" in frame.url)
        new_line = line.replace(
            'frame.url.startswith("https://newassets.hcaptcha.com/captcha/v1/")',
            '("/captcha/v1/" in frame.url)'
        )
    elif ln == 357:
        # Python: child_frame.url.startswith("https://...") → ("/captcha/v1/" in child_frame.url)
        new_line = line.replace(
            'child_frame.url.startswith("https://newassets.hcaptcha.com/captcha/v1/")',
            '("/captcha/v1/" in child_frame.url)'
        )

    if new_line != line:
        changes += 1
        print(f"   ✅ L{ln}: {line.strip()[:60]} → {new_line.strip()[:60]}")
    new_lines.append(new_line)

with open(CHALLENGER_FILE, "w") as f:
    f.writelines(new_lines)

print(f"\n共修改 {changes} 处")

# 验证
with open(CHALLENGER_FILE, "r") as f:
    content = f.read()
remaining = content.count("newassets.hcaptcha.com")
if remaining > 0:
    print(f"⚠️ 仍有 {remaining} 处 newassets.hcaptcha.com 引用")
else:
    print("✅ 所有 hcaptcha.com 硬编码已移除")
