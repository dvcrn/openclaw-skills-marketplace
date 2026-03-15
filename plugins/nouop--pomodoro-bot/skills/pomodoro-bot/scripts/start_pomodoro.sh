#!/bin/bash
# pomodoro-bot: 启动番茄钟（25m工作 + 5m休息）
# 参数：--work-mins [int] --rest-mins [int] --user-id [string]

WORK_MINS=25
REST_MINS=5
USER_ID=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --work-mins)
      WORK_MINS="$2"
      shift 2
      ;;
    --rest-mins)
      REST_MINS="$2"
      shift 2
      ;;
    --user-id)
      USER_ID="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [ -z "$USER_ID" ]; then
  echo "Error: --user-id is required"
  exit 1
fi

# 1. 工作倒计时（25m）
WORK_NAME="pomodoro-work-${USER_ID}"
openclaw cron add \
  --name "$WORK_NAME" \
  --at "${WORK_MINS}m" \
  --session isolated \
  --message "🍅 工作时间结束！准备进入5分钟休息～" \
  --deliver \
  --channel qqbot \
  --to "$USER_ID" \
  --delete-after-run

# 2. 休息倒计时（5m）——在工作提醒触发后自动追加（通过消息中的 cron 命令实现）
# 这里我们用一个“延迟触发”的技巧：在工作提醒消息中嵌入休息任务创建命令
# 但为简化，先手动创建休息任务（实际可由工作提醒的 isolated session 触发）
REST_NAME="pomodoro-rest-${USER_ID}"
openclaw cron add \
  --name "$REST_NAME" \
  --at "$((WORK_MINS + REST_MINS))m" \
  --session isolated \
  --message "☕ 休息结束！下一个番茄钟随时开始～ 🐾" \
  --deliver \
  --channel qqbot \
  --to "$USER_ID" \
  --delete-after-run

echo "✅ 番茄钟已启动：${WORK_MINS}分钟工作 → ${REST_MINS}分钟休息"
echo "ID: $USER_ID | 任务名: $WORK_NAME, $REST_NAME"