# Twitter Video Download Skill - Release Page Content

---

## 📌 Basic Information

**Skill Name:** Twitter Video Download
**Slug:** twitter-video-download
**Category:** Utility > Media Download
**Tags:** twitter, x, video, download, media, social-media
**License:** MIT

---

## 📝 Description

**One-line Description:**
One-click download Twitter/X videos and GIFs to local storage

**Detailed Introduction:**
A simple and easy-to-use OpenClaw Skill, implemented based on yt-dlp. Supports downloading videos and GIFs from Twitter/X posts, automatically saved as MP4 format. Simply send a video link, and the AI assistant can help you complete the download.

---

## ✨ Features

- ✅ Supports twitter.com and x.com links
- ✅ Supports video and GIF downloads (GIF converted to MP4)
- ✅ High-quality video download
- ✅ Custom save path and filename
- ✅ Supports proxy configuration
- ✅ Automatic cleanup of temporary files

---

## 🔧 Environment Requirements

**Required:**
- Python 3.8+
- yt-dlp (`pip install yt-dlp`)

**Optional:**
- Proxy (for accessing Twitter/X)

---

## 📖 Usage

**Method 1: Tell the AI**
> "Download this video: https://x.com/username/status/123456789"

**Method 2: Command Line**
```bash
node download.mjs "https://x.com/username/status/123456789" --output "D:\Videos"
```

---

## ⚙️ Configuration

```bash
# Set proxy (if needed)
setx PROXY_URL "http://your-proxy:port"
```

---

## 📊 Predicted Popularity

### ⭐ Expected Rating: 4.2/5

**Reasons for Popularity:**

1. **Wide Demand** - Twitter/X is a popular social platform, many people want to save videos
2. **Easy to Use** - Just send a link, no manual operation needed
3. **High Practicality** - Can be used to save tutorials, news, highlights
4. **China User Friendly** - Many domestic users need proxy to access Twitter, this skill considers this

**Potential Issues:**

1. ⚠️ Proxy Required - Domestic users must configure proxy to use
2. ⚠️ Depends on External Service - yt-dlp may need updates to handle Twitter API changes
3. ⚠️ Copyright Notice - Recommended for personal learning only, respect copyright

**Target Users:**
- Users who need to save Twitter videos
- Self-media operators (collecting materials)
- Social media researchers
- AI assistant enthusiasts

---

## 📦 Release Version

**Version:** 1.0.0
**Release Date:** 2026-03-11
**Author:** Lemonpek66 / Jack

---

## 🔗 Links

- GitHub: https://github.com/Lemonpek66/twitter-video-download
- Demo Video: (To be added)

---

*This content has been cleaned of personal information and proxy addresses, can be copied to ClawHub form before publishing*
