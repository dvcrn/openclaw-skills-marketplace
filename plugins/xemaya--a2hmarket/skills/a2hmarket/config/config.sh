#!/usr/bin/env bash
# a2hmarket 公共配置文件
# 本文件由 a2hmarket-install.sh 自动生成，也可手动修改

# ========== 必填项 ==========
export BASE_URL="http://api.a2hmarket.ai"
export AGENT_ID="REPLACE_WITH_YOUR_AGENT_ID"    # 由安装脚本自动填入或者手动填入
export AGENT_SECRET="REPLACE_WITH_YOUR_SECRET"  # 由安装脚本自动填入或者手动填入

# ========== 说明 ==========
# runtime 专用配置（OpenClaw、MQTT、推送等）已内置在 runtime/js/src/config/loader.js
# 如需覆盖默认值，可通过环境变量或在此文件中导出相应变量
# 详见：a2hmarket/references/listener-config.md
#
# 常用可覆盖项：
#   A2HMARKET_LISTENER_LOG_FILE  - 日志文件路径，默认 runtime/logs/listener.log
#   A2HMARKET_LISTENER_PID_FILE  - PID 文件路径，默认 runtime/store/listener.pid
#   A2HMARKET_DB_PATH            - 数据库路径，默认 runtime/store/a2hmarket_listener.db
