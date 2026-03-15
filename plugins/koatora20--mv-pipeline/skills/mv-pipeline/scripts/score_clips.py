#!/usr/bin/env python3
"""
score_clips.py — AI生成動画の品質自動スコアリング

8秒のVeo生成クリップを分析して、
- NG素材を弾く（フリッカー、ぼけ、静止）
- ベスト区間を特定（motion + sharpness + consistency）
- BPM同期のカットポイントを提案

Usage:
    python3 score_clips.py --input-dir ./videos/ --output scores.json
    python3 score_clips.py --input-dir ./videos/ --output scores.json --bpm 140 --bar-beats 4
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import cv2
    import numpy as np
except ImportError:
    print("ERROR: opencv-python and numpy required.")
    print("  pip install opencv-python numpy")
    sys.exit(1)


def get_video_info(video_path: str) -> dict:
    """ffprobeで動画情報を取得"""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {}
    return json.loads(result.stdout)


def extract_frames(video_path: str, fps: float = 10.0) -> list:
    """OpenCVでフレーム抽出（指定FPSでサンプリング）"""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return []

    src_fps = cap.get(cv2.CAP_PROP_FPS)
    if src_fps <= 0:
        src_fps = 24.0

    frame_interval = max(1, int(src_fps / fps))
    frames = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_interval == 0:
            frames.append({
                "idx": frame_idx,
                "time": frame_idx / src_fps,
                "frame": frame
            })
        frame_idx += 1

    cap.release()
    return frames


def calc_sharpness(frame: np.ndarray) -> float:
    """Laplacian varianceでシャープネス計測（高い=シャープ）"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    return float(lap.var())


def calc_ssim_pair(frame_a: np.ndarray, frame_b: np.ndarray) -> float:
    """2フレーム間のSSIM（構造類似度）を計算"""
    gray_a = cv2.cvtColor(frame_a, cv2.COLOR_BGR2GRAY)
    gray_b = cv2.cvtColor(frame_b, cv2.COLOR_BGR2GRAY)

    # リサイズして統一
    h, w = min(gray_a.shape[0], gray_b.shape[0]), min(gray_a.shape[1], gray_b.shape[1])
    gray_a = cv2.resize(gray_a, (w, h))
    gray_b = cv2.resize(gray_b, (w, h))

    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2

    mu_a = cv2.GaussianBlur(gray_a.astype(np.float64), (11, 11), 1.5)
    mu_b = cv2.GaussianBlur(gray_b.astype(np.float64), (11, 11), 1.5)

    sigma_a2 = cv2.GaussianBlur(gray_a.astype(np.float64) ** 2, (11, 11), 1.5) - mu_a ** 2
    sigma_b2 = cv2.GaussianBlur(gray_b.astype(np.float64) ** 2, (11, 11), 1.5) - mu_b ** 2
    sigma_ab = cv2.GaussianBlur(
        gray_a.astype(np.float64) * gray_b.astype(np.float64), (11, 11), 1.5
    ) - mu_a * mu_b

    ssim_map = ((2 * mu_a * mu_b + C1) * (2 * sigma_ab + C2)) / \
               ((mu_a ** 2 + mu_b ** 2 + C1) * (sigma_a2 + sigma_b2 + C2))

    return float(ssim_map.mean())


def calc_motion(frame_a: np.ndarray, frame_b: np.ndarray) -> float:
    """フレーム間の動き量（ピクセル差分の平均）"""
    gray_a = cv2.cvtColor(frame_a, cv2.COLOR_BGR2GRAY).astype(np.float64)
    gray_b = cv2.cvtColor(frame_b, cv2.COLOR_BGR2GRAY).astype(np.float64)

    h, w = min(gray_a.shape[0], gray_b.shape[0]), min(gray_a.shape[1], gray_b.shape[1])
    gray_a = cv2.resize(gray_a, (w, h))
    gray_b = cv2.resize(gray_b, (w, h))

    diff = np.abs(gray_a - gray_b)
    return float(diff.mean())


def detect_flicker(frames: list, threshold: float = 30.0) -> list:
    """急激な輝度変化（フリッカー）を検出"""
    flicker_points = []
    for i in range(1, len(frames)):
        brightness_a = frames[i - 1]["frame"].mean()
        brightness_b = frames[i]["frame"].mean()
        delta = abs(brightness_b - brightness_a)
        if delta > threshold:
            flicker_points.append({
                "time": frames[i]["time"],
                "delta": round(delta, 2)
            })
    return flicker_points


def score_segment(frames: list, start_idx: int, end_idx: int) -> dict:
    """フレーム区間のスコアを計算"""
    seg_frames = frames[start_idx:end_idx + 1]
    if len(seg_frames) < 2:
        return {"score": 0, "motion": 0, "sharpness": 0, "consistency": 0, "flicker": 0}

    # シャープネス: 全フレームの平均
    sharpness_vals = [calc_sharpness(f["frame"]) for f in seg_frames]
    avg_sharpness = np.mean(sharpness_vals)
    # 正規化（0-1）: 典型的なVeo出力は100-2000くらい
    sharpness_norm = min(1.0, avg_sharpness / 500.0)

    # モーション: 連続フレーム間の平均動き
    motion_vals = []
    for i in range(1, len(seg_frames)):
        motion_vals.append(calc_motion(seg_frames[i - 1]["frame"], seg_frames[i]["frame"]))
    avg_motion = np.mean(motion_vals) if motion_vals else 0
    # 正規化: 動きすぎもNG（5-30が理想）
    if avg_motion < 2:
        motion_norm = avg_motion / 2 * 0.3  # 静止に近い = 低スコア
    elif avg_motion > 50:
        motion_norm = max(0, 1.0 - (avg_motion - 50) / 100)  # 動きすぎ = 減点
    else:
        motion_norm = min(1.0, avg_motion / 30.0)

    # 一貫性（SSIM）: 隣接フレーム間の平均SSIM
    ssim_vals = []
    for i in range(1, len(seg_frames)):
        ssim_vals.append(calc_ssim_pair(seg_frames[i - 1]["frame"], seg_frames[i]["frame"]))
    avg_ssim = np.mean(ssim_vals) if ssim_vals else 1.0
    # SSIMが低すぎる = モーフィング崩壊
    consistency_norm = max(0, (avg_ssim - 0.5) / 0.5)

    # フリッカーペナルティ
    flicker_count = 0
    for i in range(1, len(seg_frames)):
        b_a = seg_frames[i - 1]["frame"].mean()
        b_b = seg_frames[i]["frame"].mean()
        if abs(b_b - b_a) > 30:
            flicker_count += 1
    flicker_penalty = min(1.0, flicker_count / max(1, len(seg_frames) - 1))

    # 総合スコア
    score = (
        0.25 * motion_norm +
        0.30 * sharpness_norm +
        0.30 * consistency_norm -
        0.40 * flicker_penalty
    )
    score = max(0.0, min(1.0, score))

    return {
        "score": round(score, 3),
        "motion": round(motion_norm, 3),
        "sharpness": round(sharpness_norm, 3),
        "consistency": round(consistency_norm, 3),
        "flicker_penalty": round(flicker_penalty, 3),
        "raw": {
            "avg_sharpness": round(avg_sharpness, 1),
            "avg_motion": round(avg_motion, 1),
            "avg_ssim": round(avg_ssim, 4),
            "flicker_count": flicker_count
        }
    }


def find_best_segments(frames: list, segment_duration: float = 1.71,
                       sample_fps: float = 10.0) -> list:
    """ベスト区間を1小節（segment_duration秒）単位で探す"""
    if not frames:
        return []

    total_time = frames[-1]["time"] if frames else 0
    seg_frame_count = max(2, int(segment_duration * sample_fps))

    segments = []
    i = 0
    seg_idx = 0

    while i + seg_frame_count <= len(frames):
        result = score_segment(frames, i, i + seg_frame_count - 1)
        start_time = frames[i]["time"]
        end_time = frames[min(i + seg_frame_count - 1, len(frames) - 1)]["time"]

        segments.append({
            "segment_idx": seg_idx,
            "start": round(start_time, 3),
            "end": round(end_time, 3),
            "duration": round(end_time - start_time, 3),
            **result
        })

        # 半分ずつオーバーラップしてスライド
        i += max(1, seg_frame_count // 2)
        seg_idx += 1

    # スコア順にソート
    segments.sort(key=lambda s: s["score"], reverse=True)
    return segments


def analyze_clip(video_path: str, bpm: float = 140.0,
                 bar_beats: int = 4, sample_fps: float = 10.0) -> dict:
    """1クリップの完全分析"""
    path = Path(video_path)

    # 動画情報
    info = get_video_info(video_path)
    if not info:
        return {"file": path.name, "status": "error", "message": "Cannot read video"}

    # duration取得
    duration = 0
    if "format" in info and "duration" in info["format"]:
        duration = float(info["format"]["duration"])

    # フレーム抽出
    frames = extract_frames(video_path, fps=sample_fps)
    if len(frames) < 4:
        return {"file": path.name, "status": "error", "message": "Too few frames"}

    # 全体スコア
    overall = score_segment(frames, 0, len(frames) - 1)

    # フリッカー検出
    flickers = detect_flicker(frames)

    # 1小節 = bar_beats / bpm * 60
    bar_duration = bar_beats / bpm * 60

    # ベスト区間を探索
    best_segments = find_best_segments(frames, segment_duration=bar_duration,
                                       sample_fps=sample_fps)

    # NG判定
    is_ng = False
    ng_reasons = []
    if overall["score"] < 0.15:
        is_ng = True
        ng_reasons.append("overall_score_too_low")
    if overall["raw"]["avg_motion"] < 1.0:
        is_ng = True
        ng_reasons.append("nearly_static")
    if overall["flicker_penalty"] > 0.5:
        is_ng = True
        ng_reasons.append("heavy_flicker")
    if overall["raw"]["avg_ssim"] < 0.4:
        is_ng = True
        ng_reasons.append("morphing_collapse")
    if overall["raw"]["avg_sharpness"] < 30:
        is_ng = True
        ng_reasons.append("extremely_blurry")

    # ベスト区間（トップ3）
    top_segments = best_segments[:3] if best_segments else []

    return {
        "file": path.name,
        "path": str(path.absolute()),
        "status": "ng" if is_ng else "ok",
        "ng_reasons": ng_reasons,
        "duration": round(duration, 2),
        "overall": overall,
        "flicker_points": flickers[:5],  # 上位5件
        "bar_duration": round(bar_duration, 3),
        "best_segments": top_segments,
        "best_cut": {
            "start": top_segments[0]["start"] if top_segments else 0,
            "end": top_segments[0]["end"] if top_segments else 0,
            "score": top_segments[0]["score"] if top_segments else 0
        } if top_segments else None
    }


def main():
    parser = argparse.ArgumentParser(
        description="AI生成動画の品質スコアリング＆ベスト区間検出"
    )
    parser.add_argument("--input-dir", "-i", required=True,
                        help="動画ディレクトリ")
    parser.add_argument("--output", "-o", default="scores.json",
                        help="出力JSONファイル (default: scores.json)")
    parser.add_argument("--bpm", type=float, default=140.0,
                        help="楽曲BPM (default: 140)")
    parser.add_argument("--bar-beats", type=int, default=4,
                        help="1小節の拍数 (default: 4)")
    parser.add_argument("--sample-fps", type=float, default=10.0,
                        help="分析サンプリングFPS (default: 10)")
    parser.add_argument("--single", "-s", type=str, default=None,
                        help="1ファイルだけ分析")
    args = parser.parse_args()

    if args.single:
        result = analyze_clip(args.single, bpm=args.bpm,
                              bar_beats=args.bar_beats, sample_fps=args.sample_fps)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"ERROR: Directory not found: {input_dir}")
        sys.exit(1)

    # 動画ファイルを収集
    video_exts = {".mp4", ".webm", ".mov", ".avi", ".mkv"}
    videos = sorted([
        f for f in input_dir.iterdir()
        if f.suffix.lower() in video_exts
    ])

    if not videos:
        print(f"No video files found in {input_dir}")
        sys.exit(1)

    print(f"📹 {len(videos)} clips found in {input_dir}")
    print(f"🎵 BPM: {args.bpm} → 1 bar = {4 / args.bpm * 60:.3f}s")
    print()

    results = []
    ok_count = 0
    ng_count = 0

    for idx, video in enumerate(videos):
        print(f"  [{idx + 1}/{len(videos)}] {video.name}...", end=" ", flush=True)
        result = analyze_clip(str(video), bpm=args.bpm,
                              bar_beats=args.bar_beats, sample_fps=args.sample_fps)
        results.append(result)

        if result["status"] == "ok":
            ok_count += 1
            best = result.get("best_cut")
            if best:
                print(f"✅ score={result['overall']['score']:.3f} "
                      f"best=[{best['start']:.1f}s-{best['end']:.1f}s]={best['score']:.3f}")
            else:
                print(f"✅ score={result['overall']['score']:.3f}")
        elif result["status"] == "ng":
            ng_count += 1
            print(f"❌ NG: {', '.join(result['ng_reasons'])}")
        else:
            ng_count += 1
            print(f"⚠️  {result.get('message', 'error')}")

    # サマリー
    total = len(results)
    yield_rate = ok_count / total * 100 if total > 0 else 0
    ok_results = [r for r in results if r["status"] == "ok"]
    avg_score = np.mean([r["overall"]["score"] for r in ok_results]) if ok_results else 0

    total_usable_time = sum(
        r["best_cut"]["end"] - r["best_cut"]["start"]
        for r in ok_results
        if r.get("best_cut")
    )

    summary = {
        "total_clips": total,
        "ok": ok_count,
        "ng": ng_count,
        "yield_rate": round(yield_rate, 1),
        "avg_score": round(float(avg_score), 3),
        "total_usable_seconds": round(total_usable_time, 1),
        "bpm": args.bpm,
        "bar_duration": round(4 / args.bpm * 60, 3),
        "estimated_bars": int(total_usable_time / (4 / args.bpm * 60))
    }

    output = {
        "summary": summary,
        "clips": results
    }

    # 出力
    output_path = Path(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 50)
    print(f"📊 結果サマリー")
    print(f"  OK: {ok_count}/{total} ({yield_rate:.0f}%)")
    print(f"  NG: {ng_count}/{total}")
    print(f"  平均スコア: {avg_score:.3f}")
    print(f"  使える素材: {total_usable_time:.1f}秒 ({summary['estimated_bars']}小節)")
    print(f"  出力: {output_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
