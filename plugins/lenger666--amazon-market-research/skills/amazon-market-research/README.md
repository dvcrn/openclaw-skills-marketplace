# Amazon Market Research

Amazon Market Research 用于快速生成 Amazon 市场调研报告。

输出结果分三层：

1. 飞书可读摘要
2. 完整 18 条 SOP 调研报告
3. 本地 PDF 文件

首次安装或更新 Skill 后，请先执行：

openclaw gateway restart

然后检查是否识别成功：

openclaw skills list | grep amazon

如果看到：

amazon_market_research

说明 Skill 已被 OpenClaw 正确识别。

推荐在飞书中使用 Slash 命令调用：

/amazon_market_research 调研一下午餐盒在美国Amazon市场值不值得做

本地测试：

bash ~/.openclaw/workspace/skills/amazon_market_research/run.sh "调研一下午餐盒在美国Amazon市场值不值得做"