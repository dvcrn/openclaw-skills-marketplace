#!/bin/bash
# 发布 company-research skill 到 ClawHub
# 用法: bash publish.sh

clawhub publish "$(dirname "$0")" \
  --slug company-research \
  --name "企业背景调查" \
  --version 1.0.0 \
  --changelog "面向电信客户经理的企业背景调查工具，基于agent-browser搜索百度提取企业工商数据，自动生成企业概况、近期动态和商机雷达报告"
