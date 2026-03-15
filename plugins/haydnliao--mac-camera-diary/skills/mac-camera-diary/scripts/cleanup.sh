#!/usr/bin/env bash
# cleanup.sh - 根据 KEEP_PHOTOS_DAYS 清理过期照片（保留日志文件）
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# 计算清理目标日期
if [ "$KEEP_PHOTOS_DAYS" -eq 0 ]; then
  # 默认：删除昨天
  TARGET=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)
  DIRS=("${DIARY_DIR}/$TARGET")
else
  # 删除 N 天前及更早的所有日期目录
  CUTOFF=$(date -v-${KEEP_PHOTOS_DAYS}d +%Y-%m-%d 2>/dev/null || date -d "${KEEP_PHOTOS_DAYS} days ago" +%Y-%m-%d)
  # 找出所有日期目录中早于 cutoff 的
  mapfile -t DIRS < <(find "${DIARY_DIR}" -maxdepth 1 -type d -name "????-??-??" | while read -r d; do
    dname=$(basename "$d")
    [ "$dname" \< "$CUTOFF" ] && echo "$d"
  done | sort)
fi

if [ "${#DIRS[@]}" -eq 0 ]; then
  echo "[INFO] 没有需要清理的目录。"
  exit 0
fi

for DIR in "${DIRS[@]}"; do
  if [ -d "$DIR" ]; then
    find "$DIR" -name "*.jpg" -delete
    echo "🗑️ 已清理 $DIR 中的照片"
  fi
done
