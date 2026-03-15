# Scale Test — 并发 / 幂等 / 负载 / 配置一致性

多实例部署、多用户并发场景下的测试。当用户说"并发测试""压测""幂等""scale test"时使用。

## 四类测试

### 1. 并发安全测试

验证多用户同时触发同一功能时，结果互不干扰。

```bash
# L6-01: 两个用户同时存记忆，互不可见
echo "━━━ L6-01: 并发记忆隔离 ━━━"

# 并行执行两个存储操作
(
  curl -s -X POST "$GATEWAY/api/memory_store" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"text":"user_a_secret","userId":"ou_aaa"}' > /tmp/store_a.json
) &
PID_A=$!

(
  curl -s -X POST "$GATEWAY/api/memory_store" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"text":"user_b_secret","userId":"ou_bbb"}' > /tmp/store_b.json
) &
PID_B=$!

wait $PID_A $PID_B

# 验证：A 搜不到 B 的记忆
result_a=$(curl -s "$GATEWAY/api/memory_recall?query=user_b_secret&userId=ou_aaa")
echo "$result_a" | grep -q "No relevant memories" \
  && log_pass "L6-01: 并发存储后用户隔离正确" \
  || log_fail "L6-01: 用户隔离失败" "$result_a"
```

```bash
# L6-02: 同一用户两条消息同时到达
echo "━━━ L6-02: 同时发消息不丢不重 ━━━"

msg1="消息1_$(date +%s)"
msg2="消息2_$(date +%s)"

# 并行发送
send_feishu_msg "$msg1" &
send_feishu_msg "$msg2" &
wait

sleep 5  # 等处理完

# 验证：两条都被处理，没有丢失也没有重复回复
replies=$(get_recent_replies 10)
count1=$(echo "$replies" | grep -c "$msg1" || true)
count2=$(echo "$replies" | grep -c "$msg2" || true)

[ "$count1" -eq 1 ] && [ "$count2" -eq 1 ] \
  && log_pass "L6-02: 并发消息处理正确 (各回复1次)" \
  || log_fail "L6-02: 消息处理异常" "msg1回复${count1}次, msg2回复${count2}次"
```

### TypeScript 版本

```typescript
describe('L6: concurrent memory isolation', () => {
  it('parallel stores from different users are isolated', async () => {
    // 并行存储
    await Promise.all([
      memoryStore({ text: 'secret_a', userId: 'user_a' }),
      memoryStore({ text: 'secret_b', userId: 'user_b' }),
    ]);

    // 验证隔离
    const recallA = await memoryRecall({ query: 'secret_b', userId: 'user_a' });
    expect(recallA.length).toBe(0);
  });
});
```

### 2. 幂等性测试

验证同一操作执行两次，结果符合预期。

```bash
# L6-03: 相同群入群通知不重复
echo "━━━ L6-03: 入群通知幂等 ━━━"

# 模拟 bot_added 事件连续触发两次（飞书重试场景）
bash scripts/onboard-group.sh oc_test_idem 2>/dev/null
result1=$?
bash scripts/onboard-group.sh oc_test_idem 2>/dev/null
result2=$?

# 第二次应该跳过（SKIP），不重复创建配置
config_count=$(ls workspace/ai-pm/data/group_personas/oc_test_idem* 2>/dev/null | wc -l)

[ "$config_count" -le 1 ] \
  && log_pass "L6-03: 重复入群不创建重复配置" \
  || log_fail "L6-03: 创建了 $config_count 份配置"

# Cleanup
rm -f workspace/ai-pm/data/group_personas/oc_test_idem*
```

```bash
# L6-04: memory_store 去重
echo "━━━ L6-04: 相同记忆不重复存储 ━━━"

store_result1=$(memory_store "我喜欢Python" "ou_test")
store_result2=$(memory_store "我喜欢Python" "ou_test")

echo "$store_result2" | grep -q "duplicate\|already exists" \
  && log_pass "L6-04: 重复记忆被去重" \
  || log_fail "L6-04: 重复记忆未去重" "$store_result2"
```

### 3. 负载测试

验证高负载下的响应时间和稳定性。

```bash
# L6-05: 10 个并发请求的响应时间
echo "━━━ L6-05: 10并发 memory_recall 响应时间 ━━━"

start_time=$(date +%s%N)

for i in $(seq 1 10); do
  (
    curl -s -o /dev/null -w "%{time_total}" \
      "$GATEWAY/api/memory_recall?query=test&userId=ou_load_$i" \
      > /tmp/load_time_$i.txt
  ) &
done
wait

end_time=$(date +%s%N)
total_ms=$(( (end_time - start_time) / 1000000 ))

# 收集各请求响应时间
max_time=0
for i in $(seq 1 10); do
  t=$(cat /tmp/load_time_$i.txt)
  t_ms=$(echo "$t * 1000" | bc | cut -d. -f1)
  [ "$t_ms" -gt "$max_time" ] && max_time=$t_ms
done

[ "$max_time" -lt 10000 ] \
  && log_pass "L6-05: 10并发最大响应 ${max_time}ms (< 10s)" \
  || log_fail "L6-05: 10并发最大响应 ${max_time}ms (> 10s)"

rm -f /tmp/load_time_*.txt
```

```bash
# L6-06: 持续 30 秒发请求，观察错误率
echo "━━━ L6-06: 30秒持续负载错误率 ━━━"

total=0
errors=0
end=$(($(date +%s) + 30))

while [ $(date +%s) -lt $end ]; do
  total=$((total + 1))
  status=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY/api/health" 2>/dev/null)
  [ "$status" != "200" ] && errors=$((errors + 1))
  sleep 0.5
done

error_rate=$(echo "scale=2; $errors * 100 / $total" | bc)

[ "$(echo "$error_rate < 5" | bc)" -eq 1 ] \
  && log_pass "L6-06: 30秒持续负载错误率 ${error_rate}% (< 5%)" \
  || log_fail "L6-06: 错误率 ${error_rate}% (≥ 5%)" "${errors}/${total} 请求失败"
```

### 4. 配置一致性测试（多实例）

验证多台服务器的配置是否同步。

```bash
# L6-07: 多实例 skills 一致性
echo "━━━ L6-07: 多实例 Skills 文件一致性 ━━━"

SERVERS=("user@server1" "user@server2" "user@server3")
reference_hash=$(find workspace/skills -name 'SKILL.md' -exec md5sum {} + | sort | md5sum | cut -d' ' -f1)

all_match=true
for server in "${SERVERS[@]}"; do
  remote_hash=$(ssh "$server" "find ~/.openclaw/workspace/skills -name 'SKILL.md' -exec md5sum {} + | sort | md5sum | cut -d' ' -f1" 2>/dev/null)
  if [ "$remote_hash" != "$reference_hash" ]; then
    all_match=false
    log_fail "L6-07: $server skills hash 不匹配" "本地=$reference_hash 远程=$remote_hash"
  fi
done

$all_match && log_pass "L6-07: 所有实例 Skills 一致"
```

```bash
# L6-08: 多实例 extensions 一致性
echo "━━━ L6-08: 多实例 Plugins 代码一致性 ━━━"

reference_hash=$(find workspace/.openclaw/extensions -name '*.ts' -exec md5sum {} + | sort | md5sum | cut -d' ' -f1)

all_match=true
for server in "${SERVERS[@]}"; do
  remote_hash=$(ssh "$server" "find ~/.openclaw/workspace/.openclaw/extensions -name '*.ts' -exec md5sum {} + | sort | md5sum | cut -d' ' -f1" 2>/dev/null)
  if [ "$remote_hash" != "$reference_hash" ]; then
    all_match=false
    log_fail "L6-08: $server plugins hash 不匹配"
  fi
done

$all_match && log_pass "L6-08: 所有实例 Plugins 一致"
```

```bash
# L6-09: 多实例 OpenClaw 版本一致
echo "━━━ L6-09: 多实例版本一致性 ━━━"

versions=()
for server in "${SERVERS[@]}"; do
  ver=$(ssh "$server" "openclaw --version 2>/dev/null")
  versions+=("$server:$ver")
done

# 检查所有版本是否相同
unique_versions=$(printf '%s\n' "${versions[@]}" | cut -d: -f2 | sort -u | wc -l)
[ "$unique_versions" -eq 1 ] \
  && log_pass "L6-09: 所有实例版本一致 ($(echo "${versions[0]}" | cut -d: -f2))" \
  || log_fail "L6-09: 版本不一致" "$(printf '%s\n' "${versions[@]}")"
```

## 何时运行

| 触发场景 | 运行哪些 |
|---------|---------|
| 每次 `update-all.sh config` 后 | L6-07、L6-08、L6-09（配置一致性） |
| 新增用户/群到实例后 | L6-01、L6-02（并发安全） |
| 版本升级后 | 全部 L6 |
| 用户报告"消息丢了"或"重复回复" | L6-02、L6-03（并发+幂等） |
| 性能劣化感知 | L6-05、L6-06（负载） |
