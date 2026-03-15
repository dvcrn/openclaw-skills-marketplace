#!/usr/bin/env python3
import os
import subprocess
import re
import argparse
from pathlib import Path

def get_sorted_videos(folder_path):
    """严格按文件名数字序号从小到大排序获取视频列表"""
    videos = []
    for f in os.listdir(folder_path):
        if f.lower().endswith(".mp4") and re.match(r"^\d+_", f):
            videos.append(f)
    if not videos:
        raise ValueError(f"目录 {folder_path} 下未找到符合命名规则（数字_开头）的MP4文件")
    videos.sort(key=lambda x: int(re.match(r"^(\d+)_", x).group(1)))
    return [os.path.join(folder_path, v) for v in videos]

def merge_videos(input_dir, output_path, custom_resolution=None, transition_duration=0.5):
    """
    合并目录下的所有分镜头视频为完整长视频
    :param input_dir: 分镜头视频所在目录
    :param output_path: 输出视频路径
    :param custom_resolution: 自定义分辨率，如"864x496"，默认保持原始分辨率
    :param transition_duration: 转场时长（秒）
    """
    video_list = get_sorted_videos(input_dir)
    n = len(video_list)
    print(f"找到 {n} 个视频片段，已按序号排序完成")

    # 获取原始分辨率
    if not custom_resolution:
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "default=noprint_wrappers=1:nokey=1",
            video_list[0]
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        height, width = result.stdout.strip().split("\n")[:2]
        custom_resolution = f"{width}x{height}"
        print(f"使用原始分辨率：{custom_resolution}")
    else:
        print(f"使用自定义分辨率：{custom_resolution}")

    # 生成concat列表
    concat_file = "./temp_concat_list.txt"
    with open(concat_file, "w") as f:
        for v in video_list:
            f.write(f"file '{os.path.abspath(v)}'\n")

    # 先无损拼接所有片段
    temp_raw = "./temp_raw.mp4"
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
        "-c", "copy", temp_raw
    ]
    print("正在拼接视频片段...")
    subprocess.run(cmd_concat, capture_output=True)

    # 获取总时长
    duration = float(subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", temp_raw],
        capture_output=True, text=True
    ).stdout.strip())

    # 统一参数+添加转场
    print("正在添加转场效果和编码...")
    cmd_final = [
        "ffmpeg", "-y", "-i", temp_raw,
        "-vf", f"scale={custom_resolution},fps=24,format=yuv420p,fade=t=in:st=0:d={transition_duration},fade=t=out:st={duration-transition_duration}:d={transition_duration}",
        "-af", f"afade=t=in:st=0:d={transition_duration},afade=t=out:st={duration-transition_duration}:d={transition_duration}",
        "-c:v", "h264", "-crf", "22", "-preset", "medium",
        "-c:a", "aac", "-ar", "44100", "-ac", "2",
        output_path
    ]
    subprocess.run(cmd_final, capture_output=True)

    # 清理临时文件
    os.remove(concat_file)
    os.remove(temp_raw)

    print(f"\n✅ 合并完成！")
    print(f"输出文件：{output_path}")
    print(f"总时长：{int(duration/60)}分{int(duration%60)}秒")
    print(f"文件大小：{os.path.getsize(output_path)/1024/1024:.1f}MB")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="多片段短视频自动拼接为完整长视频")
    parser.add_argument("--input", required=True, help="分镜头视频所在目录（文件需以数字_开头命名）")
    parser.add_argument("--output", required=True, help="输出视频文件路径，如./full.mp4")
    parser.add_argument("--resolution", help="自定义输出分辨率，如1080x1920，默认保持原始分辨率")
    parser.add_argument("--transition", type=float, default=0.5, help="淡入淡出转场时长（秒），默认0.5秒")
    
    args = parser.parse_args()
    merge_videos(args.input, args.output, args.resolution, args.transition)
