#!/bin/bash

# Nero Market Research - 打包脚本

VERSION="4.0.0"
PACKAGE_NAME="nero-market-research-v${VERSION}"

echo "📦 打包 Nero Market Research v${VERSION}..."

# 创建临时目录
mkdir -p /tmp/${PACKAGE_NAME}

# 复制文件
cp -r nero-market-research/* /tmp/${PACKAGE_NAME}/

# 删除不必要的文件
rm -rf /tmp/${PACKAGE_NAME}/.git
rm -rf /tmp/${PACKAGE_NAME}/__pycache__
rm -f /tmp/${PACKAGE_NAME}/config.json

# 设置权限
chmod +x /tmp/${PACKAGE_NAME}/install.sh
chmod +x /tmp/${PACKAGE_NAME}/uninstall.sh

# 打包
cd /tmp
tar -czf ${PACKAGE_NAME}.tar.gz ${PACKAGE_NAME}

# 移动到工作目录
mv ${PACKAGE_NAME}.tar.gz /root/.openclaw/workspace-work/

# 清理
rm -rf /tmp/${PACKAGE_NAME}

echo "✅ 打包完成: ${PACKAGE_NAME}.tar.gz"
echo "文件大小: $(du -h /root/.openclaw/workspace-work/${PACKAGE_NAME}.tar.gz | cut -f1)"
