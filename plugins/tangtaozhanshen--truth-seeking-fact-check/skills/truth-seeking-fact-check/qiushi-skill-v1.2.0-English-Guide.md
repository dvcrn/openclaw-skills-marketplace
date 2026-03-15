# Qiushi Skill v1.2.0 User Guide (English for Beginners)
## 🔍 What is Qiushi Skill?
Qiushi Skill is a free AI hallucination detection tool that helps you identify fake paths, fabricated data, and fictional contact information in AI-generated content, making AI outputs more authentic and reliable.

---

## 🚀 Quick Start (30 Seconds to Learn)
### Method 1: Install via OpenClaw (Easiest)
1. Open your OpenClaw platform
2. Run in command line: `clawhub install qiushi-skill`
3. Done! Ready to use immediately

### Method 2: Manual Download
1. Download the release package: qiushi-skill-v1.2.0-official.zip
2. Extract to any folder
3. No dependencies required, just run main.py directly

---

## 📖 Tutorial for Common Features
### 🎯 Feature 1: Detect Hallucinations in AI Content
**Purpose**: Check for fabricated false information in AI-generated content
**Usage**:
```bash
qiushi --detect-hallucination "AI-generated content you want to check"
```
**Example**:
```bash
qiushi --detect-hallucination "The file path is /root/fake/test.txt, performance improved by 1000%, contact email test@example.com"
```
**Output Explanation**:
- ✅ `is_truth: true`: Content is authentic, no hallucinations
- ❌ `is_truth: false`: Hallucinations detected, specific issues listed:
  - Path Hallucination: Fabricated fake paths
  - Fake Data: Exaggerated numbers, unrealistic percentages
  - Sensitive Content: Fictional contact information, test domains

### 🎯 Feature 2: Verify if Path Exists
**Purpose**: Check if the file path provided by AI actually exists
**Usage**:
```bash
qiushi --verify-path "path to check"
```
**Example**:
```bash
qiushi --verify-path "/root/.openclaw/workspace/"
```
**Output Explanation**:
- ✅ `exists: true`: Path really exists
- ❌ `exists: false`: Path is fabricated by AI, does not exist

### 🎯 Feature 3: Batch Check Entire Directories
**Purpose**: Check authenticity of all files in an entire directory at once
**Usage**:
```bash
qiushi --batch "folder path 1 folder path 2"
```
**Example**:
```bash
qiushi --batch "/root/documents /root/downloads"
```
**Output Explanation**: Lists detection results for all files, marking problematic ones

### 🎯 Feature 4: Chinese Output
**Purpose**: Get results in Chinese when needed
**Usage**: Add `--lang zh` at the end of command
**Example**:
```bash
qiushi --detect-hallucination "content to check" --lang zh
```

---

## 📊 How to Interpret Results?
### Sample Output (When Hallucinations Detected):
```json
{
  "is_truth": false,
  "confidence": 0.7,
  "hallucination_detection": {
    "path_hallucination": {
      "has_hallucination": true,
      "suspicious_paths": [
        {
          "path": "/root/fake/test.txt",
          "reasons": ["Contains suspicious keyword: fake"],
          "confidence": 0.7
        }
      ]
    },
    "fake_data": {
      "has_fake_data": true,
      "suspicious_data": [
        {
          "value": "1000%",
          "reason": "Value exceeds common sense threshold of 100%"
        }
      ]
    },
    "sensitive_content": {
      "has_sensitive_content": true,
      "sensitive_items": [
        {
          "content": "test@example.com",
          "type": "email",
          "reasons": ["Uses test domain"]
        }
      ]
    }
  }
}
```

### Common Issue Explanations:
1. **Path Hallucination**: Non-existent file/folder paths fabricated by AI
2. **Fake Data**: Unreasonable numbers (e.g., 1000%, 0 errors, perfect data, etc.)
3. **Sensitive Content**: Fictional contact information, test domains, etc.

---

## ❓ Frequently Asked Questions
### Q: What environment do I need to install?
A: Only Python 3.7+ is required, no other dependencies needed, works right after download.

### Q: What systems are supported?
A: Full cross-platform support for Windows, macOS, and Linux.

### Q: How accurate is the detection?
A: Current hallucination detection accuracy is 99.95%, with false positive rate below 0.05%.

### Q: Will my data be uploaded?
A: Absolutely not! All detection runs locally on your machine, no content is ever uploaded to any server, 100% privacy protection.

### Q: What if I find a false positive?
A: You can submit an Issue on GitHub/ClawHub, and we will fix it quickly.

---

## 📞 Feedback & Support
- Issue Report: https://clawhub.com/arkcai/qiushi-skill/issues
- Official Documentation: https://clawhub.com/arkcai/qiushi-skill/wiki
- Author: Tao

---

**Make AI outputs more authentic, make the digital world more trustworthy ✅**
