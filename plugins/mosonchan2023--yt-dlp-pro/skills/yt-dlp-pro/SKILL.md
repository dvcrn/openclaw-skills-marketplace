---
name: yt-dlp-pro
description: "YouTube video search, download, subtitles & audio extraction. 40 Stars! Full yt-dlp wrapper. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/joeseesun/yt-search-download
---

# YouTube Downloader Pro (yt-dlp)

## 功能

YouTube video search, download & subtitle extraction based on **yt-dlp** (40 Stars on GitHub).

### 核心功能

- **Video Search**: Search by keyword, channel, sort by date/views
- **Video Download**: Support 4K, 1080p, various formats
- **Audio Extract**: Download as MP3
- **Subtitle Download**: SRT (with timestamps) + TXT (for AI)
- **Chinese Translation**: Auto-translate English titles to Chinese
- **Channel Browse**: Browse channel latest videos
- **Playlist Support**: Download entire playlists

## 使用方法

```json
{
  "action": "search",
  "query": "Python tutorial",
  "limit": 10
}
```

### Actions

| Action | Description |
|--------|-------------|
| search | Search videos by keyword |
| download | Download video from URL |
| audio | Extract audio as MP3 |
| subtitles | Download subtitles (SRT+TXT) |
| playlist | Download entire playlist |

## 输出示例

```json
{
  "success": true,
  "action": "search",
  "results": [
    {
      "title": "Python Tutorial 2024",
      "views": "741K",
      "duration": "4h25m",
      "url": "https://youtube.com/watch?v=..."
    }
  ]
}
```

## 价格

每次调用: **0.001 USDT**

## 安装前置

- YouTube API Key (from Google Cloud Console)
- yt-dlp: `pip install yt-dlp`
- ffmpeg: for audio extraction

## Use Cases

- **学习下载**: 下载课程视频离线观看
- **音频提取**: 将教程视频转MP3，通勤听
- **字幕获取**: 提取字幕用于学习或AI处理
- **内容备份**: 备份YouTube内容
- **频道采集**: 批量下载整个频道视频
