#!/usr/bin/env python3
"""
Douyin Video Transcription Script (Cross-platform)

Usage:
    python transcribe.py --video-url <CDN_URL> [options]
    python transcribe.py --url <douyin_link> --video-url <CDN_URL> [options]

Options:
    --video-url, -v   Video CDN URL (required, get from browser)
    --url, -u         Original Douyin link (for extracting video ID)
    --video-id        Specify video ID directly (if --url not provided)
    --output-dir, -o  Output directory, default current dir
    --model, -m       Whisper model: tiny/base/small/medium, default small
    --language, -l    Language: zh/en/auto, default zh
    --keep-files      Keep intermediate files (wav)

Examples:
    python transcribe.py -v "https://v5-dy-o-abtest.zjcdn.com/..." -o ./output
    python transcribe.py -u "https://v.douyin.com/xxx/" -v "https://..." --model base

Note:
    Video CDN URL must be obtained via browser first.
    See SKILL.md or use get_video_url.js for extraction method.
"""

import argparse
import subprocess
import sys
import re
import os
import platform
from pathlib import Path


def get_curl_cmd():
    """Get curl command (Windows needs curl.exe)"""
    return "curl.exe" if platform.system() == "Windows" else "curl"


def run_cmd(cmd, check=True, capture=False, shell=True):
    """Execute command"""
    print(f"[CMD] {cmd}")
    try:
        if capture:
            result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
            if result.returncode != 0 and check:
                print(f"[STDERR] {result.stderr}")
                raise RuntimeError(f"Command failed: {cmd}")
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=shell, check=check)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {e}")
        raise


def resolve_short_url(url):
    """Resolve Douyin short URL"""
    if "v.douyin.com" not in url:
        return url
    
    curl = get_curl_cmd()
    null_dev = "NUL" if platform.system() == "Windows" else "/dev/null"
    cmd = f'{curl} -sL -o {null_dev} -w "%{{url_effective}}" "{url}"'
    resolved = run_cmd(cmd, capture=True)
    print(f"[INFO] Short URL resolved: {url} -> {resolved}")
    return resolved


def extract_video_id(url):
    """Extract video ID from URL"""
    # Match /video/digits
    match = re.search(r'/video/(\d+)', url)
    if match:
        return match.group(1)
    
    # Match any 15-19 digit number
    match = re.search(r'(\d{15,19})', url)
    if match:
        return match.group(1)
    
    return None


def download_video(video_url, output_path):
    """Download video"""
    curl = get_curl_cmd()
    cmd = f'{curl} -L -H "Referer: https://www.douyin.com/" -o "{output_path}" "{video_url}"'
    run_cmd(cmd)
    
    if not os.path.exists(output_path):
        raise RuntimeError("Download failed: file not found")
    
    size = os.path.getsize(output_path)
    if size < 1000:
        raise RuntimeError(f"Download failed: file too small ({size} bytes), possibly 403 or expired URL")
    
    print(f"[INFO] Video downloaded: {output_path} ({size / 1024 / 1024:.1f} MB)")


def extract_audio(video_path, audio_path):
    """Extract audio"""
    cmd = f'ffmpeg -i "{video_path}" -ar 16000 -ac 1 -c:a pcm_s16le "{audio_path}" -y'
    run_cmd(cmd)
    
    if not os.path.exists(audio_path):
        raise RuntimeError("Audio extraction failed")
    
    print(f"[INFO] Audio extracted: {audio_path}")


def transcribe(audio_path, output_dir, model="small", language="zh"):
    """Transcribe audio"""
    lang_arg = "" if language == "auto" else f"--language {language}"
    cmd = f'python -m whisper "{audio_path}" --model {model} {lang_arg} --output_dir "{output_dir}"'
    run_cmd(cmd)
    
    # Find output file
    audio_name = Path(audio_path).stem
    txt_path = os.path.join(output_dir, f"{audio_name}.txt")
    
    if os.path.exists(txt_path):
        print(f"[INFO] Transcription complete: {txt_path}")
        return txt_path
    
    raise RuntimeError(f"Transcription output not found: {txt_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Douyin Video Transcription (Cross-platform)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--video-url", "-v", required=True, help="Video CDN URL (from browser)")
    parser.add_argument("--url", "-u", help="Original Douyin link (for video ID)")
    parser.add_argument("--video-id", help="Specify video ID directly")
    parser.add_argument("--output-dir", "-o", default=".", help="Output directory, default current")
    parser.add_argument("--model", "-m", default="small", 
                        choices=["tiny", "base", "small", "medium", "large"], 
                        help="Whisper model, default small")
    parser.add_argument("--language", "-l", default="zh", help="Language: zh/en/auto, default zh")
    parser.add_argument("--keep-files", action="store_true", help="Keep intermediate files (wav)")
    
    args = parser.parse_args()
    
    # Determine video ID
    video_id = args.video_id
    if not video_id and args.url:
        resolved_url = resolve_short_url(args.url)
        video_id = extract_video_id(resolved_url)
    if not video_id:
        video_id = extract_video_id(args.video_url) or "video"
    
    print(f"[INFO] Video ID: {video_id}")
    print(f"[INFO] Platform: {platform.system()}")
    
    # Create output directory
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # File paths
    video_path = os.path.join(output_dir, f"{video_id}.mp4")
    audio_path = os.path.join(output_dir, f"{video_id}.wav")
    
    try:
        # Download video
        download_video(args.video_url, video_path)
        
        # Extract audio
        extract_audio(video_path, audio_path)
        
        # Transcribe
        txt_path = transcribe(audio_path, output_dir, args.model, args.language)
        
        # Output result
        print("\n" + "=" * 60)
        print(f"✅ Transcription complete")
        print(f"   Text file: {txt_path}")
        print(f"   Video file: {video_path}")
        print("=" * 60)
        
        # Clean up intermediate files
        if not args.keep_files and os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"[INFO] Removed temp file: {audio_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
