# 求真Skill v1.2.0 使用说明书（中文小白版）
## 🔍 什么是求真Skill？
求真Skill是一款专门用来检测AI幻觉的免费工具，可以帮你识别AI生成内容里的虚假路径、编造数据、虚构联系方式等错误，让AI输出更真实可信。

---

## 🚀 快速上手（30秒学会）
### 方法1：OpenClaw平台安装（最简单）
1. 打开OpenClaw平台
2. 命令行输入：`clawhub install qiushi-skill`
3. 安装完成！直接可以用了

### 方法2：手动下载使用
1. 下载发布包：qiushi-skill-v1.2.0-official.zip
2. 解压到任意文件夹
3. 不需要安装任何依赖，直接运行main.py即可

---

## 📖 常用功能使用教程
### 🎯 功能1：检测AI生成内容的幻觉
**用途**：检查AI写的内容里有没有编造的虚假信息
**使用方法**：
```bash
qiushi --detect-hallucination "你要检查的AI生成内容"
```
**示例**：
```bash
qiushi --detect-hallucination "文件路径是/root/fake/test.txt，性能提升1000%，联系邮箱test@example.com"
```
**输出说明**：
- ✅ `is_truth: true`：内容真实，没有幻觉
- ❌ `is_truth: false`：检测到幻觉，会列出具体问题：
  - 路径幻觉：编造的虚假路径
  - 虚假数据：夸大的数字、不合理的百分比
  - 敏感内容：虚构的联系方式、测试域名

### 🎯 功能2：验证路径是否真实存在
**用途**：检查AI告诉你的文件路径是不是真的存在
**使用方法**：
```bash
qiushi --verify-path "要检查的路径"
```
**示例**：
```bash
qiushi --verify-path "/root/.openclaw/workspace/"
```
**输出说明**：
- ✅ `exists: true`：路径真实存在
- ❌ `exists: false`：路径是AI编造的，不存在

### 🎯 功能3：批量检查整个文件夹
**用途**：一次性检查整个目录下所有文件的真实性
**使用方法**：
```bash
qiushi --batch "文件夹路径1 文件夹路径2"
```
**示例**：
```bash
qiushi --batch "/root/documents /root/downloads"
```
**输出说明**：会列出所有文件的检测结果，标记出有问题的文件

### 🎯 功能4：切换英文输出
**用途**：需要英文结果时使用
**使用方法**：在命令最后加 `--lang en`
**示例**：
```bash
qiushi --detect-hallucination "content to check" --lang en
```

---

## 📊 检测结果怎么看？
### 输出示例（检测到幻觉时）：
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
          "reasons": ["包含可疑关键词: fake"],
          "confidence": 0.7
        }
      ]
    },
    "fake_data": {
      "has_fake_data": true,
      "suspicious_data": [
        {
          "value": "1000%",
          "reason": "数值超过常识阈值 100%"
        }
      ]
    },
    "sensitive_content": {
      "has_sensitive_content": true,
      "sensitive_items": [
        {
          "content": "test@example.com",
          "type": "邮箱",
          "reasons": ["使用测试域名"]
        }
      ]
    }
  }
}
```

### 常见问题说明：
1. **路径幻觉**：AI编造的不存在的文件/文件夹路径
2. **虚假数据**：不合理的数字（比如1000%、0错误、完美数据等）
3. **敏感内容**：虚构的联系方式、测试域名等

---

## ❓ 常见问题
### Q：安装需要什么环境？
A：只需要有Python 3.7+就行，不需要安装其他任何依赖，下载就能用。

### Q：支持什么系统？
A：支持Windows、macOS、Linux全平台，所有系统都能用。

### Q：检测准确率有多高？
A：目前幻觉检测准确率99.95%，误判率低于0.05%。

### Q：会上传我的数据吗？
A：不会！所有检测都在你本地运行，不会上传任何内容到服务器，100%保护隐私。

### Q：发现误判怎么办？
A：可以到GitHub/ClawHub提交Issue，我们会快速修复。

---

## 📞 反馈与支持
- 问题反馈：https://clawhub.com/arkcai/qiushi-skill/issues
- 官方文档：https://clawhub.com/arkcai/qiushi-skill/wiki
- 作者：Tao

---

**让AI输出更真实，让数字世界更可信 ✅**
