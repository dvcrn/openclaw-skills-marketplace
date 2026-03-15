require('dotenv').config();
const express = require('express');
const FeishuService = require('./feishuService');
const dbStore = require('./dbStore');

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

const feishu = new FeishuService(
  process.env.FEISHU_APP_ID,
  process.env.FEISHU_APP_SECRET
);

/**
 * =========================================================
 * 供 OpenClaw Agent 调用的三组原子化 Skill 接口
 * =========================================================
 */

/**
 * 技能一：日历排期计算器
 * Agent 提取出人名单和期望时间段后，调用此接口索要 3 个左右空闲时间解
 */
app.post('/api/claw/calc-free-time', async (req, res) => {
  const { userIds, startTimeIso, endTimeIso, durationMinutes } = req.body;

  if (!userIds || !startTimeIso || !endTimeIso || !durationMinutes) {
    return res.status(400).json({ error: '缺少 userIds / startTimeIso / endTimeIso / durationMinutes' });
  }

  try {
    const timeOptions = await feishu.getCommonFreeTime(userIds, startTimeIso, endTimeIso, durationMinutes);
    res.json({
      success: true,
      message: timeOptions.length > 0 ? '找到了以下空闲时段' : '在给定时间内所有人无符合要求的共同空闲时段',
      data: { options: timeOptions }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * 技能二：状态发包与意向收集单
 * Agent 利用第一步的结果自己生成了拟人化的话术，再调用此接口下发确认卡片，并开启一个 Session 挂起任务
 */
app.post('/api/claw/dispatch-cards', async (req, res) => {
  const { meetingTopic, userIds, timeSlots, agentMessage } = req.body;

  if (!meetingTopic || !userIds || !timeSlots || !agentMessage) {
    return res.status(400).json({ error: '参数缺失' });
  }

  try {
    // 1. 生成唯一事务 ID
    const sessionId = 'ses_' + Date.now() + '_' + Math.floor(Math.random() * 1000);

    // 2. 本地（持久化）存储事务状态
    dbStore.createSession(sessionId, {
      meetingTopic,
      userIds,
      timeSlots,
      agentMessage
    });

    // 3. 将包含 session_id 的独立带按钮卡片派给这几个人
    await feishu.sendPollCards(userIds, sessionId, meetingTopic, agentMessage, timeSlots);

    res.json({
      success: true,
      message: `已向 ${userIds.length} 人的飞书发送了排期卡片。此任务已建档挂起等待用户响应。`,
      data: { sessionId }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * =========================================================
 * 飞书卡片 Webhook，用于接管用户点击与后续决策
 * =========================================================
 */
app.post('/api/feishu/card-webhook', async (req, res) => {
  if (req.body.type === 'url_verification') {
    return res.json({ challenge: req.body.challenge });
  }

  const actionObj = req.body.action;
  
  // 处理投递按钮点击逻辑
  if (actionObj && actionObj.value && actionObj.value.action === 'vote') {
    const { session_id, choice } = actionObj.value;
    const operatorId = req.body.open_id;

    console.log(`[Webhook] Session ${session_id} - User ${operatorId} clicked: ${choice}`);

    // 1. 更新此人的意向
    dbStore.updateParticipantState(session_id, operatorId, choice);

    // 2. 检查会话当前的共识状态
    const status = dbStore.checkSessionConsensus(session_id);

    // 回复给点击用户的局部视图 Toast 提示
    let toastMsg = '收到意向！请等待其他人反馈~';

    if (status.done) {
      if (status.result === 'agreed') {
        // ========== 技能三/四内部触发：全员同意，执行最终定档 ==========
        toastMsg = '你是最后一个确认者！全员意见统一，我正在执行系统排期...';
        
        const agreedSlot = JSON.parse(status.time);
        const sessionStore = dbStore.getSession(session_id);
        
        // （异步调用飞书 API 创会，并用机器人提醒大家）
        feishu.createMeeting(
          sessionStore.userIds, 
          sessionStore.meetingTopic, 
          agreedSlot.start_time, 
          agreedSlot.end_time
        );
        
      } else if (status.result === 'conflict') {
        // ========== 重大难点突破：如果时间相冲，怎么把它抛回给 Agent ==========
        toastMsg = '由于存在冲突或都有人没空，排期进程暂停。助手已记录！';

        /**
         * 真实落地的复杂架构中，这里应该反向调起大模型的 HTTP 接口 / 唤醒 Agent 流。
         * 伪代码：
         * openclawAgent.wakeUp({
         *   sessionId: session_id,
         *   prompt: '你的排期任务大家时间无法协调。这是目前收集的状态：... 请你分析并生成安抚用户或重试其它时间的策略并发信。'
         * });
         */
        console.log(`[ALERT] 系统状态机：会话 ${session_id} 发生排期冲突！需唤醒 LLM 决策下一条出路！`);
      }
    }

    // 给飞书立刻回包，让那根卡片的小按钮变成已响应状态
    return res.json({ toast: { type: 'success', content: toastMsg } });
  }

  res.status(200).send('ok');
});

app.listen(port, () => {
  console.log(`[OpenClaw Agent] 排期原子服务启动, 监听端口: ${port}`);
});
