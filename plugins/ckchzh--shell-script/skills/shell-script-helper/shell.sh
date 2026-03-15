#!/usr/bin/env bash
# Shell Script Helper — shell-script skill
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  generate) cat << 'PROMPT'
你是Shell脚本专家。根据描述生成完整可用的Bash脚本。要求：1.#!/usr/bin/env bash 2.set -euo pipefail 3.充分的注释 4.参数验证 5.错误处理 6.颜色输出。用中文注释。
需求描述：
PROMPT
    echo "$INPUT" ;;
  explain) cat << 'PROMPT'
你是Bash教学专家。逐行解释这个脚本：1.整体功能 2.每行/每块的作用 3.特殊语法说明 4.潜在问题 5.改进建议。用中文。
脚本内容：
PROMPT
    echo "$INPUT" ;;
  debug) cat << 'PROMPT'
你是Shell调试专家。诊断脚本问题：1.语法错误 2.逻辑bug 3.权限问题 4.路径问题 5.变量引用 6.调试方法(set -x/trap)。给出修复代码。用中文。
脚本/错误信息：
PROMPT
    echo "$INPUT" ;;
  template) cat << 'PROMPT'
你是运维专家。生成可直接使用的Shell脚本模板。类型：backup(备份)、monitor(监控)、deploy(部署)、cleanup(清理)、log-rotate(日志轮转)、health-check(健康检查)。包含：参数处理、日志记录、错误通知、cron配置说明。用中文注释。
模板类型：
PROMPT
    echo "$INPUT" ;;
  oneliner) cat << 'PROMPT'
你是命令行大师。生成一行命令(one-liner)解决问题。给出：1.命令本身 2.拆解解释 3.常用变体 4.注意事项。用中文。
需求：
PROMPT
    echo "$INPUT" ;;
  cheatsheet) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🐚 Bash 速查表
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  变量    $VAR  ${VAR:-default}  ${#VAR}
  数组    arr=(a b c)  ${arr[0]}  ${#arr[@]}
  条件    if [ -f file ]; then ... fi
  循环    for i in {1..10}; do ... done
          while read line; do ... done < file
  函数    func() { local var=$1; echo $var; }
  管道    cmd1 | cmd2 | cmd3
  重定向  > 覆盖  >> 追加  2>&1 合并  < 输入
  测试    -f 文件  -d 目录  -z 空串  -n 非空
  算术    $((a+b))  $((a>b?a:b))
  替换    ${var/old/new}  ${var%suffix}
  特殊    $? 返回码  $$ PID  $# 参数数  $@ 全部参数

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🐚 Shell Script Helper — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  generate [描述]    生成Shell脚本
  explain [脚本]     逐行解释
  debug [脚本]       调试排错
  template [类型]    模板(backup/monitor/deploy)
  oneliner [描述]    一行命令
  cheatsheet        Bash速查表

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
