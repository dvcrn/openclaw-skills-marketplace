#!/usr/bin/env python3
"""进入案件详情页 → 点击查看商家详情 → 点所有"查看明文" → 截图弹框。

用法:
    python merchant_screenshot.py <case_id>
    python merchant_screenshot.py <case_id> --output merchant.png
    python merchant_screenshot.py <case_id> --timeout 15000

使用 JoyDesk SDK 的 PlaywrightBrowser（通过 playwright-component 后端执行，
不需要本地安装 Playwright）。
"""
import argparse
import json
import re
import sys
import time

from joydesk_sdk import PlaywrightBrowser

CASE_DETAIL_URL = "https://jdlawsuit-web.jd.com/#/case-detail?no={case_id}"


def find_ref_by_text(snapshot_text: str, target_texts: list[str]) -> int | None:
    """从 snapshot 文本中根据目标文字找到 ref 编号。"""
    for target in target_texts:
        # 在 snapshot 中搜索包含目标文本的行，提取 ref 数字
        for line in snapshot_text.split("\n"):
            if target in line:
                match = re.search(r'ref=(\d+)', line)
                if match:
                    return int(match.group(1))
    return None


def find_all_refs_by_text(snapshot_text: str, target_texts: list[str]) -> list[int]:
    """找出所有匹配目标文字的 ref。"""
    refs = []
    for target in target_texts:
        for line in snapshot_text.split("\n"):
            if target in line:
                match = re.search(r'ref=(\d+)', line)
                if match:
                    refs.append(int(match.group(1)))
    return refs


def take_merchant_screenshot(case_id: str, output_path: str, timeout_ms: int = 15000):
    """
    完整流程:
    1. 打开案件详情页（带 Electron cookie）
    2. 找到并点击"查看商家详情"或类似按钮
    3. 等待弹框出现
    4. 点击所有"查看明文"按钮
    5. 截图
    """
    br = PlaywrightBrowser()

    # 1. 打开案件详情页
    url = CASE_DETAIL_URL.format(case_id=case_id)
    print(f"[1/5] 打开案件详情: {url}", file=sys.stderr)
    tab = br.open(url, sync_cookies=True, timeout=timeout_ms)
    tab_id = tab["browserTabId"]

    # 等待页面加载
    br.smart_wait(tab_id, timeout=timeout_ms)

    # 2. 获取页面快照，找商家详情入口
    print("[2/5] 查找商家详情入口...", file=sys.stderr)
    snap = br.snapshot(tab_id)
    snap_text = json.dumps(snap, ensure_ascii=False) if isinstance(snap, dict) else str(snap)

    # 尝试多个可能的按钮文本
    merchant_texts = ["查看商家详情", "店铺信息", "商家详情", "商家信息"]
    merchant_ref = find_ref_by_text(snap_text, merchant_texts)

    if merchant_ref is not None:
        print(f"  → 找到入口 ref={merchant_ref}", file=sys.stderr)
        br.click(tab_id, merchant_ref)
    else:
        # 尝试 click_by_text 作为后备
        print("  → 未在 snapshot 中找到，尝试 click_by_text...", file=sys.stderr)
        for text in merchant_texts:
            try:
                br.click_by_text(tab_id, text)
                print(f"  → 点击了: {text}", file=sys.stderr)
                break
            except Exception:
                continue
        else:
            print("  ✗ 无法找到商家详情入口", file=sys.stderr)
            # 截全页作为回退
            br.screenshot(tab_id, full_page=True, save_path=output_path)
            print(f"已保存全页截图: {output_path}")
            br.close_tab(tab_id)
            return

    # 3. 等待弹框出现
    print("[3/5] 等待弹框...", file=sys.stderr)
    time.sleep(2)  # 给弹框动画时间
    br.smart_wait(tab_id, timeout=5000, stable_time=1000)

    # 4. 点击所有"查看明文"
    print("[4/5] 点击所有'查看明文'...", file=sys.stderr)
    snap2 = br.snapshot(tab_id)
    snap2_text = json.dumps(snap2, ensure_ascii=False) if isinstance(snap2, dict) else str(snap2)

    plaintext_texts = ["查看明文", "显示明文"]
    refs = find_all_refs_by_text(snap2_text, plaintext_texts)
    print(f"  → 找到 {len(refs)} 个明文按钮", file=sys.stderr)

    for ref in refs:
        try:
            br.click(tab_id, ref)
            time.sleep(0.5)
        except Exception as e:
            print(f"  ⚠ 点击 ref={ref} 失败: {e}", file=sys.stderr)

    # 等待解密完成
    if refs:
        time.sleep(1)

    # 5. 截图
    print("[5/5] 截图...", file=sys.stderr)
    br.screenshot(tab_id, save_path=output_path)
    print(f"截图已保存: {output_path}")

    br.close_tab(tab_id)


def main():
    parser = argparse.ArgumentParser(description="案件商家详情截图（含明文解密）")
    parser.add_argument("case_id", help="案件 ID（case_list 返回的 id 字段）")
    parser.add_argument("--output", "-o", default=None, help="输出路径（默认 merchant_<id>.png）")
    parser.add_argument("--timeout", type=int, default=15000, help="页面加载超时毫秒数（默认15000）")
    args = parser.parse_args()

    if args.output is None:
        safe_name = args.case_id.replace("/", "_").replace("\\", "_")
        args.output = f"merchant_{safe_name}.png"

    take_merchant_screenshot(args.case_id, args.output, args.timeout)


if __name__ == "__main__":
    main()
