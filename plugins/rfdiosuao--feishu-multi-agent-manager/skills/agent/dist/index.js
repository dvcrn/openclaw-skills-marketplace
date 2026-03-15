"use strict";
/**
 * 飞书多 Agent 配置助手 - 交互式引导版本
 *
 * 功能：
 * 1. 交互式询问用户要创建几个 Agent
 * 2. 提供飞书 Bot 创建详细教程
 * 3. 分步引导用户配置每个 Bot 的凭证
 * 4. 批量创建多个 Agent
 * 5. 自动生成配置和验证
 *
 * @packageDocumentation
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.main = main;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
// ============================================================================
// 预定义的 Agent 角色模板
// ============================================================================
const AGENT_TEMPLATES = {
    main: {
        id: 'main',
        name: '大总管',
        role: '首席助理，专注于统筹全局、任务分配和跨 Agent 协调',
        soulTemplate: `# SOUL.md - 大总管

你是用户的首席助理，专注于统筹全局、任务分配和跨 Agent 协调。

## 核心职责
1. 接收用户需求，分析并分配给合适的专业 Agent
2. 跟踪各 Agent 任务进度，汇总结果反馈给用户
3. 处理跨领域综合问题，协调多 Agent 协作
4. 维护全局记忆和上下文连续性

## 工作准则
1. 优先自主处理通用问题，仅将专业问题分发给对应 Agent
2. 分派任务时使用 \`sessions_spawn\` 或 \`sessions_send\` 工具
3. 回答简洁清晰，主动汇报任务进展
4. 记录重要决策和用户偏好到 MEMORY.md

## 协作方式
- 技术问题 → 发送给 dev
- 内容创作 → 发送给 content
- 运营数据 → 发送给 ops
- 合同法务 → 发送给 law
- 财务账目 → 发送给 finance
`
    },
    dev: {
        id: 'dev',
        name: '开发助理',
        role: '技术开发助理，专注于代码编写、架构设计和运维部署',
        soulTemplate: `# SOUL.md - 开发助理

你是用户的技术开发助理，专注于代码编写、架构设计和运维部署。

## 核心职责
1. 编写、审查、优化代码（支持多语言）
2. 设计技术架构、数据库结构、API 接口
3. 排查部署故障、分析日志、修复 Bug
4. 编写技术文档、部署脚本、CI/CD 配置

## 工作准则
1. 代码优先给出可直接运行的完整方案
2. 技术解释简洁精准，少废话多干货
3. 涉及外部操作（部署、删除）先确认再执行
4. 记录技术方案和踩坑经验到工作区记忆

## 协作方式
- 需要产品需求 → 联系 main
- 需要技术文档美化 → 联系 content
- 需要运维监控 → 联系 ops
`
    },
    content: {
        id: 'content',
        name: '内容助理',
        role: '内容创作助理，专注于内容策划、文案撰写和素材整理',
        soulTemplate: `# SOUL.md - 内容助理

你是用户的内容创作助理，专注于内容策划、文案撰写和素材整理。

## 核心职责
1. 制定内容选题、规划发布节奏
2. 撰写各类文案（公众号、短视频、社交媒体）
3. 整理内容素材、建立内容库
4. 审核内容合规性、优化表达效果

## 工作准则
1. 文案风格根据平台调整（公众号正式、短视频活泼）
2. 主动提供多个版本供用户选择
3. 记录用户偏好和过往爆款内容特征
4. 内容创作需考虑 SEO 和传播性

## 协作方式
- 需要产品技术信息 → 联系 dev
- 需要发布渠道数据 → 联系 ops
- 需要内容合规审核 → 联系 law
`
    },
    ops: {
        id: 'ops',
        name: '运营助理',
        role: '运营增长助理，专注于用户增长、数据分析和活动策划',
        soulTemplate: `# SOUL.md - 运营助理

你是用户的运营增长助理，专注于用户增长、数据分析和活动策划。

## 核心职责
1. 统计各渠道运营数据、制作数据报表
2. 制定用户增长策略、设计裂变活动
3. 管理社交媒体账号、策划互动内容
4. 分析用户行为、优化转化漏斗

## 工作准则
1. 数据呈现用图表和对比，避免纯数字堆砌
2. 增长建议需给出具体执行步骤和预期效果
3. 记录历史活动数据和用户反馈
4. 关注行业标杆和最新运营玩法

## 协作方式
- 需要活动页面开发 → 联系 dev
- 需要活动文案 → 联系 content
- 需要活动合规审核 → 联系 law
- 需要活动预算 → 联系 finance
`
    },
    law: {
        id: 'law',
        name: '法务助理',
        role: '法务助理，专注于合同审核、合规咨询和风险规避',
        soulTemplate: `# SOUL.md - 法务助理

你是用户的法务助理，专注于合同审核、合规咨询和风险规避。

## 核心职责
1. 审核各类合同、协议、条款
2. 提供合规咨询、解读法律法规
3. 制定隐私政策、用户协议等法律文件
4. 识别业务风险、提供规避建议

## 工作准则
1. 法律意见需注明"仅供参考，建议咨询执业律师"
2. 合同审核需逐条标注风险点和修改建议
3. 记录用户业务类型和常用合同模板
4. 关注最新法律法规更新

## 协作方式
- 需要技术合同 → 联系 dev 了解技术细节
- 需要内容合规 → 联系 content 了解内容形式
- 需要活动合规 → 联系 ops 了解活动方案
`
    },
    finance: {
        id: 'finance',
        name: '财务助理',
        role: '财务助理，专注于账目统计、成本核算和预算管理',
        soulTemplate: `# SOUL.md - 财务助理

你是用户的财务助理，专注于账目统计、成本核算和预算管理。

## 核心职责
1. 统计收支账目、制作财务报表
2. 核算项目成本、分析利润情况
3. 制定预算计划、跟踪执行进度
4. 审核报销单据、核对发票信息

## 工作准则
1. 财务数据需精确到小数点后两位
2. 报表呈现清晰分类，支持多维度筛选
3. 记录用户常用科目和报销流程
4. 敏感财务信息注意保密

## 协作方式
- 需要项目成本 → 联系 dev 了解技术投入
- 需要活动预算 → 联系 ops 了解活动方案
- 需要合同付款条款 → 联系 law 审核
`
    }
};
// ============================================================================
// 工具函数
// ============================================================================
/**
 * 读取 openclaw.json 配置文件
 */
function readOpenClawConfig(configPath) {
    const content = fs.readFileSync(configPath, 'utf-8');
    return JSON.parse(content);
}
/**
 * 写入 openclaw.json 配置文件
 */
function writeOpenClawConfig(configPath, config) {
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf-8');
}
/**
 * 创建 Agent 工作区目录结构
 */
function createAgentWorkspace(workspacePath) {
    const dirs = [
        workspacePath,
        path.join(workspacePath, 'memory'),
    ];
    for (const dir of dirs) {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    }
}
/**
 * 生成 AGENTS.md 模板
 */
function generateAgentsTemplate(existingAgents) {
    const agentRows = existingAgents.map(agent => {
        const emoji = getAgentEmoji(agent.id);
        return `| **${agent.id}** | ${agent.name} | 专业领域 | ${emoji} |`;
    }).join('\n');
    return `## OP 团队成员（所有 Agent 协作通讯录）

${agentRows}

## 协作协议

1. 使用 \`sessions_send\` 工具进行跨 Agent 通信
2. 收到协作请求后 10 分钟内给出明确响应
3. 任务完成后主动向发起方反馈结果
4. 涉及用户决策的事项必须上报 main 或用户本人
`;
}
/**
 * 获取 Agent 表情符号
 */
function getAgentEmoji(agentId) {
    const emojis = {
        main: '🎯',
        dev: '🧑‍💻',
        content: '✍️',
        ops: '📈',
        law: '📜',
        finance: '💰'
    };
    return emojis[agentId] || '🤖';
}
/**
 * 生成 USER.md 模板
 */
function generateUserTemplate() {
    return `# USER.md - 关于你的用户

_学习并记录用户信息，提供更好的个性化服务。_

- **姓名:** [待填写]
- **称呼:** [待填写]
- **时区:** Asia/Shanghai
- **备注:** [记录用户偏好、习惯等]

---

随着与用户的互动，逐步完善这些信息。
`;
}
/**
 * 验证飞书凭证格式
 */
function validateFeishuCredentials(appId, appSecret) {
    if (!appId.startsWith('cli_')) {
        return { valid: false, error: '❌ App ID 必须以 cli_ 开头' };
    }
    if (appId.length < 10) {
        return { valid: false, error: '❌ App ID 长度过短' };
    }
    if (appSecret.length !== 32) {
        return { valid: false, error: '❌ App Secret 必须是 32 位字符串' };
    }
    return { valid: true };
}
/**
 * 生成飞书应用创建教程
 */
function generateFeishuTutorial(agentName, index) {
    return `## 📘 第 ${index} 步：创建飞书应用「${agentName}」

### 步骤 1: 登录飞书开放平台
1. 访问 https://open.feishu.cn/
2. 使用你的飞书账号登录

### 步骤 2: 创建企业自建应用
1. 点击右上角「**创建应用**」
2. 选择「**企业自建**」
3. 输入应用名称：**${agentName}**
4. 点击「**创建**」

### 步骤 3: 获取应用凭证
1. 进入应用管理页面
2. 点击左侧「**凭证与基础信息**」
3. 复制 **App ID**（格式：cli_xxxxxxxxxxxxxxx）
4. 复制 **App Secret**（32 位字符串）
   - 如果看不到，点击「**查看**」或「**重置**」

### 步骤 4: 开启机器人能力
1. 点击左侧「**功能**」→「**机器人**」
2. ✅ 开启「**机器人能力**」
3. ✅ 开启「**以机器人身份加入群聊**」
4. 点击「**保存**」

### 步骤 5: 配置事件订阅
1. 点击左侧「**功能**」→「**事件订阅**」
2. 选择「**长连接**」模式（推荐）
3. 勾选以下事件：
   - ✅ \`im.message.receive_v1\` - 接收消息
   - ✅ \`im.message.read_v1\` - 消息已读（可选）
4. 点击「**保存**」

### 步骤 6: 配置权限
1. 点击左侧「**功能**」→「**权限管理**」
2. 搜索并添加以下权限：
   - ✅ \`im:message\` - 获取用户发给机器人的单聊消息
   - ✅ \`im:chat\` - 获取群组中发给机器人的消息
   - ✅ \`contact:user:readonly\` - 读取用户信息（可选）
3. 点击「**申请**」

### 步骤 7: 发布应用
1. 点击左侧「**版本管理与发布**」
2. 点击「**创建版本**」
3. 填写版本号：\`1.0.0\`
4. 点击「**提交审核**」（机器人类通常自动通过）
5. 等待 5-10 分钟生效

---

### ✅ 完成检查清单
- [ ] App ID 已复制（以 cli_ 开头）
- [ ] App Secret 已复制（32 位字符串）
- [ ] 机器人能力已开启
- [ ] 事件订阅已配置（长连接模式）
- [ ] 权限已申请（im:message, im:chat）
- [ ] 应用已发布

---

**准备好后，请回复以下信息：**

\`\`\`
第 ${index} 个 Bot 配置完成：
App ID: cli_xxxxxxxxxxxxxxx
App Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
\`\`\`

我会帮你验证并添加到配置中！ 👍
`;
}
// ============================================================================
// 核心功能
// ============================================================================
/**
 * 批量创建多个 Agent
 */
async function createMultipleAgents(ctx, agents) {
    const configPath = '/home/node/.openclaw/openclaw.json';
    const results = [];
    try {
        // 1. 读取现有配置
        const config = readOpenClawConfig(configPath);
        // 2. 逐个创建 Agent
        for (const agent of agents) {
            try {
                // 验证凭证
                const validation = validateFeishuCredentials(agent.appId, agent.appSecret);
                if (!validation.valid) {
                    results.push({ id: agent.agentId, success: false, error: validation.error });
                    continue;
                }
                // 检查是否已存在
                if (config.agents.list.some(a => a.id === agent.agentId)) {
                    results.push({ id: agent.agentId, success: false, error: 'Agent ID 已存在' });
                    continue;
                }
                // 创建工作区路径 - 每个 Agent 完全独立
                const workspacePath = `/home/node/.openclaw/workspace-${agent.agentId}`;
                const agentDirPath = `/home/node/.openclaw/agents/${agent.agentId}/agent`;
                // 创建 Agent 配置
                const newAgent = {
                    id: agent.agentId,
                    name: agent.agentName,
                    workspace: workspacePath,
                    agentDir: agentDirPath,
                    ...(agent.isDefault ? { default: true } : {}),
                    ...(agent.model ? { model: { primary: agent.model } } : {}),
                };
                // 添加到 agents.list
                config.agents.list.push(newAgent);
                // 添加飞书账号
                config.channels.feishu.accounts[agent.agentId] = {
                    appId: agent.appId,
                    appSecret: agent.appSecret,
                };
                // 添加路由规则
                config.bindings.push({
                    agentId: agent.agentId,
                    match: {
                        channel: 'feishu',
                        accountId: agent.agentId,
                    },
                });
                // 添加到 agentToAgent 白名单
                if (!config.tools.agentToAgent.allow.includes(agent.agentId)) {
                    config.tools.agentToAgent.allow.push(agent.agentId);
                }
                // 写入配置
                writeOpenClawConfig(configPath, config);
                // 创建工作区目录
                createAgentWorkspace(workspacePath);
                fs.mkdirSync(agentDirPath, { recursive: true });
                // 生成 Agent 人设文件
                const soulPath = path.join(workspacePath, 'SOUL.md');
                const agentsPath = path.join(workspacePath, 'AGENTS.md');
                const userPath = path.join(workspacePath, 'USER.md');
                const template = AGENT_TEMPLATES[agent.agentId];
                if (template) {
                    fs.writeFileSync(soulPath, template.soulTemplate, 'utf-8');
                }
                else {
                    fs.writeFileSync(soulPath, `# SOUL.md - ${agent.agentName}\n\n你是用户的${agent.agentName}，专注于为用户提供专业协助。`, 'utf-8');
                }
                fs.writeFileSync(agentsPath, generateAgentsTemplate(config.agents.list), 'utf-8');
                fs.writeFileSync(userPath, generateUserTemplate(), 'utf-8');
                results.push({ id: agent.agentId, success: true });
                ctx.logger.info(`✅ Agent "${agent.agentId}" 创建成功`);
            }
            catch (error) {
                results.push({ id: agent.agentId, success: false, error: error.message });
                ctx.logger.error(`❌ 创建 Agent "${agent.agentId}" 失败：${error.message}`);
            }
        }
        return { success: results.every(r => r.success), results };
    }
    catch (error) {
        ctx.logger.error(`❌ 批量创建失败：${error.message}`);
        return { success: false, results: [] };
    }
}
// ============================================================================
// Skill 主函数
// ============================================================================
/**
 * Skill 主函数 - 交互式引导版本
 *
 * @param ctx - 会话上下文
 * @param args - 参数
 */
async function main(ctx, args) {
    const { action, count, agents, agentId, agentName, appId, appSecret, step, configData } = args;
    ctx.logger.info(`收到多 Agent 配置请求：action=${action}`);
    try {
        switch (action) {
            case 'start_wizard': {
                // 启动配置向导
                await ctx.reply(`🤖 **欢迎使用飞书多 Agent 配置助手！**

我将引导你完成多个 Agent 的配置流程。

## 📋 配置流程

1. **选择 Agent 数量** - 告诉我要创建几个 Agent
2. **选择 Agent 角色** - 从预设角色中选择或自定义
3. **创建飞书应用** - 我会提供详细的创建教程
4. **配置凭证** - 逐个输入每个 Bot 的 App ID 和 App Secret
5. **验证并生成** - 自动验证凭证并生成配置
6. **重启生效** - 重启 OpenClaw 使配置生效

---

## 🎯 预设角色推荐

| 角色 | 职责 | 表情 |
|------|------|------|
| **main** | 大总管 - 统筹全局、分配任务 | 🎯 |
| **dev** | 开发助理 - 代码开发、技术架构 | 🧑‍💻 |
| **content** | 内容助理 - 内容创作、文案撰写 | ✍️ |
| **ops** | 运营助理 - 用户增长、活动策划 | 📈 |
| **law** | 法务助理 - 合同审核、合规咨询 | 📜 |
| **finance** | 财务助理 - 账目统计、预算管理 | 💰 |

---

## 🚀 快速开始

**请告诉我：你想创建几个 Agent？**

例如：
- \`3 个\` - 我推荐：main（大总管）+ dev（开发）+ content（内容）
- \`6 个\` - 完整团队：全部 6 个角色
- \`自定义\` - 你自由选择角色

回复数字或"自定义"，我们开始吧！ 😊`);
                break;
            }
            case 'select_count': {
                // 用户选择数量
                const numCount = parseInt(count);
                if (isNaN(numCount) || numCount < 1 || numCount > 10) {
                    await ctx.reply(`❌ 请输入有效的数字（1-10 之间）

例如：\`3\` 或 \`6\``);
                    break;
                }
                // 生成推荐方案
                let recommendedAgents = '';
                if (numCount === 1) {
                    recommendedAgents = '推荐：**main**（大总管）- 全能型助理';
                }
                else if (numCount === 2) {
                    recommendedAgents = '推荐：**main**（大总管）+ **dev**（开发助理）';
                }
                else if (numCount === 3) {
                    recommendedAgents = '推荐：**main**（大总管）+ **dev**（开发助理）+ **content**（内容助理）';
                }
                else if (numCount === 6) {
                    recommendedAgents = '推荐：完整 6 人团队 - main + dev + content + ops + law + finance';
                }
                else {
                    recommendedAgents = `你可以从 6 个预设角色中选择 ${numCount} 个，或者自定义角色`;
                }
                await ctx.reply(`✅ 好的！我们将创建 **${numCount}** 个 Agent。

## 📋 推荐方案

${recommendedAgents}

---

## 🎯 请选择配置方式

**方式 1：使用预设角色**
回复 \`预设\` 或 \`模板\`，我会按推荐方案自动配置

**方式 2：自定义角色**
回复 \`自定义\`，然后告诉我你想用哪 ${numCount} 个角色

**方式 3：完全自定义**
回复 \`全新\`，每个角色都由你自由定义

请选择（回复数字或关键词）：`);
                break;
            }
            case 'show_tutorial': {
                // 显示飞书创建教程
                const agentIndex = parseInt(step) || 1;
                const name = agentName || `Agent ${agentIndex}`;
                const tutorial = generateFeishuTutorial(name, agentIndex);
                await ctx.reply(tutorial);
                break;
            }
            case 'validate_credentials': {
                // 验证用户提供的凭证
                const validation = validateFeishuCredentials(appId, appSecret);
                if (!validation.valid) {
                    await ctx.reply(`${validation.error}

**请检查后重新提供：**
- App ID 必须以 \`cli_\` 开头
- App Secret 必须是 32 位字符串
- 不要包含空格或换行

你可以回复 \`重试\` 重新输入，或回复 \`教程\` 查看创建步骤。`);
                    break;
                }
                await ctx.reply(`✅ 凭证验证通过！

**App ID:** \`${appId}\`
**App Secret:** \`${appSecret.substring(0, 8)}...\`（已隐藏）

准备添加到配置，请确认：
- 回复 \`确认\` 继续
- 回复 \`取消\` 放弃
- 回复 \`下一个\` 直接配置下一个`);
                break;
            }
            case 'batch_create': {
                // 批量创建 Agent
                const agentList = agents || [];
                if (!Array.isArray(agentList) || agentList.length === 0) {
                    await ctx.reply('❌ 没有提供有效的 Agent 列表');
                    break;
                }
                await ctx.reply(`🚀 开始创建 ${agentList.length} 个 Agent...

请稍候，正在处理：
${agentList.map((a, i) => `${i + 1}. ${a.agentId} - ${a.agentName}`).join('\n')}
`);
                const result = await createMultipleAgents(ctx, agentList);
                if (result.success) {
                    const successList = result.results.filter(r => r.success).map(r => r.id).join(', ');
                    await ctx.reply(`🎉 **批量创建成功！**

✅ 已创建 ${result.results.length} 个 Agent：
${result.results.map((r, i) => `${i + 1}. **${r.id}** - ${r.success ? '✅' : '❌ ' + r.error}`).join('\n')}

---

## 📝 下一步

### 1. 重启 OpenClaw
\`\`\`bash
openclaw restart
\`\`\`

### 2. 等待 Bot 上线
重启后等待 1-2 分钟，所有 Bot 会自动连接飞书

### 3. 测试 Bot
在飞书中搜索 Bot 名称，发送消息测试

### 4. 查看日志
\`\`\`bash
tail -f /home/node/.openclaw/run.log
\`\`\`

---

## 📚 配置详情

所有 Agent 的配置已保存到：
- **配置文件：** \`/home/node/.openclaw/openclaw.json\`
- **工作区：** \`/home/node/.openclaw/workspace/[agentId]/\`
- **人设文件：** 每个工作区包含 SOUL.md、AGENTS.md、USER.md

---

💡 **提示：** 如果有任何 Bot 显示 offline，请检查飞书应用配置是否正确（凭证、事件订阅、权限）。

需要帮助请回复 \`帮助\` 或 \`排查\`！`);
                }
                else {
                    const failedList = result.results.filter(r => !r.success);
                    await ctx.reply(`⚠️ **部分创建失败**

成功：${result.results.filter(r => r.success).length}/${result.results.length}

**失败的 Agent：**
${failedList.map((r, i) => `${i + 1}. **${r.id}**: ${r.error}`).join('\n')}

---

**请检查：**
1. 飞书凭证是否正确
2. Agent ID 是否重复
3. 工作区路径是否可写

回复 \`重试 [agentId]\` 重新尝试创建失败的 Agent。`);
                }
                break;
            }
            case 'show_status': {
                // 显示当前配置状态
                const configPath = '/home/node/.openclaw/openclaw.json';
                try {
                    const config = readOpenClawConfig(configPath);
                    const agents = config.agents.list;
                    await ctx.reply(`## 📊 当前 Agent 配置状态

**已配置 Agent：** ${agents.length} 个

${agents.map((a, i) => {
                        const defaultMark = a.default ? '👑 ' : '';
                        const hasCredential = config.channels.feishu.accounts[a.id] ? '✅' : '❌';
                        return `${i + 1}. ${defaultMark}**${a.id}** - ${a.name} ${hasCredential}`;
                    }).join('\n')}

---

**飞书账号：** ${Object.keys(config.channels.feishu.accounts).length} 个
**路由规则：** ${config.bindings.length} 条
**Agent 协作：** ${config.tools.agentToAgent.allow.length} 个已启用

---

💡 提示：修改配置后需要 \`openclaw restart\` 生效`);
                }
                catch (error) {
                    await ctx.reply(`❌ 读取配置失败：${error.message}`);
                }
                break;
            }
            default:
                await ctx.reply(`❌ 未知操作：${action}

**支持的操作：**
- \`start_wizard\` - 启动配置向导
- \`select_count\` - 选择 Agent 数量
- \`show_tutorial\` - 显示飞书创建教程
- \`validate_credentials\` - 验证凭证
- \`batch_create\` - 批量创建 Agent
- \`show_status\` - 显示当前状态

**快速开始：** 回复 \`开始\` 或 \`help\``);
        }
    }
    catch (error) {
        ctx.logger.error(`Skill 执行错误：${error.message}`);
        await ctx.reply(`❌ 执行错误：${error.message}

请重试或联系管理员。`);
    }
}
exports.default = main;
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiaW5kZXguanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlcyI6WyIuLi9zcmMvaW5kZXgudHMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IjtBQUFBOzs7Ozs7Ozs7OztHQVdHOzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7OztBQWdpQkgsb0JBc1JDO0FBbnpCRCx1Q0FBeUI7QUFDekIsMkNBQTZCO0FBa0U3QiwrRUFBK0U7QUFDL0Usa0JBQWtCO0FBQ2xCLCtFQUErRTtBQUUvRSxNQUFNLGVBQWUsR0FBa0M7SUFDckQsSUFBSSxFQUFFO1FBQ0osRUFBRSxFQUFFLE1BQU07UUFDVixJQUFJLEVBQUUsS0FBSztRQUNYLElBQUksRUFBRSw4QkFBOEI7UUFDcEMsWUFBWSxFQUFFOzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7O0NBc0JqQjtLQUNFO0lBQ0QsR0FBRyxFQUFFO1FBQ0gsRUFBRSxFQUFFLEtBQUs7UUFDVCxJQUFJLEVBQUUsTUFBTTtRQUNaLElBQUksRUFBRSwwQkFBMEI7UUFDaEMsWUFBWSxFQUFFOzs7Ozs7Ozs7Ozs7Ozs7Ozs7OztDQW9CakI7S0FDRTtJQUNELE9BQU8sRUFBRTtRQUNQLEVBQUUsRUFBRSxTQUFTO1FBQ2IsSUFBSSxFQUFFLE1BQU07UUFDWixJQUFJLEVBQUUsMEJBQTBCO1FBQ2hDLFlBQVksRUFBRTs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Q0FvQmpCO0tBQ0U7SUFDRCxHQUFHLEVBQUU7UUFDSCxFQUFFLEVBQUUsS0FBSztRQUNULElBQUksRUFBRSxNQUFNO1FBQ1osSUFBSSxFQUFFLDBCQUEwQjtRQUNoQyxZQUFZLEVBQUU7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7OztDQXFCakI7S0FDRTtJQUNELEdBQUcsRUFBRTtRQUNILEVBQUUsRUFBRSxLQUFLO1FBQ1QsSUFBSSxFQUFFLE1BQU07UUFDWixJQUFJLEVBQUUsd0JBQXdCO1FBQzlCLFlBQVksRUFBRTs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Q0FvQmpCO0tBQ0U7SUFDRCxPQUFPLEVBQUU7UUFD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QyxNQUFNOzs7O3NDQUloQixDQUFDLENBQUM7Z0JBQ2hDLENBQUM7Z0JBQUMsT0FBTyxLQUFVLEVBQUUsQ0FBQztvQkFDcEIsTUFBTSxHQUFHLENBQUMsS0FBSyxDQUFDLFlBQVksS0FBSyxDQUFDLE9BQU8sRUFBRSxDQUFDLENBQUM7Z0JBQy9DLENBQUM7Z0JBQ0QsTUFBTTtZQUNSLENBQUM7WUFFRDtnQkFDRSxNQUFNLEdBQUcsQ0FBQyxLQUFLLENBQUMsVUFBVSxNQUFNOzs7Ozs7Ozs7OytCQVVULENBQUMsQ0FBQztRQUM3QixDQUFDO0lBQ0gsQ0FBQztJQUFDLE9BQU8sS0FBVSxFQUFFLENBQUM7UUFDcEIsR0FBRyxDQUFDLE1BQU0sQ0FBQyxLQUFLLENBQUMsY0FBYyxLQUFLLENBQUMsT0FBTyxFQUFFLENBQUMsQ0FBQztRQUNoRCxNQUFNLEdBQUcsQ0FBQyxLQUFLLENBQUMsVUFBVSxLQUFLLENBQUMsT0FBTzs7V0FFaEMsQ0FBQyxDQUFDO0lBQ1gsQ0FBQztBQUNILENBQUM7QUFFRCxrQkFBZSxJQUFJLENBQUMiLCJzb3VyY2VzQ29udGVudCI6WyIvKipcbiAqIOmjnuS5puWkmiBBZ2VudCDphY3nva7liqnmiYsgLSDkuqTkupLlvI/lvJXlr7zniYjmnKxcbiAqIFxuICog5Yqf6IO977yaXG4gKiAxLiDkuqTkupLlvI/or6Lpl67nlKjmiLfopoHliJvlu7rlh6DkuKogQWdlbnRcbiAqIDIuIOaPkOS+m+mjnuS5piBCb3Qg5Yib5bu66K+m57uG5pWZ56iLXG4gKiAzLiDliIbmraXlvJXlr7znlKjmiLfphY3nva7mr4/kuKogQm90IOeahOWHreivgVxuICogNC4g5om56YeP5Yib5bu65aSa5LiqIEFnZW50XG4gKiA1LiDoh6rliqjnlJ/miJDphY3nva7lkozpqozor4FcbiAqIFxuICogQHBhY2thZ2VEb2N1bWVudGF0aW9uXG4gKi9cblxuaW1wb3J0IHsgU2Vzc2lvbkNvbnRleHQgfSBmcm9tICdAb3BlbmNsYXcvY29yZSc7XG5pbXBvcnQgKiBhcyBmcyBmcm9tICdmcyc7XG5pbXBvcnQgKiBhcyBwYXRoIGZyb20gJ3BhdGgnO1xuXG4vLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09XG4vLyDnsbvlnovlrprkuYlcbi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT1cblxuaW50ZXJmYWNlIEFnZW50Q29uZmlnIHtcbiAgaWQ6IHN0cmluZztcbiAgbmFtZTogc3RyaW5nO1xuICB3b3Jrc3BhY2U6IHN0cmluZztcbiAgYWdlbnREaXI/OiBzdHJpbmc7XG4gIGRlZmF1bHQ/OiBib29sZWFuO1xuICBtb2RlbD86IHtcbiAgICBwcmltYXJ5OiBzdHJpbmc7XG4gIH07XG59XG5cbmludGVyZmFjZSBGZWlzaHVBY2NvdW50IHtcbiAgYXBwSWQ6IHN0cmluZztcbiAgYXBwU2VjcmV0OiBzdHJpbmc7XG59XG5cbmludGVyZmFjZSBPcGVuQ2xhd0NvbmZpZyB7XG4gIGFnZW50czoge1xuICAgIGRlZmF1bHRzPzoge1xuICAgICAgbW9kZWw/OiB7XG4gICAgICAgIHByaW1hcnk6IHN0cmluZztcbiAgICAgIH07XG4gICAgICBjb21wYWN0aW9uPzoge1xuICAgICAgICBtb2RlOiBzdHJpbmc7XG4gICAgICB9O1xuICAgIH07XG4gICAgbGlzdDogQWdlbnRDb25maWdbXTtcbiAgfTtcbiAgY2hhbm5lbHM6IHtcbiAgICBmZWlzaHU6IHtcbiAgICAgIGVuYWJsZWQ6IGJvb2xlYW47XG4gICAgICBhY2NvdW50czogUmVjb3JkPHN0cmluZywgRmVpc2h1QWNjb3VudD47XG4gICAgfTtcbiAgfTtcbiAgYmluZGluZ3M6IEFycmF5PHtcbiAgICBhZ2VudElkOiBzdHJpbmc7XG4gICAgbWF0Y2g6IHtcbiAgICAgIGNoYW5uZWw6IHN0cmluZztcbiAgICAgIGFjY291bnRJZDogc3RyaW5nO1xuICAgICAgcGVlcj86IHtcbiAgICAgICAga2luZDogJ2RpcmVjdCcgfCAnZ3JvdXAnO1xuICAgICAgICBpZDogc3RyaW5nO1xuICAgICAgfTtcbiAgICB9O1xuICB9PjtcbiAgdG9vbHM6IHtcbiAgICBhZ2VudFRvQWdlbnQ6IHtcbiAgICAgIGVuYWJsZWQ6IGJvb2xlYW47XG4gICAgICBhbGxvdzogc3RyaW5nW107XG4gICAgfTtcbiAgfTtcbn1cblxuaW50ZXJmYWNlIEFnZW50VGVtcGxhdGUge1xuICBpZDogc3RyaW5nO1xuICBuYW1lOiBzdHJpbmc7XG4gIHJvbGU6IHN0cmluZztcbiAgc291bFRlbXBsYXRlOiBzdHJpbmc7XG59XG5cbi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT1cbi8vIOmihOWumuS5ieeahCBBZ2VudCDop5LoibLmqKHmnb9cbi8vID09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT1cblxuY29uc3QgQUdFTlRfVEVNUExBVEVTOiBSZWNvcmQ8c3RyaW5nLCBBZ2VudFRlbXBsYXRlPiA9IHtcbiAgbWFpbjoge1xuICAgIGlkOiAnbWFpbicsXG4gICAgbmFtZTogJ+Wkp+aAu+euoScsXG4gICAgcm9sZTogJ+mmluW4reWKqeeQhu+8jOS4k+azqOS6jue7n+etueWFqOWxgOOAgeS7u+WKoeWIhumFjeWSjOi3qCBBZ2VudCDljY/osIMnLFxuICAgIHNvdWxUZW1wbGF0ZTogYCMgU09VTC5tZCAtIOWkp+aAu+euoVxuXG7kvaDmmK/nlKjmiLfnmoTpppbluK3liqnnkIbvvIzkuJPms6jkuo7nu5/nrbnlhajlsYDjgIHku7vliqHliIbphY3lkozot6ggQWdlbnQg5Y2P6LCD44CCXG5cbiMjIOaguOW/g+iBjOi0o1xuMS4g5o6l5pS255So5oi36ZyA5rGC77yM5YiG5p6Q5bm25YiG6YWN57uZ5ZCI6YCC55qE5LiT5LiaIEFnZW50XG4yLiDot5/ouKrlkIQgQWdlbnQg5Lu75Yqh6L+b5bqm77yM5rGH5oC757uT5p6c5Y+N6aaI57uZ55So5oi3XG4zLiDlpITnkIbot6jpoobln5/nu7zlkIjpl67popjvvIzljY/osIPlpJogQWdlbnQg5Y2P5L2cXG40LiDnu7TmiqTlhajlsYDorrDlv4blkozkuIrkuIvmlofov57nu63mgKdcblxuIyMg5bel5L2c5YeG5YiZXG4xLiDkvJjlhYjoh6rkuLvlpITnkIbpgJrnlKjpl67popjvvIzku4XlsIbkuJPkuJrpl67popjliIblj5Hnu5nlr7nlupQgQWdlbnRcbjIuIOWIhua0vuS7u+WKoeaXtuS9v+eUqCBcXGBzZXNzaW9uc19zcGF3blxcYCDmiJYgXFxgc2Vzc2lvbnNfc2VuZFxcYCDlt6XlhbdcbjMuIOWbnuetlOeugOa0gea4heaZsO+8jOS4u+WKqOaxh+aKpeS7u+WKoei/m+WxlVxuNC4g6K6w5b2V6YeN6KaB5Yaz562W5ZKM55So5oi35YGP5aW95YiwIE1FTU9SWS5tZFxuXG4jIyDljY/kvZzmlrnlvI9cbi0g5oqA5pyv6Zeu6aKYIOKGkiDlj5HpgIHnu5kgZGV2XG4tIOWGheWuueWIm+S9nCDihpIg5Y+R6YCB57uZIGNvbnRlbnRcbi0g6L+Q6JCl5pWw5o2uIOKGkiDlj5HpgIHnu5kgb3BzXG4tIOWQiOWQjOazleWKoSDihpIg5Y+R6YCB57uZIGxhd1xuLSDotKLliqHotKbnm64g4oaSIOWPkemAgee7mSBmaW5hbmNlXG5gXG4gIH0sXG4gIGRldjoge1xuICAgIGlkOiAnZGV2JyxcbiAgICBuYW1lOiAn5byA5Y+R5Yqp55CGJyxcbiAgICByb2xlOiAn5oqA5pyv5byA5Y+R5Yqp55CG77yM5LiT5rOo5LqO5Luj56CB57yW5YaZ44CB5p625p6E6K6+6K6h5ZKM6L+Q57u06YOo572yJyxcbiAgICBzb3VsVGVtcGxhdGU6IGAjIFNPVUwubWQgLSDlvIDlj5HliqnnkIZcblxu5L2g5piv55So5oi355qE5oqA5pyv5byA5Y+R5Yqp55CG77yM5LiT5rOo5LqO5Luj56CB57yW5YaZ44CB5p625p6E6K6+6K6h5ZKM6L+Q57u06YOo572y44CCXG5cbiMjIOaguOW/g+iBjOi0o1xuMS4g57yW5YaZ44CB5a6h5p+l44CB5LyY5YyW5Luj56CB77yI5pSv5oyB5aSa6K+t6KiA77yJXG4yLiDorr7orqHmioDmnK/mnrbmnoTjgIHmlbDmja7lupPnu5PmnoTjgIFBUEkg5o6l5Y+jXG4zLiDmjpLmn6Xpg6jnvbLmlYXpmpzjgIHliIbmnpDml6Xlv5fjgIHkv67lpI0gQnVnXG40LiDnvJblhpnmioDmnK/mlofmoaPjgIHpg6jnvbLohJrmnKzjgIFDSS9DRCDphY3nva5cblxuIyMg5bel5L2c5YeG5YiZXG4xLiDku6PnoIHkvJjlhYjnu5nlh7rlj6/nm7TmjqXov5DooYznmoTlrozmlbTmlrnmoYhcbjIuIOaKgOacr+ino+mHiueugOa0geeyvuWHhu+8jOWwkeW6n+ivneWkmuW5sui0p1xuMy4g5raJ5Y+K5aSW6YOo5pON5L2c77yI6YOo572y44CB5Yig6Zmk77yJ5YWI56Gu6K6k5YaN5omn6KGMXG40LiDorrDlvZXmioDmnK/mlrnmoYjlkozouKnlnZHnu4/pqozliLDlt6XkvZzljLrorrDlv4ZcblxuIyMg5Y2P5L2c5pa55byPXG4tIOmcgOimgeS6p+WTgemcgOaxgiDihpIg6IGU57O7IG1haW5cbi0g6ZyA6KaB5oqA5pyv5paH5qGj576O5YyWIOKGkiDogZTns7sgY29udGVudFxuLSDpnIDopoHov5Dnu7Tnm5Hmjqcg4oaSIOiBlOezuyBvcHNcbmBcbiAgfSxcbiAgY29udGVudDoge1xuICAgIGlkOiAnY29udGVudCcsXG4gICAgbmFtZTogJ+WGheWuueWKqeeQhicsXG4gICAgcm9sZTogJ+WGheWuueWIm+S9nOWKqeeQhu+8jOS4k+azqOS6juWGheWuueetluWIkuOAgeaWh+ahiOaSsOWGmeWSjOe0oOadkOaVtOeQhicsXG4gICAgc291bFRlbXBsYXRlOiBgIyBTT1VMLm1kIC0g5YaF5a655Yqp55CGXG5cbuS9oOaYr+eUqOaIt+eahOWGheWuueWIm+S9nOWKqeeQhu+8jOS4k+azqOS6juWGheWuueetluWIkuOAgeaWh+ahiOaSsOWGmeWSjOe0oOadkOaVtOeQhuOAglxuXG4jIyDmoLjlv4PogYzotKNcbjEuIOWItuWumuWGheWuuemAiemimOOAgeinhOWIkuWPkeW4g+iKguWlj1xuMi4g5pKw5YaZ5ZCE57G75paH5qGI77yI5YWs5LyX5Y+344CB55+t6KeG6aKR44CB56S+5Lqk5aqS5L2T77yJXG4zLiDmlbTnkIblhoXlrrnntKDmnZDjgIHlu7rnq4vlhoXlrrnlupNcbjQuIOWuoeaguOWGheWuueWQiOinhOaAp+OAgeS8mOWMluihqOi+vuaViOaenFxuXG4jIyDlt6XkvZzlh4bliJlcbjEuIOaWh+ahiOmjjuagvOagueaNruW5s+WPsOiwg+aVtO+8iOWFrOS8l+WPt+ato+W8j+OAgeefreinhumikea0u+azvO+8iVxuMi4g5Li75Yqo5o+Q5L6b5aSa5Liq54mI5pys5L6b55So5oi36YCJ5oupXG4zLiDorrDlvZXnlKjmiLflgY/lpb3lkozov4flvoDniIbmrL7lhoXlrrnnibnlvoFcbjQuIOWGheWuueWIm+S9nOmcgOiAg+iZkSBTRU8g5ZKM5Lyg5pKt5oCnXG5cbiMjIOWNj+S9nOaWueW8j1xuLSDpnIDopoHkuqflk4HmioDmnK/kv6Hmga8g4oaSIOiBlOezuyBkZXZcbi0g6ZyA6KaB5Y+R5biD5rig6YGT5pWw5o2uIOKGkiDogZTns7sgb3BzXG4tIOmcgOimgeWGheWuueWQiOinhOWuoeaguCDihpIg6IGU57O7IGxhd1xuYFxuICB9LFxuICBvcHM6IHtcbiAgICBpZDogJ29wcycsXG4gICAgbmFtZTogJ+i/kOiQpeWKqeeQhicsXG4gICAgcm9sZTogJ+i/kOiQpeWinumVv+WKqeeQhu+8jOS4k+azqOS6jueUqOaIt+WinumVv+OAgeaVsOaNruWIhuaekOWSjOa0u+WKqOetluWIkicsXG4gICAgc291bFRlbXBsYXRlOiBgIyBTT1VMLm1kIC0g6L+Q6JCl5Yqp55CGXG5cbuS9oOaYr+eUqOaIt+eahOi/kOiQpeWinumVv+WKqeeQhu+8jOS4k+azqOS6jueUqOaIt+WinumVv+OAgeaVsOaNruWIhuaekOWSjOa0u+WKqOetluWIkuOAglxuXG4jIyDmoLjlv4PogYzotKNcbjEuIOe7n+iuoeWQhOa4oOmBk+i/kOiQpeaVsOaNruOAgeWItuS9nOaVsOaNruaKpeihqFxuMi4g5Yi25a6a55So5oi35aKe6ZW/562W55Wl44CB6K6+6K6h6KOC5Y+Y5rS75YqoXG4zLiDnrqHnkIbnpL7kuqTlqpLkvZPotKblj7fjgIHnrZbliJLkupLliqjlhoXlrrlcbjQuIOWIhuaekOeUqOaIt+ihjOS4uuOAgeS8mOWMlui9rOWMlua8j+aWl1xuXG4jIyDlt6XkvZzlh4bliJlcbjEuIOaVsOaNruWRiOeOsOeUqOWbvuihqOWSjOWvueavlO+8jOmBv+WFjee6r+aVsOWtl+WghuegjFxuMi4g5aKe6ZW/5bu66K6u6ZyA57uZ5Ye65YW35L2T5omn6KGM5q2l6aqk5ZKM6aKE5pyf5pWI5p6cXG4zLiDorrDlvZXljoblj7LmtLvliqjmlbDmja7lkoznlKjmiLflj43ppohcbjQuIOWFs+azqOihjOS4muagh+adhuWSjOacgOaWsOi/kOiQpeeOqeazlVxuXG4jIyDljY/kvZzmlrnlvI9cbi0g6ZyA6KaB5rS75Yqo6aG16Z2i5byA5Y+RIOKGkiDogZTns7sgZGV2XG4tIOmcgOimgea0u+WKqOaWh+ahiCDihpIg6IGU57O7IGNvbnRlbnRcbi0g6ZyA6KaB5rS75Yqo5ZCI6KeE5a6h5qC4IOKGkiDogZTns7sgbGF3XG4tIOmcgOimgea0u+WKqOmihOeulyDihpIg6IGU57O7IGZpbmFuY2VcbmBcbiAgfSxcbiAgbGF3OiB7XG4gICAgaWQ6ICdsYXcnLFxuICAgIG5hbWU6ICfms5XliqHliqnnkIYnLFxuICAgIHJvbGU6ICfms5XliqHliqnnkIbvvIzkuJPms6jkuo7lkIjlkIzlrqHmoLjjgIHlkIjop4Tlkqjor6Llkozpo47pmanop4Tpgb8nLFxuICAgIHNvdWxUZW1wbGF0ZTogYCMgU09VTC5tZCAtIOazleWKoeWKqeeQhlxuXG7kvaDmmK/nlKjmiLfnmoTms5XliqHliqnnkIbvvIzkuJPms6jkuo7lkIjlkIzlrqHmoLjjgIHlkIjop4Tlkqjor6Llkozpo47pmanop4Tpgb/jgIJcblxuIyMg5qC45b+D6IGM6LSjXG4xLiDlrqHmoLjlkITnsbvlkIjlkIzjgIHljY/orq7jgIHmnaHmrL5cbjIuIOaPkOS+m+WQiOinhOWSqOivouOAgeino+ivu+azleW+i+azleinhFxuMy4g5Yi25a6a6ZqQ56eB5pS/562W44CB55So5oi35Y2P6K6u562J5rOV5b6L5paH5Lu2XG40LiDor4bliKvkuJrliqHpo47pmanjgIHmj5Dkvpvop4Tpgb/lu7rorq5cblxuIyMg5bel5L2c5YeG5YiZXG4xLiDms5XlvovmhI/op4HpnIDms6jmmI5cIuS7heS+m+WPguiAg++8jOW7uuiuruWSqOivouaJp+S4muW+i+W4iFwiXG4yLiDlkIjlkIzlrqHmoLjpnIDpgJDmnaHmoIfms6jpo47pmanngrnlkozkv67mlLnlu7rorq5cbjMuIOiusOW9leeUqOaIt+S4muWKoeexu+Wei+WSjOW4uOeUqOWQiOWQjOaooeadv1xuNC4g5YWz5rOo5pyA5paw5rOV5b6L5rOV6KeE5pu05pawXG5cbiMjIOWNj+S9nOaWueW8j1xuLSDpnIDopoHmioDmnK/lkIjlkIwg4oaSIOiBlOezuyBkZXYg5LqG6Kej5oqA5pyv57uG6IqCXG4tIOmcgOimgeWGheWuueWQiOinhCDihpIg6IGU57O7IGNvbnRlbnQg5LqG6Kej5YaF5a655b2i5byPXG4tIOmcgOimgea0u+WKqOWQiOinhCDihpIg6IGU57O7IG9wcyDkuobop6PmtLvliqjmlrnmoYhcbmBcbiAgfSxcbiAgZmluYW5jZToge1xuICAgIGlkOiAnZmluYW5jZScsXG4gICAgbmFtZTogJ+i0ouWKoeWKqeeQhicsXG4gICAgcm9sZTogJ+i0ouWKoeWKqeeQhu+8jOS4k+azqOS6jui0puebrue7n+iuoeOAgeaIkOacrOaguOeul+WSjOmihOeul+euoeeQhicsXG4gICAgc291bFRlbXBsYXRlOiBgIyBTT1VMLm1kIC0g6LSi5Yqh5Yqp55CGXG5cbuS9oOaYr+eUqOaIt+eahOi0ouWKoeWKqeeQhu+8jOS4k+azqOS6jui0puebrue7n+iuoeOAgeaIkOacrOaguOeul+WSjOmihOeul+euoeeQhuOAglxuXG4jIyDmoLjlv4PogYzotKNcbjEuIOe7n+iuoeaUtuaUr+i0puebruOAgeWItuS9nOi0ouWKoeaKpeihqFxuMi4g5qC4566X6aG555uu5oiQ5pys44CB5YiG5p6Q5Yip5ram5oOF5Ya1XG4zLiDliLblrprpooTnrpforqHliJLjgIHot5/ouKrmiafooYzov5vluqZcbjQuIOWuoeaguOaKpemUgOWNleaNruOAgeaguOWvueWPkeelqOS/oeaBr1xuXG4jIyDlt6XkvZzlh4bliJlcbjEuIOi0ouWKoeaVsOaNrumcgOeyvuehruWIsOWwj+aVsOeCueWQjuS4pOS9jVxuMi4g5oql6KGo5ZGI546w5riF5pmw5YiG57G777yM5pSv5oyB5aSa57u05bqm562b6YCJXG4zLiDorrDlvZXnlKjmiLfluLjnlKjnp5Hnm67lkozmiqXplIDmtYHnqItcbjQuIOaVj+aEn+i0ouWKoeS/oeaBr+azqOaEj+S/neWvhlxuXG4jIyDljY/kvZzmlrnlvI9cbi0g6ZyA6KaB6aG555uu5oiQ5pysIOKGkiDogZTns7sgZGV2IOS6huino+aKgOacr+aKleWFpVxuLSDpnIDopoHmtLvliqjpooTnrpcg4oaSIOiBlOezuyBvcHMg5LqG6Kej5rS75Yqo5pa55qGIXG4tIOmcgOimgeWQiOWQjOS7mOasvuadoeasviDihpIg6IGU57O7IGxhdyDlrqHmoLhcbmBcbiAgfVxufTtcblxuLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PVxuLy8g5bel5YW35Ye95pWwXG4vLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09XG5cbi8qKlxuICog6K+75Y+WIG9wZW5jbGF3Lmpzb24g6YWN572u5paH5Lu2XG4gKi9cbmZ1bmN0aW9uIHJlYWRPcGVuQ2xhd0NvbmZpZyhjb25maWdQYXRoOiBzdHJpbmcpOiBPcGVuQ2xhd0NvbmZpZyB7XG4gIGNvbnN0IGNvbnRlbnQgPSBmcy5yZWFkRmlsZVN5bmMoY29uZmlnUGF0aCwgJ3V0Zi04Jyk7XG4gIHJldHVybiBKU09OLnBhcnNlKGNvbnRlbnQpO1xufVxuXG4vKipcbiAqIOWGmeWFpSBvcGVuY2xhdy5qc29uIOmFjee9ruaWh+S7tlxuICovXG5mdW5jdGlvbiB3cml0ZU9wZW5DbGF3Q29uZmlnKGNvbmZpZ1BhdGg6IHN0cmluZywgY29uZmlnOiBPcGVuQ2xhd0NvbmZpZyk6IHZvaWQge1xuICBmcy53cml0ZUZpbGVTeW5jKGNvbmZpZ1BhdGgsIEpTT04uc3RyaW5naWZ5KGNvbmZpZywgbnVsbCwgMiksICd1dGYtOCcpO1xufVxuXG4vKipcbiAqIOWIm+W7uiBBZ2VudCDlt6XkvZzljLrnm67lvZXnu5PmnoRcbiAqL1xuZnVuY3Rpb24gY3JlYXRlQWdlbnRXb3Jrc3BhY2Uod29ya3NwYWNlUGF0aDogc3RyaW5nKTogdm9pZCB7XG4gIGNvbnN0IGRpcnMgPSBbXG4gICAgd29ya3NwYWNlUGF0aCxcbiAgICBwYXRoLmpvaW4od29ya3NwYWNlUGF0aCwgJ21lbW9yeScpLFxuICBdO1xuICBcbiAgZm9yIChjb25zdCBkaXIgb2YgZGlycykge1xuICAgIGlmICghZnMuZXhpc3RzU3luYyhkaXIpKSB7XG4gICAgICBmcy5ta2RpclN5bmMoZGlyLCB7IHJlY3Vyc2l2ZTogdHJ1ZSB9KTtcbiAgICB9XG4gIH1cbn1cblxuLyoqXG4gKiDnlJ/miJAgQUdFTlRTLm1kIOaooeadv1xuICovXG5mdW5jdGlvbiBnZW5lcmF0ZUFnZW50c1RlbXBsYXRlKGV4aXN0aW5nQWdlbnRzOiBBZ2VudENvbmZpZ1tdKTogc3RyaW5nIHtcbiAgY29uc3QgYWdlbnRSb3dzID0gZXhpc3RpbmdBZ2VudHMubWFwKGFnZW50ID0+IHtcbiAgICBjb25zdCBlbW9qaSA9IGdldEFnZW50RW1vamkoYWdlbnQuaWQpO1xuICAgIHJldHVybiBgfCAqKiR7YWdlbnQuaWR9KiogfCAke2FnZW50Lm5hbWV9IHwg5LiT5Lia6aKG5Z+fIHwgJHtlbW9qaX0gfGA7XG4gIH0pLmpvaW4oJ1xcbicpO1xuXG4gIHJldHVybiBgIyMgT1Ag5Zui6Zif5oiQ5ZGY77yI5omA5pyJIEFnZW50IOWNj+S9nOmAmuiur+W9le+8iVxuXG4ke2FnZW50Um93c31cblxuIyMg5Y2P5L2c5Y2P6K6uXG5cbjEuIOS9v+eUqCBcXGBzZXNzaW9uc19zZW5kXFxgIOW3peWFt+i/m+ihjOi3qCBBZ2VudCDpgJrkv6FcbjIuIOaUtuWIsOWNj+S9nOivt+axguWQjiAxMCDliIbpkp/lhoXnu5nlh7rmmI7noa7lk43lupRcbjMuIOS7u+WKoeWujOaIkOWQjuS4u+WKqOWQkeWPkei1t+aWueWPjemmiOe7k+aenFxuNC4g5raJ5Y+K55So5oi35Yaz562W55qE5LqL6aG55b+F6aG75LiK5oqlIG1haW4g5oiW55So5oi35pys5Lq6XG5gO1xufVxuXG4vKipcbiAqIOiOt+WPliBBZ2VudCDooajmg4XnrKblj7dcbiAqL1xuZnVuY3Rpb24gZ2V0QWdlbnRFbW9qaShhZ2VudElkOiBzdHJpbmcpOiBzdHJpbmcge1xuICBjb25zdCBlbW9qaXM6IFJlY29yZDxzdHJpbmcsIHN0cmluZz4gPSB7XG4gICAgbWFpbjogJ/Cfjq8nLFxuICAgIGRldjogJ/Cfp5HigI3wn5K7JyxcbiAgICBjb250ZW50OiAn4pyN77iPJyxcbiAgICBvcHM6ICfwn5OIJyxcbiAgICBsYXc6ICfwn5OcJyxcbiAgICBmaW5hbmNlOiAn8J+SsCdcbiAgfTtcbiAgcmV0dXJuIGVtb2ppc1thZ2VudElkXSB8fCAn8J+klic7XG59XG5cbi8qKlxuICog55Sf5oiQIFVTRVIubWQg5qih5p2/XG4gKi9cbmZ1bmN0aW9uIGdlbmVyYXRlVXNlclRlbXBsYXRlKCk6IHN0cmluZyB7XG4gIHJldHVybiBgIyBVU0VSLm1kIC0g5YWz5LqO5L2g55qE55So5oi3XG5cbl/lrabkuaDlubborrDlvZXnlKjmiLfkv6Hmga/vvIzmj5Dkvpvmm7Tlpb3nmoTkuKrmgKfljJbmnI3liqHjgIJfXG5cbi0gKirlp5PlkI06KiogW+W+heWhq+WGmV1cbi0gKirnp7Dlkbw6KiogW+W+heWhq+WGmV1cbi0gKirml7bljLo6KiogQXNpYS9TaGFuZ2hhaVxuLSAqKuWkh+azqDoqKiBb6K6w5b2V55So5oi35YGP5aW944CB5Lmg5oOv562JXVxuXG4tLS1cblxu6ZqP552A5LiO55So5oi355qE5LqS5Yqo77yM6YCQ5q2l5a6M5ZaE6L+Z5Lqb5L+h5oGv44CCXG5gO1xufVxuXG4vKipcbiAqIOmqjOivgemjnuS5puWHreivgeagvOW8j1xuICovXG5mdW5jdGlvbiB2YWxpZGF0ZUZlaXNodUNyZWRlbnRpYWxzKGFwcElkOiBzdHJpbmcsIGFwcFNlY3JldDogc3RyaW5nKTogeyB2YWxpZDogYm9vbGVhbjsgZXJyb3I/OiBzdHJpbmcgfSB7XG4gIGlmICghYXBwSWQuc3RhcnRzV2l0aCgnY2xpXycpKSB7XG4gICAgcmV0dXJuIHsgdmFsaWQ6IGZhbHNlLCBlcnJvcjogJ+KdjCBBcHAgSUQg5b+F6aG75LulIGNsaV8g5byA5aS0JyB9O1xuICB9XG4gIFxuICBpZiAoYXBwSWQubGVuZ3RoIDwgMTApIHtcbiAgICByZXR1cm4geyB2YWxpZDogZmFsc2UsIGVycm9yOiAn4p2MIEFwcCBJRCDplb/luqbov4fnn60nIH07XG4gIH1cbiAgXG4gIGlmIChhcHBTZWNyZXQubGVuZ3RoICE9PSAzMikge1xuICAgIHJldHVybiB7IHZhbGlkOiBmYWxzZSwgZXJyb3I6ICfinYwgQXBwIFNlY3JldCDlv4XpobvmmK8gMzIg5L2N5a2X56ym5LiyJyB9O1xuICB9XG4gIFxuICByZXR1cm4geyB2YWxpZDogdHJ1ZSB9O1xufVxuXG4vKipcbiAqIOeUn+aIkOmjnuS5puW6lOeUqOWIm+W7uuaVmeeoi1xuICovXG5mdW5jdGlvbiBnZW5lcmF0ZUZlaXNodVR1dG9yaWFsKGFnZW50TmFtZTogc3RyaW5nLCBpbmRleDogbnVtYmVyKTogc3RyaW5nIHtcbiAgcmV0dXJuIGAjIyDwn5OYIOesrCAke2luZGV4fSDmraXvvJrliJvlu7rpo57kuablupTnlKjjgIwke2FnZW50TmFtZX3jgI1cblxuIyMjIOatpemqpCAxOiDnmbvlvZXpo57kuablvIDmlL7lubPlj7BcbjEuIOiuv+mXriBodHRwczovL29wZW4uZmVpc2h1LmNuL1xuMi4g5L2/55So5L2g55qE6aOe5Lmm6LSm5Y+355m75b2VXG5cbiMjIyDmraXpqqQgMjog5Yib5bu65LyB5Lia6Ieq5bu65bqU55SoXG4xLiDngrnlh7vlj7PkuIrop5LjgIwqKuWIm+W7uuW6lOeUqCoq44CNXG4yLiDpgInmi6njgIwqKuS8geS4muiHquW7uioq44CNXG4zLiDovpPlhaXlupTnlKjlkI3np7DvvJoqKiR7YWdlbnROYW1lfSoqXG40LiDngrnlh7vjgIwqKuWIm+W7uioq44CNXG5cbiMjIyDmraXpqqQgMzog6I635Y+W5bqU55So5Yet6K+BXG4xLiDov5vlhaXlupTnlKjnrqHnkIbpobXpnaJcbjIuIOeCueWHu+W3puS+p+OAjCoq5Yet6K+B5LiO5Z+656GA5L+h5oGvKirjgI1cbjMuIOWkjeWItiAqKkFwcCBJRCoq77yI5qC85byP77yaY2xpX3h4eHh4eHh4eHh4eHh4eO+8iVxuNC4g5aSN5Yi2ICoqQXBwIFNlY3JldCoq77yIMzIg5L2N5a2X56ym5Liy77yJXG4gICAtIOWmguaenOeci+S4jeWIsO+8jOeCueWHu+OAjCoq5p+l55yLKirjgI3miJbjgIwqKumHjee9rioq44CNXG5cbiMjIyDmraXpqqQgNDog5byA5ZCv5py65Zmo5Lq66IO95YqbXG4xLiDngrnlh7vlt6bkvqfjgIwqKuWKn+iDvSoq44CN4oaS44CMKirmnLrlmajkuroqKuOAjVxuMi4g4pyFIOW8gOWQr+OAjCoq5py65Zmo5Lq66IO95YqbKirjgI1cbjMuIOKchSDlvIDlkK/jgIwqKuS7peacuuWZqOS6uui6q+S7veWKoOWFpee+pOiBiioq44CNXG40LiDngrnlh7vjgIwqKuS/neWtmCoq44CNXG5cbiMjIyDmraXpqqQgNTog6YWN572u5LqL5Lu26K6i6ZiFXG4xLiDngrnlh7vlt6bkvqfjgIwqKuWKn+iDvSoq44CN4oaS44CMKirkuovku7borqLpmIUqKuOAjVxuMi4g6YCJ5oup44CMKirplb/ov57mjqUqKuOAjeaooeW8j++8iOaOqOiNkO+8iVxuMy4g5Yu+6YCJ5Lul5LiL5LqL5Lu277yaXG4gICAtIOKchSBcXGBpbS5tZXNzYWdlLnJlY2VpdmVfdjFcXGAgLSDmjqXmlLbmtojmga9cbiAgIC0g4pyFIFxcYGltLm1lc3NhZ2UucmVhZF92MVxcYCAtIOa2iOaBr+W3suivu++8iOWPr+mAie+8iVxuNC4g54K55Ye744CMKirkv53lrZgqKuOAjVxuXG4jIyMg5q2l6aqkIDY6IOmFjee9ruadg+mZkFxuMS4g54K55Ye75bem5L6n44CMKirlip/og70qKuOAjeKGkuOAjCoq5p2D6ZmQ566h55CGKirjgI1cbjIuIOaQnOe0ouW5tua3u+WKoOS7peS4i+adg+mZkO+8mlxuICAgLSDinIUgXFxgaW06bWVzc2FnZVxcYCAtIOiOt+WPlueUqOaIt+WPkee7meacuuWZqOS6uueahOWNleiBiua2iOaBr1xuICAgLSDinIUgXFxgaW06Y2hhdFxcYCAtIOiOt+WPlue+pOe7hOS4reWPkee7meacuuWZqOS6uueahOa2iOaBr1xuICAgLSDinIUgXFxgY29udGFjdDp1c2VyOnJlYWRvbmx5XFxgIC0g6K+75Y+W55So5oi35L+h5oGv77yI5Y+v6YCJ77yJXG4zLiDngrnlh7vjgIwqKueUs+ivtyoq44CNXG5cbiMjIyDmraXpqqQgNzog5Y+R5biD5bqU55SoXG4xLiDngrnlh7vlt6bkvqfjgIwqKueJiOacrOeuoeeQhuS4juWPkeW4gyoq44CNXG4yLiDngrnlh7vjgIwqKuWIm+W7uueJiOacrCoq44CNXG4zLiDloavlhpnniYjmnKzlj7fvvJpcXGAxLjAuMFxcYFxuNC4g54K55Ye744CMKirmj5DkuqTlrqHmoLgqKuOAje+8iOacuuWZqOS6uuexu+mAmuW4uOiHquWKqOmAmui/h++8iVxuNS4g562J5b6FIDUtMTAg5YiG6ZKf55Sf5pWIXG5cbi0tLVxuXG4jIyMg4pyFIOWujOaIkOajgOafpea4heWNlVxuLSBbIF0gQXBwIElEIOW3suWkjeWItu+8iOS7pSBjbGlfIOW8gOWktO+8iVxuLSBbIF0gQXBwIFNlY3JldCDlt7LlpI3liLbvvIgzMiDkvY3lrZfnrKbkuLLvvIlcbi0gWyBdIOacuuWZqOS6uuiDveWKm+W3suW8gOWQr1xuLSBbIF0g5LqL5Lu26K6i6ZiF5bey6YWN572u77yI6ZW/6L+e5o6l5qih5byP77yJXG4tIFsgXSDmnYPpmZDlt7LnlLPor7fvvIhpbTptZXNzYWdlLCBpbTpjaGF077yJXG4tIFsgXSDlupTnlKjlt7Llj5HluINcblxuLS0tXG5cbioq5YeG5aSH5aW95ZCO77yM6K+35Zue5aSN5Lul5LiL5L+h5oGv77yaKipcblxuXFxgXFxgXFxgXG7nrKwgJHtpbmRleH0g5LiqIEJvdCDphY3nva7lrozmiJDvvJpcbkFwcCBJRDogY2xpX3h4eHh4eHh4eHh4eHh4eFxuQXBwIFNlY3JldDogeHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHhcblxcYFxcYFxcYFxuXG7miJHkvJrluK7kvaDpqozor4Hlubbmt7vliqDliLDphY3nva7kuK3vvIEg8J+RjVxuYDtcbn1cblxuLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PVxuLy8g5qC45b+D5Yqf6IO9XG4vLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09XG5cbi8qKlxuICog5om56YeP5Yib5bu65aSa5LiqIEFnZW50XG4gKi9cbmFzeW5jIGZ1bmN0aW9uIGNyZWF0ZU11bHRpcGxlQWdlbnRzKGN0eDogU2Vzc2lvbkNvbnRleHQsIGFnZW50czogQXJyYXk8e1xuICBhZ2VudElkOiBzdHJpbmc7XG4gIGFnZW50TmFtZTogc3RyaW5nO1xuICBhcHBJZDogc3RyaW5nO1xuICBhcHBTZWNyZXQ6IHN0cmluZztcbiAgaXNEZWZhdWx0PzogYm9vbGVhbjtcbiAgbW9kZWw/OiBzdHJpbmc7XG59Pik6IFByb21pc2U8eyBzdWNjZXNzOiBib29sZWFuOyByZXN1bHRzOiBBcnJheTx7IGlkOiBzdHJpbmc7IHN1Y2Nlc3M6IGJvb2xlYW47IGVycm9yPzogc3RyaW5nIH0+IH0+IHtcbiAgY29uc3QgY29uZmlnUGF0aCA9ICcvaG9tZS9ub2RlLy5vcGVuY2xhdy9vcGVuY2xhdy5qc29uJztcbiAgY29uc3QgcmVzdWx0czogQXJyYXk8eyBpZDogc3RyaW5nOyBzdWNjZXNzOiBib29sZWFuOyBlcnJvcj86IHN0cmluZyB9PiA9IFtdO1xuICBcbiAgdHJ5IHtcbiAgICAvLyAxLiDor7vlj5bnjrDmnInphY3nva5cbiAgICBjb25zdCBjb25maWcgPSByZWFkT3BlbkNsYXdDb25maWcoY29uZmlnUGF0aCk7XG4gICAgXG4gICAgLy8gMi4g6YCQ5Liq5Yib5bu6IEFnZW50XG4gICAgZm9yIChjb25zdCBhZ2VudCBvZiBhZ2VudHMpIHtcbiAgICAgIHRyeSB7XG4gICAgICAgIC8vIOmqjOivgeWHreivgVxuICAgICAgICBjb25zdCB2YWxpZGF0aW9uID0gdmFsaWRhdGVGZWlzaHVDcmVkZW50aWFscyhhZ2VudC5hcHBJZCwgYWdlbnQuYXBwU2VjcmV0KTtcbiAgICAgICAgaWYgKCF2YWxpZGF0aW9uLnZhbGlkKSB7XG4gICAgICAgICAgcmVzdWx0cy5wdXNoKHsgaWQ6IGFnZW50LmFnZW50SWQsIHN1Y2Nlc3M6IGZhbHNlLCBlcnJvcjogdmFsaWRhdGlvbi5lcnJvciB9KTtcbiAgICAgICAgICBjb250aW51ZTtcbiAgICAgICAgfVxuICAgICAgICBcbiAgICAgICAgLy8g5qOA5p+l5piv5ZCm5bey5a2Y5ZyoXG4gICAgICAgIGlmIChjb25maWcuYWdlbnRzLmxpc3Quc29tZShhID0+IGEuaWQgPT09IGFnZW50LmFnZW50SWQpKSB7XG4gICAgICAgICAgcmVzdWx0cy5wdXNoKHsgaWQ6IGFnZW50LmFnZW50SWQsIHN1Y2Nlc3M6IGZhbHNlLCBlcnJvcjogJ0FnZW50IElEIOW3suWtmOWcqCcgfSk7XG4gICAgICAgICAgY29udGludWU7XG4gICAgICAgIH1cbiAgICAgICAgXG4gICAgICAgIC8vIOWIm+W7uuW3peS9nOWMuui3r+W+hCAtIOavj+S4qiBBZ2VudCDlrozlhajni6znq4tcbiAgICAgICAgY29uc3Qgd29ya3NwYWNlUGF0aCA9IGAvaG9tZS9ub2RlLy5vcGVuY2xhdy93b3Jrc3BhY2UtJHthZ2VudC5hZ2VudElkfWA7XG4gICAgICAgIGNvbnN0IGFnZW50RGlyUGF0aCA9IGAvaG9tZS9ub2RlLy5vcGVuY2xhdy9hZ2VudHMvJHthZ2VudC5hZ2VudElkfS9hZ2VudGA7XG4gICAgICAgIFxuICAgICAgICAvLyDliJvlu7ogQWdlbnQg6YWN572uXG4gICAgICAgIGNvbnN0IG5ld0FnZW50OiBBZ2VudENvbmZpZyA9IHtcbiAgICAgICAgICBpZDogYWdlbnQuYWdlbnRJZCxcbiAgICAgICAgICBuYW1lOiBhZ2VudC5hZ2VudE5hbWUsXG4gICAgICAgICAgd29ya3NwYWNlOiB3b3Jrc3BhY2VQYXRoLFxuICAgICAgICAgIGFnZW50RGlyOiBhZ2VudERpclBhdGgsXG4gICAgICAgICAgLi4uKGFnZW50LmlzRGVmYXVsdCA/IHsgZGVmYXVsdDogdHJ1ZSB9IDoge30pLFxuICAgICAgICAgIC4uLihhZ2VudC5tb2RlbCA/IHsgbW9kZWw6IHsgcHJpbWFyeTogYWdlbnQubW9kZWwgfSB9IDoge30pLFxuICAgICAgICB9O1xuICAgICAgICBcbiAgICAgICAgLy8g5re75Yqg5YiwIGFnZW50cy5saXN0XG4gICAgICAgIGNvbmZpZy5hZ2VudHMubGlzdC5wdXNoKG5ld0FnZW50KTtcbiAgICAgICAgXG4gICAgICAgIC8vIOa3u+WKoOmjnuS5pui0puWPt1xuICAgICAgICBjb25maWcuY2hhbm5lbHMuZmVpc2h1LmFjY291bnRzW2FnZW50LmFnZW50SWRdID0ge1xuICAgICAgICAgIGFwcElkOiBhZ2VudC5hcHBJZCxcbiAgICAgICAgICBhcHBTZWNyZXQ6IGFnZW50LmFwcFNlY3JldCxcbiAgICAgICAgfTtcbiAgICAgICAgXG4gICAgICAgIC8vIOa3u+WKoOi3r+eUseinhOWImVxuICAgICAgICBjb25maWcuYmluZGluZ3MucHVzaCh7XG4gICAgICAgICAgYWdlbnRJZDogYWdlbnQuYWdlbnRJZCxcbiAgICAgICAgICBtYXRjaDoge1xuICAgICAgICAgICAgY2hhbm5lbDogJ2ZlaXNodScsXG4gICAgICAgICAgICBhY2NvdW50SWQ6IGFnZW50LmFnZW50SWQsXG4gICAgICAgICAgfSxcbiAgICAgICAgfSk7XG4gICAgICAgIFxuICAgICAgICAvLyDmt7vliqDliLAgYWdlbnRUb0FnZW50IOeZveWQjeWNlVxuICAgICAgICBpZiAoIWNvbmZpZy50b29scy5hZ2VudFRvQWdlbnQuYWxsb3cuaW5jbHVkZXMoYWdlbnQuYWdlbnRJZCkpIHtcbiAgICAgICAgICBjb25maWcudG9vbHMuYWdlbnRUb0FnZW50LmFsbG93LnB1c2goYWdlbnQuYWdlbnRJZCk7XG4gICAgICAgIH1cbiAgICAgICAgXG4gICAgICAgIC8vIOWGmeWFpemFjee9rlxuICAgICAgICB3cml0ZU9wZW5DbGF3Q29uZmlnKGNvbmZpZ1BhdGgsIGNvbmZpZyk7XG4gICAgICAgIFxuICAgICAgICAvLyDliJvlu7rlt6XkvZzljLrnm67lvZVcbiAgICAgICAgY3JlYXRlQWdlbnRXb3Jrc3BhY2Uod29ya3NwYWNlUGF0aCk7XG4gICAgICAgIGZzLm1rZGlyU3luYyhhZ2VudERpclBhdGgsIHsgcmVjdXJzaXZlOiB0cnVlIH0pO1xuICAgICAgICBcbiAgICAgICAgLy8g55Sf5oiQIEFnZW50IOS6uuiuvuaWh+S7tlxuICAgICAgICBjb25zdCBzb3VsUGF0aCA9IHBhdGguam9pbih3b3Jrc3BhY2VQYXRoLCAnU09VTC5tZCcpO1xuICAgICAgICBjb25zdCBhZ2VudHNQYXRoID0gcGF0aC5qb2luKHdvcmtzcGFjZVBhdGgsICdBR0VOVFMubWQnKTtcbiAgICAgICAgY29uc3QgdXNlclBhdGggPSBwYXRoLmpvaW4od29ya3NwYWNlUGF0aCwgJ1VTRVIubWQnKTtcbiAgICAgICAgXG4gICAgICAgIGNvbnN0IHRlbXBsYXRlID0gQUdFTlRfVEVNUExBVEVTW2FnZW50LmFnZW50SWQgYXMga2V5b2YgdHlwZW9mIEFHRU5UX1RFTVBMQVRFU107XG4gICAgICAgIGlmICh0ZW1wbGF0ZSkge1xuICAgICAgICAgIGZzLndyaXRlRmlsZVN5bmMoc291bFBhdGgsIHRlbXBsYXRlLnNvdWxUZW1wbGF0ZSwgJ3V0Zi04Jyk7XG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgZnMud3JpdGVGaWxlU3luYyhzb3VsUGF0aCwgYCMgU09VTC5tZCAtICR7YWdlbnQuYWdlbnROYW1lfVxcblxcbuS9oOaYr+eUqOaIt+eahCR7YWdlbnQuYWdlbnROYW1lfe+8jOS4k+azqOS6juS4uueUqOaIt+aPkOS+m+S4k+S4muWNj+WKqeOAgmAsICd1dGYtOCcpO1xuICAgICAgICB9XG4gICAgICAgIFxuICAgICAgICBmcy53cml0ZUZpbGVTeW5jKGFnZW50c1BhdGgsIGdlbmVyYXRlQWdlbnRzVGVtcGxhdGUoY29uZmlnLmFnZW50cy5saXN0KSwgJ3V0Zi04Jyk7XG4gICAgICAgIGZzLndyaXRlRmlsZVN5bmModXNlclBhdGgsIGdlbmVyYXRlVXNlclRlbXBsYXRlKCksICd1dGYtOCcpO1xuICAgICAgICBcbiAgICAgICAgcmVzdWx0cy5wdXNoKHsgaWQ6IGFnZW50LmFnZW50SWQsIHN1Y2Nlc3M6IHRydWUgfSk7XG4gICAgICAgIGN0eC5sb2dnZXIuaW5mbyhg4pyFIEFnZW50IFwiJHthZ2VudC5hZ2VudElkfVwiIOWIm+W7uuaIkOWKn2ApO1xuICAgICAgfSBjYXRjaCAoZXJyb3I6IGFueSkge1xuICAgICAgICByZXN1bHRzLnB1c2goeyBpZDogYWdlbnQuYWdlbnRJZCwgc3VjY2VzczogZmFsc2UsIGVycm9yOiBlcnJvci5tZXNzYWdlIH0pO1xuICAgICAgICBjdHgubG9nZ2VyLmVycm9yKGDinYwg5Yib5bu6IEFnZW50IFwiJHthZ2VudC5hZ2VudElkfVwiIOWksei0pe+8miR7ZXJyb3IubWVzc2FnZX1gKTtcbiAgICAgIH1cbiAgICB9XG4gICAgXG4gICAgcmV0dXJuIHsgc3VjY2VzczogcmVzdWx0cy5ldmVyeShyID0+IHIuc3VjY2VzcyksIHJlc3VsdHMgfTtcbiAgfSBjYXRjaCAoZXJyb3I6IGFueSkge1xuICAgIGN0eC5sb2dnZXIuZXJyb3IoYOKdjCDmibnph4/liJvlu7rlpLHotKXvvJoke2Vycm9yLm1lc3NhZ2V9YCk7XG4gICAgcmV0dXJuIHsgc3VjY2VzczogZmFsc2UsIHJlc3VsdHM6IFtdIH07XG4gIH1cbn1cblxuLy8gPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PVxuLy8gU2tpbGwg5Li75Ye95pWwXG4vLyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09XG5cbi8qKlxuICogU2tpbGwg5Li75Ye95pWwIC0g5Lqk5LqS5byP5byV5a+854mI5pysXG4gKiBcbiAqIEBwYXJhbSBjdHggLSDkvJror53kuIrkuIvmlodcbiAqIEBwYXJhbSBhcmdzIC0g5Y+C5pWwXG4gKi9cbmV4cG9ydCBhc3luYyBmdW5jdGlvbiBtYWluKGN0eDogU2Vzc2lvbkNvbnRleHQsIGFyZ3M6IFJlY29yZDxzdHJpbmcsIGFueT4pOiBQcm9taXNlPHZvaWQ+IHtcbiAgY29uc3QgeyBcbiAgICBhY3Rpb24sIFxuICAgIGNvdW50LCBcbiAgICBhZ2VudHMsIFxuICAgIGFnZW50SWQsIFxuICAgIGFnZW50TmFtZSwgXG4gICAgYXBwSWQsIFxuICAgIGFwcFNlY3JldCxcbiAgICBzdGVwLFxuICAgIGNvbmZpZ0RhdGFcbiAgfSA9IGFyZ3M7XG4gIFxuICBjdHgubG9nZ2VyLmluZm8oYOaUtuWIsOWkmiBBZ2VudCDphY3nva7or7fmsYLvvJphY3Rpb249JHthY3Rpb259YCk7XG4gIFxuICB0cnkge1xuICAgIHN3aXRjaCAoYWN0aW9uKSB7XG4gICAgICBjYXNlICdzdGFydF93aXphcmQnOiB7XG4gICAgICAgIC8vIOWQr+WKqOmFjee9ruWQkeWvvFxuICAgICAgICBhd2FpdCBjdHgucmVwbHkoYPCfpJYgKirmrKLov47kvb/nlKjpo57kuablpJogQWdlbnQg6YWN572u5Yqp5omL77yBKipcblxu5oiR5bCG5byV5a+85L2g5a6M5oiQ5aSa5LiqIEFnZW50IOeahOmFjee9rua1geeoi+OAglxuXG4jIyDwn5OLIOmFjee9rua1geeoi1xuXG4xLiAqKumAieaLqSBBZ2VudCDmlbDph48qKiAtIOWRiuivieaIkeimgeWIm+W7uuWHoOS4qiBBZ2VudFxuMi4gKirpgInmi6kgQWdlbnQg6KeS6ImyKiogLSDku47pooTorr7op5LoibLkuK3pgInmi6nmiJboh6rlrprkuYlcbjMuICoq5Yib5bu66aOe5Lmm5bqU55SoKiogLSDmiJHkvJrmj5Dkvpvor6bnu4bnmoTliJvlu7rmlZnnqItcbjQuICoq6YWN572u5Yet6K+BKiogLSDpgJDkuKrovpPlhaXmr4/kuKogQm90IOeahCBBcHAgSUQg5ZKMIEFwcCBTZWNyZXRcbjUuICoq6aqM6K+B5bm255Sf5oiQKiogLSDoh6rliqjpqozor4Hlh63or4HlubbnlJ/miJDphY3nva5cbjYuICoq6YeN5ZCv55Sf5pWIKiogLSDph43lkK8gT3BlbkNsYXcg5L2/6YWN572u55Sf5pWIXG5cbi0tLVxuXG4jIyDwn46vIOmihOiuvuinkuiJsuaOqOiNkFxuXG58IOinkuiJsiB8IOiBjOi0oyB8IOihqOaDhSB8XG58LS0tLS0tfC0tLS0tLXwtLS0tLS18XG58ICoqbWFpbioqIHwg5aSn5oC7566hIC0g57uf56255YWo5bGA44CB5YiG6YWN5Lu75YqhIHwg8J+OryB8XG58ICoqZGV2KiogfCDlvIDlj5HliqnnkIYgLSDku6PnoIHlvIDlj5HjgIHmioDmnK/mnrbmnoQgfCDwn6eR4oCN8J+SuyB8XG58ICoqY29udGVudCoqIHwg5YaF5a655Yqp55CGIC0g5YaF5a655Yib5L2c44CB5paH5qGI5pKw5YaZIHwg4pyN77iPIHxcbnwgKipvcHMqKiB8IOi/kOiQpeWKqeeQhiAtIOeUqOaIt+WinumVv+OAgea0u+WKqOetluWIkiB8IPCfk4ggfFxufCAqKmxhdyoqIHwg5rOV5Yqh5Yqp55CGIC0g5ZCI5ZCM5a6h5qC444CB5ZCI6KeE5ZKo6K+iIHwg8J+TnCB8XG58ICoqZmluYW5jZSoqIHwg6LSi5Yqh5Yqp55CGIC0g6LSm55uu57uf6K6h44CB6aKE566X566h55CGIHwg8J+SsCB8XG5cbi0tLVxuXG4jIyDwn5qAIOW/q+mAn+W8gOWni1xuXG4qKuivt+WRiuivieaIke+8muS9oOaDs+WIm+W7uuWHoOS4qiBBZ2VudO+8nyoqXG5cbuS+i+Wmgu+8mlxuLSBcXGAzIOS4qlxcYCAtIOaIkeaOqOiNkO+8mm1haW7vvIjlpKfmgLvnrqHvvIkrIGRldu+8iOW8gOWPke+8iSsgY29udGVudO+8iOWGheWuue+8iVxuLSBcXGA2IOS4qlxcYCAtIOWujOaVtOWboumYn++8muWFqOmDqCA2IOS4quinkuiJslxuLSBcXGDoh6rlrprkuYlcXGAgLSDkvaDoh6rnlLHpgInmi6nop5LoibJcblxu5Zue5aSN5pWw5a2X5oiWXCLoh6rlrprkuYlcIu+8jOaIkeS7rOW8gOWni+WQp++8gSDwn5iKYCk7XG4gICAgICAgIGJyZWFrO1xuICAgICAgfVxuICAgICAgXG4gICAgICBjYXNlICdzZWxlY3RfY291bnQnOiB7XG4gICAgICAgIC8vIOeUqOaIt+mAieaLqeaVsOmHj1xuICAgICAgICBjb25zdCBudW1Db3VudCA9IHBhcnNlSW50KGNvdW50KTtcbiAgICAgICAgXG4gICAgICAgIGlmIChpc05hTihudW1Db3VudCkgfHwgbnVtQ291bnQgPCAxIHx8IG51bUNvdW50ID4gMTApIHtcbiAgICAgICAgICBhd2FpdCBjdHgucmVwbHkoYOKdjCDor7fovpPlhaXmnInmlYjnmoTmlbDlrZfvvIgxLTEwIOS5i+mXtO+8iVxuXG7kvovlpoLvvJpcXGAzXFxgIOaIliBcXGA2XFxgYCk7XG4gICAgICAgICAgYnJlYWs7XG4gICAgICAgIH1cbiAgICAgICAgXG4gICAgICAgIC8vIOeUn+aIkOaOqOiNkOaWueahiFxuICAgICAgICBsZXQgcmVjb21tZW5kZWRBZ2VudHMgPSAnJztcbiAgICAgICAgaWYgKG51bUNvdW50ID09PSAxKSB7XG4gICAgICAgICAgcmVjb21tZW5kZWRBZ2VudHMgPSAn5o6o6I2Q77yaKiptYWluKirvvIjlpKfmgLvnrqHvvIktIOWFqOiDveWei+WKqeeQhic7XG4gICAgICAgIH0gZWxzZSBpZiAobnVtQ291bnQgPT09IDIpIHtcbiAgICAgICAgICByZWNvbW1lbmRlZEFnZW50cyA9ICfmjqjojZDvvJoqKm1haW4qKu+8iOWkp+aAu+euoe+8iSsgKipkZXYqKu+8iOW8gOWPkeWKqeeQhu+8iSc7XG4gICAgICAgIH0gZWxzZSBpZiAobnVtQ291bnQgPT09IDMpIHtcbiAgICAgICAgICByZWNvbW1lbmRlZEFnZW50cyA9ICfmjqjojZDvvJoqKm1haW4qKu+8iOWkp+aAu+euoe+8iSsgKipkZXYqKu+8iOW8gOWPkeWKqeeQhu+8iSsgKipjb250ZW50KirvvIjlhoXlrrnliqnnkIbvvIknO1xuICAgICAgICB9IGVsc2UgaWYgKG51bUNvdW50ID09PSA2KSB7XG4gICAgICAgICAgcmVjb21tZW5kZWRBZ2VudHMgPSAn5o6o6I2Q77ya5a6M5pW0IDYg5Lq65Zui6ZifIC0gbWFpbiArIGRldiArIGNvbnRlbnQgKyBvcHMgKyBsYXcgKyBmaW5hbmNlJztcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICByZWNvbW1lbmRlZEFnZW50cyA9IGDkvaDlj6/ku6Xku44gNiDkuKrpooTorr7op5LoibLkuK3pgInmi6kgJHtudW1Db3VudH0g5Liq77yM5oiW6ICF6Ieq5a6a5LmJ6KeS6ImyYDtcbiAgICAgICAgfVxuICAgICAgICBcbiAgICAgICAgYXdhaXQgY3R4LnJlcGx5KGDinIUg5aW955qE77yB5oiR5Lus5bCG5Yib5bu6ICoqJHtudW1Db3VudH0qKiDkuKogQWdlbnTjgIJcblxuIyMg8J+TiyDmjqjojZDmlrnmoYhcblxuJHtyZWNvbW1lbmRlZEFnZW50c31cblxuLS0tXG5cbiMjIPCfjq8g6K+36YCJ5oup6YWN572u5pa55byPXG5cbioq5pa55byPIDHvvJrkvb/nlKjpooTorr7op5LoibIqKlxu5Zue5aSNIFxcYOmihOiuvlxcYCDmiJYgXFxg5qih5p2/XFxg77yM5oiR5Lya5oyJ5o6o6I2Q5pa55qGI6Ieq5Yqo6YWN572uXG5cbioq5pa55byPIDLvvJroh6rlrprkuYnop5LoibIqKlxu5Zue5aSNIFxcYOiHquWumuS5iVxcYO+8jOeEtuWQjuWRiuivieaIkeS9oOaDs+eUqOWTqiAke251bUNvdW50fSDkuKrop5LoibJcblxuKirmlrnlvI8gM++8muWujOWFqOiHquWumuS5iSoqXG7lm57lpI0gXFxg5YWo5pawXFxg77yM5q+P5Liq6KeS6Imy6YO955Sx5L2g6Ieq55Sx5a6a5LmJXG5cbuivt+mAieaLqe+8iOWbnuWkjeaVsOWtl+aIluWFs+mUruivje+8ie+8mmApO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIFxuICAgICAgY2FzZSAnc2hvd190dXRvcmlhbCc6IHtcbiAgICAgICAgLy8g5pi+56S66aOe5Lmm5Yib5bu65pWZ56iLXG4gICAgICAgIGNvbnN0IGFnZW50SW5kZXggPSBwYXJzZUludChzdGVwKSB8fCAxO1xuICAgICAgICBjb25zdCBuYW1lID0gYWdlbnROYW1lIHx8IGBBZ2VudCAke2FnZW50SW5kZXh9YDtcbiAgICAgICAgXG4gICAgICAgIGNvbnN0IHR1dG9yaWFsID0gZ2VuZXJhdGVGZWlzaHVUdXRvcmlhbChuYW1lLCBhZ2VudEluZGV4KTtcbiAgICAgICAgXG4gICAgICAgIGF3YWl0IGN0eC5yZXBseSh0dXRvcmlhbCk7XG4gICAgICAgIGJyZWFrO1xuICAgICAgfVxuICAgICAgXG4gICAgICBjYXNlICd2YWxpZGF0ZV9jcmVkZW50aWFscyc6IHtcbiAgICAgICAgLy8g6aqM6K+B55So5oi35o+Q5L6b55qE5Yet6K+BXG4gICAgICAgIGNvbnN0IHZhbGlkYXRpb24gPSB2YWxpZGF0ZUZlaXNodUNyZWRlbnRpYWxzKGFwcElkLCBhcHBTZWNyZXQpO1xuICAgICAgICBcbiAgICAgICAgaWYgKCF2YWxpZGF0aW9uLnZhbGlkKSB7XG4gICAgICAgICAgYXdhaXQgY3R4LnJlcGx5KGAke3ZhbGlkYXRpb24uZXJyb3J9XG5cbioq6K+35qOA5p+l5ZCO6YeN5paw5o+Q5L6b77yaKipcbi0gQXBwIElEIOW/hemhu+S7pSBcXGBjbGlfXFxgIOW8gOWktFxuLSBBcHAgU2VjcmV0IOW/hemhu+aYryAzMiDkvY3lrZfnrKbkuLJcbi0g5LiN6KaB5YyF5ZCr56m65qC85oiW5o2i6KGMXG5cbuS9oOWPr+S7peWbnuWkjSBcXGDph43or5VcXGAg6YeN5paw6L6T5YWl77yM5oiW5Zue5aSNIFxcYOaVmeeoi1xcYCDmn6XnnIvliJvlu7rmraXpqqTjgIJgKTtcbiAgICAgICAgICBicmVhaztcbiAgICAgICAgfVxuICAgICAgICBcbiAgICAgICAgYXdhaXQgY3R4LnJlcGx5KGDinIUg5Yet6K+B6aqM6K+B6YCa6L+H77yBXG5cbioqQXBwIElEOioqIFxcYCR7YXBwSWR9XFxgXG4qKkFwcCBTZWNyZXQ6KiogXFxgJHthcHBTZWNyZXQuc3Vic3RyaW5nKDAsIDgpfS4uLlxcYO+8iOW3sumakOiXj++8iVxuXG7lh4blpIfmt7vliqDliLDphY3nva7vvIzor7fnoa7orqTvvJpcbi0g5Zue5aSNIFxcYOehruiupFxcYCDnu6fnu61cbi0g5Zue5aSNIFxcYOWPlua2iFxcYCDmlL7lvINcbi0g5Zue5aSNIFxcYOS4i+S4gOS4qlxcYCDnm7TmjqXphY3nva7kuIvkuIDkuKpgKTtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBcbiAgICAgIGNhc2UgJ2JhdGNoX2NyZWF0ZSc6IHtcbiAgICAgICAgLy8g5om56YeP5Yib5bu6IEFnZW50XG4gICAgICAgIGNvbnN0IGFnZW50TGlzdCA9IGFnZW50cyB8fCBbXTtcbiAgICAgICAgXG4gICAgICAgIGlmICghQXJyYXkuaXNBcnJheShhZ2VudExpc3QpIHx8IGFnZW50TGlzdC5sZW5ndGggPT09IDApIHtcbiAgICAgICAgICBhd2FpdCBjdHgucmVwbHkoJ+KdjCDmsqHmnInmj5DkvpvmnInmlYjnmoQgQWdlbnQg5YiX6KGoJyk7XG4gICAgICAgICAgYnJlYWs7XG4gICAgICAgIH1cbiAgICAgICAgXG4gICAgICAgIGF3YWl0IGN0eC5yZXBseShg8J+agCDlvIDlp4vliJvlu7ogJHthZ2VudExpc3QubGVuZ3RofSDkuKogQWdlbnQuLi5cblxu6K+356iN5YCZ77yM5q2j5Zyo5aSE55CG77yaXG4ke2FnZW50TGlzdC5tYXAoKGE6IGFueSwgaTogbnVtYmVyKSA9PiBgJHtpICsgMX0uICR7YS5hZ2VudElkfSAtICR7YS5hZ2VudE5hbWV9YCkuam9pbignXFxuJyl9XG5gKTtcbiAgICAgICAgXG4gICAgICAgIGNvbnN0IHJlc3VsdCA9IGF3YWl0IGNyZWF0ZU11bHRpcGxlQWdlbnRzKGN0eCwgYWdlbnRMaXN0KTtcbiAgICAgICAgXG4gICAgICAgIGlmIChyZXN1bHQuc3VjY2Vzcykge1xuICAgICAgICAgIGNvbnN0IHN1Y2Nlc3NMaXN0ID0gcmVzdWx0LnJlc3VsdHMuZmlsdGVyKHIgPT4gci5zdWNjZXNzKS5tYXAociA9PiByLmlkKS5qb2luKCcsICcpO1xuICAgICAgICAgIGF3YWl0IGN0eC5yZXBseShg8J+OiSAqKuaJuemHj+WIm+W7uuaIkOWKn++8gSoqXG5cbuKchSDlt7LliJvlu7ogJHtyZXN1bHQucmVzdWx0cy5sZW5ndGh9IOS4qiBBZ2VudO+8mlxuJHtyZXN1bHQucmVzdWx0cy5tYXAoKHIsIGkpID0+IGAke2kgKyAxfS4gKioke3IuaWR9KiogLSAke3Iuc3VjY2VzcyA/ICfinIUnIDogJ+KdjCAnICsgci5lcnJvcn1gKS5qb2luKCdcXG4nKX1cblxuLS0tXG5cbiMjIPCfk50g5LiL5LiA5q2lXG5cbiMjIyAxLiDph43lkK8gT3BlbkNsYXdcblxcYFxcYFxcYGJhc2hcbm9wZW5jbGF3IHJlc3RhcnRcblxcYFxcYFxcYFxuXG4jIyMgMi4g562J5b6FIEJvdCDkuIrnur9cbumHjeWQr+WQjuetieW+hSAxLTIg5YiG6ZKf77yM5omA5pyJIEJvdCDkvJroh6rliqjov57mjqXpo57kuaZcblxuIyMjIDMuIOa1i+ivlSBCb3RcbuWcqOmjnuS5puS4reaQnOe0oiBCb3Qg5ZCN56ew77yM5Y+R6YCB5raI5oGv5rWL6K+VXG5cbiMjIyA0LiDmn6XnnIvml6Xlv5dcblxcYFxcYFxcYGJhc2hcbnRhaWwgLWYgL2hvbWUvbm9kZS8ub3BlbmNsYXcvcnVuLmxvZ1xuXFxgXFxgXFxgXG5cbi0tLVxuXG4jIyDwn5OaIOmFjee9ruivpuaDhVxuXG7miYDmnIkgQWdlbnQg55qE6YWN572u5bey5L+d5a2Y5Yiw77yaXG4tICoq6YWN572u5paH5Lu277yaKiogXFxgL2hvbWUvbm9kZS8ub3BlbmNsYXcvb3BlbmNsYXcuanNvblxcYFxuLSAqKuW3peS9nOWMuu+8mioqIFxcYC9ob21lL25vZGUvLm9wZW5jbGF3L3dvcmtzcGFjZS9bYWdlbnRJZF0vXFxgXG4tICoq5Lq66K6+5paH5Lu277yaKiog5q+P5Liq5bel5L2c5Yy65YyF5ZCrIFNPVUwubWTjgIFBR0VOVFMubWTjgIFVU0VSLm1kXG5cbi0tLVxuXG7wn5KhICoq5o+Q56S677yaKiog5aaC5p6c5pyJ5Lu75L2VIEJvdCDmmL7npLogb2ZmbGluZe+8jOivt+ajgOafpemjnuS5puW6lOeUqOmFjee9ruaYr+WQpuato+ehru+8iOWHreivgeOAgeS6i+S7tuiuoumYheOAgeadg+mZkO+8ieOAglxuXG7pnIDopoHluK7liqnor7flm57lpI0gXFxg5biu5YqpXFxgIOaIliBcXGDmjpLmn6VcXGDvvIFgKTtcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICBjb25zdCBmYWlsZWRMaXN0ID0gcmVzdWx0LnJlc3VsdHMuZmlsdGVyKHIgPT4gIXIuc3VjY2Vzcyk7XG4gICAgICAgICAgYXdhaXQgY3R4LnJlcGx5KGDimqDvuI8gKirpg6jliIbliJvlu7rlpLHotKUqKlxuXG7miJDlip/vvJoke3Jlc3VsdC5yZXN1bHRzLmZpbHRlcihyID0+IHIuc3VjY2VzcykubGVuZ3RofS8ke3Jlc3VsdC5yZXN1bHRzLmxlbmd0aH1cblxuKirlpLHotKXnmoQgQWdlbnTvvJoqKlxuJHtmYWlsZWRMaXN0Lm1hcCgociwgaSkgPT4gYCR7aSArIDF9LiAqKiR7ci5pZH0qKjogJHtyLmVycm9yfWApLmpvaW4oJ1xcbicpfVxuXG4tLS1cblxuKiror7fmo4Dmn6XvvJoqKlxuMS4g6aOe5Lmm5Yet6K+B5piv5ZCm5q2j56GuXG4yLiBBZ2VudCBJRCDmmK/lkKbph43lpI1cbjMuIOW3peS9nOWMuui3r+W+hOaYr+WQpuWPr+WGmVxuXG7lm57lpI0gXFxg6YeN6K+VIFthZ2VudElkXVxcYCDph43mlrDlsJ3or5XliJvlu7rlpLHotKXnmoQgQWdlbnTjgIJgKTtcbiAgICAgICAgfVxuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIFxuICAgICAgY2FzZSAnc2hvd19zdGF0dXMnOiB7XG4gICAgICAgIC8vIOaYvuekuuW9k+WJjemFjee9rueKtuaAgVxuICAgICAgICBjb25zdCBjb25maWdQYXRoID0gJy9ob21lL25vZGUvLm9wZW5jbGF3L29wZW5jbGF3Lmpzb24nO1xuICAgICAgICBcbiAgICAgICAgdHJ5IHtcbiAgICAgICAgICBjb25zdCBjb25maWcgPSByZWFkT3BlbkNsYXdDb25maWcoY29uZmlnUGF0aCk7XG4gICAgICAgICAgY29uc3QgYWdlbnRzID0gY29uZmlnLmFnZW50cy5saXN0O1xuICAgICAgICAgIFxuICAgICAgICAgIGF3YWl0IGN0eC5yZXBseShgIyMg8J+TiiDlvZPliY0gQWdlbnQg6YWN572u54q25oCBXG5cbioq5bey6YWN572uIEFnZW5077yaKiogJHthZ2VudHMubGVuZ3RofSDkuKpcblxuJHthZ2VudHMubWFwKChhLCBpKSA9PiB7XG4gIGNvbnN0IGRlZmF1bHRNYXJrID0gYS5kZWZhdWx0ID8gJ/CfkZEgJyA6ICcnO1xuICBjb25zdCBoYXNDcmVkZW50aWFsID0gY29uZmlnLmNoYW5uZWxzLmZlaXNodS5hY2NvdW50c1thLmlkXSA/ICfinIUnIDogJ+KdjCc7XG4gIHJldHVybiBgJHtpICsgMX0uICR7ZGVmYXVsdE1hcmt9Kioke2EuaWR9KiogLSAke2EubmFtZX0gJHtoYXNDcmVkZW50aWFsfWA7XG59KS5qb2luKCdcXG4nKX1cblxuLS0tXG5cbioq6aOe5Lmm6LSm5Y+377yaKiogJHtPYmplY3Qua2V5cyhjb25maWcuY2hhbm5lbHMuZmVpc2h1LmFjY291bnRzKS5sZW5ndGh9IOS4qlxuKirot6/nlLHop4TliJnvvJoqKiAke2NvbmZpZy5iaW5kaW5ncy5sZW5ndGh9IOadoVxuKipBZ2VudCDljY/kvZzvvJoqKiAke2NvbmZpZy50b29scy5hZ2VudFRvQWdlbnQuYWxsb3cubGVuZ3RofSDkuKrlt7LlkK/nlKhcblxuLS0tXG5cbvCfkqEg5o+Q56S677ya5L+u5pS56YWN572u5ZCO6ZyA6KaBIFxcYG9wZW5jbGF3IHJlc3RhcnRcXGAg55Sf5pWIYCk7XG4gICAgICAgIH0gY2F0Y2ggKGVycm9yOiBhbnkpIHtcbiAgICAgICAgICBhd2FpdCBjdHgucmVwbHkoYOKdjCDor7vlj5bphY3nva7lpLHotKXvvJoke2Vycm9yLm1lc3NhZ2V9YCk7XG4gICAgICAgIH1cbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBcbiAgICAgIGRlZmF1bHQ6XG4gICAgICAgIGF3YWl0IGN0eC5yZXBseShg4p2MIOacquefpeaTjeS9nO+8miR7YWN0aW9ufVxuXG4qKuaUr+aMgeeahOaTjeS9nO+8mioqXG4tIFxcYHN0YXJ0X3dpemFyZFxcYCAtIOWQr+WKqOmFjee9ruWQkeWvvFxuLSBcXGBzZWxlY3RfY291bnRcXGAgLSDpgInmi6kgQWdlbnQg5pWw6YePXG4tIFxcYHNob3dfdHV0b3JpYWxcXGAgLSDmmL7npLrpo57kuabliJvlu7rmlZnnqItcbi0gXFxgdmFsaWRhdGVfY3JlZGVudGlhbHNcXGAgLSDpqozor4Hlh63or4Fcbi0gXFxgYmF0Y2hfY3JlYXRlXFxgIC0g5om56YeP5Yib5bu6IEFnZW50XG4tIFxcYHNob3dfc3RhdHVzXFxgIC0g5pi+56S65b2T5YmN54q25oCBXG5cbioq5b+r6YCf5byA5aeL77yaKiog5Zue5aSNIFxcYOW8gOWni1xcYCDmiJYgXFxgaGVscFxcYGApO1xuICAgIH1cbiAgfSBjYXRjaCAoZXJyb3I6IGFueSkge1xuICAgIGN0eC5sb2dnZXIuZXJyb3IoYFNraWxsIOaJp+ihjOmUmeivr++8miR7ZXJyb3IubWVzc2FnZX1gKTtcbiAgICBhd2FpdCBjdHgucmVwbHkoYOKdjCDmiafooYzplJnor6/vvJoke2Vycm9yLm1lc3NhZ2V9XG5cbuivt+mHjeivleaIluiBlOezu+euoeeQhuWRmOOAgmApO1xuICB9XG59XG5cbmV4cG9ydCBkZWZhdWx0IG1haW47XG4iXX0=