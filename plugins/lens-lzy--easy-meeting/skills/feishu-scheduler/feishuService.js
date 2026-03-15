/**
 * 飞书 API 交互服务 - 完整进阶版
 * 用于 OpenClaw Skill 中的日历排期、多人交互式卡片分发、日程创建等能力
 */

const logger = {
  info: (ctx, msg) => console.log(`[INFO]`, JSON.stringify({ ...ctx, msg })),
  error: (ctx, msg) => console.error(`[ERR]`, JSON.stringify({ ...ctx, msg }))
};

class FeishuService {
  constructor(appId, appSecret) {
    this.appId = appId;
    this.appSecret = appSecret;
    this.tenantAccessToken = null;
    this.tokenExpireAt = 0;
  }

  async getTenantAccessToken() {
    const now = Date.now();
    if (this.tenantAccessToken && now < this.tokenExpireAt - 5 * 60 * 1000) return this.tenantAccessToken;

    const url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal';
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json; charset=utf-8' },
      body: JSON.stringify({ app_id: this.appId, app_secret: this.appSecret })
    });
    const data = await response.json();
    if (data.code !== 0) throw new Error(`Fetch token error [${data.code}]`);
    this.tenantAccessToken = data.tenant_access_token;
    this.tokenExpireAt = now + data.expire * 1000;
    return this.tenantAccessToken;
  }

  async _request(method, url, options = {}) {
    const token = await this.getTenantAccessToken();
    const response = await fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json; charset=utf-8',
        ...options.headers
      },
      body: options.body ? JSON.stringify(options.body) : undefined
    });
    const data = await response.json();
    if (data.code !== 0) throw new Error(`API Error [${data.code}]: ${data.msg}`);
    return data.data;
  }

  /**
   * 能力1：计算一组用户的闲暇聚合时间块
   */
  async getCommonFreeTime(userIds, startTimeIso, endTimeIso, durationMinutes = 30) {
    const startTs = new Date(startTimeIso).getTime();
    const endTs = new Date(endTimeIso).getTime();
    const busyIntervals = [];

    for (const userId of userIds) {
      const url = 'https://open.feishu.cn/open-apis/calendar/v4/freebusy/list?user_id_type=user_id';
      const data = await this._request('POST', url, {
        body: { time_min: startTimeIso, time_max: endTimeIso, user_id: userId }
      });
      const list = data.freebusy_list || [];
      for (const item of list) {
        busyIntervals.push([new Date(item.start_time).getTime(), new Date(item.end_time).getTime()]);
      }
    }

    busyIntervals.sort((a, b) => a[0] - b[0]);
    const mergedBusy = [];
    if (busyIntervals.length > 0) {
      mergedBusy.push([...busyIntervals[0]]);
      for (let i = 1; i < busyIntervals.length; i++) {
        const current = busyIntervals[i];
        const last = mergedBusy[mergedBusy.length - 1];
        if (current[0] <= last[1]) last[1] = Math.max(last[1], current[1]);
        else mergedBusy.push([...current]);
      }
    }

    const freeIntervals = [];
    let currentStart = startTs;
    for (const busy of mergedBusy) {
      if (busy[0] > currentStart && (busy[0] - currentStart) >= durationMinutes * 60000) {
        freeIntervals.push([currentStart, busy[0]]);
      }
      currentStart = Math.max(currentStart, busy[1]);
    }
    if (endTs > currentStart && (endTs - currentStart) >= durationMinutes * 60000) {
      freeIntervals.push([currentStart, endTs]);
    }

    // 将连续的长空闲块依照 durationMinutes 切分成合理的可选时间段（供参考）
    const timeOptions = [];
    for (const slot of freeIntervals) {
      let tStart = slot[0];
      while (tStart + durationMinutes * 60000 <= slot[1] && timeOptions.length < 5) { // 最多取近 5 个解
        const tEnd = tStart + durationMinutes * 60000;
        timeOptions.push({
          start_time: new Date(tStart).toISOString(),
          end_time: new Date(tEnd).toISOString()
        });
        tStart += durationMinutes * 60000;
      }
    }
    return timeOptions;
  }

  /**
   * 能力2：分发意向收集卡片给所有参与人
   */
  async sendPollCards(userIds, sessionId, meetingTopic, agentMessage, timeSlots) {
    // 构造带回调 session 的动作按钮
    const actions = timeSlots.map((ts, i) => {
      // 转化为中文本地时区以显示
      const text = `${new Date(ts.start_time).toLocaleDateString('zh-CN')} ${new Date(ts.start_time).toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit'})} - ${new Date(ts.end_time).toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit'})}`;
      return {
        tag: 'button',
        text: { tag: 'plain_text', content: text },
        type: i === 0 ? 'primary' : 'default',
        value: { action: 'vote', session_id: sessionId, choice: JSON.stringify(ts) } // choice 带有完整开始借宿时间
      };
    });

    // 永远补充一个都没空的按钮，让用户能走退路交由 LLM 洗牌
    actions.push({
      tag: 'button',
      text: { tag: 'plain_text', content: '以上时间均冲突' },
      type: 'danger',
      value: { action: 'vote', session_id: sessionId, choice: 'none' }
    });

    const cardContent = {
      config: { wide_screen_mode: true },
      header: { template: 'blue', title: { tag: 'plain_text', content: `📅 会议排期邀请：${meetingTopic}` } },
      elements: [
        { tag: 'markdown', content: `你好～我是智能排期助手，${agentMessage}` },
        { tag: 'action', actions: actions }
      ]
    };

    const payloadStr = JSON.stringify(cardContent);
    // 给诸位私聊派发卡片
    for (const uid of userIds) {
      try {
        await this._request('POST', 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=user_id', {
          body: { receive_id: uid, msg_type: 'interactive', content: payloadStr }
        });
        logger.info({ uid, sessionId }, 'Poll card dispatched');
      } catch (err) {
        logger.error({ uid, err: err.message }, 'Failed sending card');
      }
    }
  }

  /**
   * 能力4：创建日程
   */
  async createMeeting(userIds, meetingTopic, startTime, endTime) {
    // 调用日历 V4 的 create event 接口
    const eventBody = {
      summary: meetingTopic,
      start_time: { timestamp: String(Math.floor(new Date(startTime).getTime()/1000)) },
      end_time: { timestamp: String(Math.floor(new Date(endTime).getTime()/1000)) },
      attendee_ability: 'none',
      need_notification: true
    };
    
    try {
      // 先向应用主日历或公共日历建会，暂使用应用的 Primary 日历
      // 真实环境中最好用用户授权或建立独立的代理日历集
      const calRes = await this._request('POST', 'https://open.feishu.cn/open-apis/calendar/v4/calendars/feishu.cn_0000/events', {
        body: eventBody
      });
      // (伪代码：实际要传真实 application calendar_id，假设成功)
      logger.info({ meetingTopic }, 'Calendar event mocked creation.');
      
      // 为参会者发确认信
      for (const uid of userIds) {
         await this._request('POST', 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=user_id', {
          body: {
            receive_id: uid, msg_type: 'text',
            content: JSON.stringify({text: `✅ 您好，会议“${meetingTopic}”已于 ${new Date(startTime).toLocaleString()} 成功建会并锁定！`})
          }
        });
      }
      return true;
    } catch(err) {
      logger.error({ err: err.message }, 'Error creating calendar event');
      return false;
    }
  }
}

module.exports = FeishuService;
