#!/usr/bin/env python3
"""
Video utility functions - pure Python implementation, no external dependencies
Supports extracting video duration (milliseconds) from MP4 files
"""

import struct
import os
from pathlib import Path


def get_mp4_duration_ms(file_path: str) -> int | None:
    """
    Extract video duration (milliseconds) from an MP4 file
    Parses the moov/mvhd atom of the MP4 container to get duration and timescale

    Returns: duration in milliseconds, None if parsing fails
    """
    try:
        with open(file_path, "rb") as f:
            file_size = os.path.getsize(file_path)
            return _find_mvhd_duration(f, 0, file_size)
    except (IOError, struct.error):
        return None


def _find_mvhd_duration(f, start: int, end: int) -> int | None:
    """Search for mvhd atom in [start, end) range"""
    pos = start
    while pos < end:
        f.seek(pos)
        header = f.read(8)
        if len(header) < 8:
            break

        size, atom_type = struct.unpack(">I4s", header)
        atom_type = atom_type.decode("ascii", errors="ignore")

        # Handle extended size
        if size == 1:
            ext = f.read(8)
            if len(ext) < 8:
                break
            size = struct.unpack(">Q", ext)[0]

        if size == 0:
            size = end - pos

        if size < 8:
            break

        atom_end = pos + size
        header_size = 8 if size != 1 else 16

        if atom_type == "moov":
            # Enter moov container, search child atoms
            return _find_mvhd_duration(f, pos + header_size, atom_end)

        if atom_type == "mvhd":
            # Found mvhd, parse duration and timescale
            f.seek(pos + header_size)
            data = f.read(min(size - header_size, 120))
            if len(data) < 4:
                return None

            version = data[0]
            if version == 0:
                # version 0: 4 bytes each
                if len(data) < 20:
                    return None
                timescale = struct.unpack(">I", data[12:16])[0]
                duration = struct.unpack(">I", data[16:20])[0]
            elif version == 1:
                # version 1: 8 bytes each
                if len(data) < 28:
                    return None
                timescale = struct.unpack(">I", data[20:24])[0]
                duration = struct.unpack(">Q", data[24:32])[0]
            else:
                return None

            if timescale == 0:
                return None

            return int(duration * 1000 / timescale)

        pos = atom_end

    return None


def is_video_file(file_path: str) -> bool:
    """Check if file is a video file (based on extension)"""
    ext = Path(file_path).suffix.lower()
    return ext in (".mp4", ".mov", ".avi", ".webm", ".mkv")


def get_video_suffix(url: str) -> str | None:
    """Extract video suffix from URL"""
    url_lower = url.lower()
    for ext in (".mp4", ".mov", ".webm", ".avi"):
        if ext in url_lower:
            return ext
    return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 video_utils.py <video_file>")
        sys.exit(1)

    path = sys.argv[1]
    duration = get_mp4_duration_ms(path)
    if duration is not None:
        print(f"Duration: {duration} ms ({duration / 1000:.1f} s)")
    else:
        print("Failed to extract duration")
        sys.exit(1)
