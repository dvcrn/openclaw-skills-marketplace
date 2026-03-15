/**
 * 列出消息
 */
export declare function listMessages(params: {
    container_id_type: 'chat';
    container_id: string;
    page_token?: string;
    page_size?: number;
}): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 撤回消息 (实际上是删除自己发送的消息)
 */
export declare function recallMessage(messageId: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 更新消息内容 (仅支持消息卡片 patch)
 */
export declare function updateMessage(messageId: string, content: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * Pin 消息
 */
export declare function pinMessage(messageId: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 移除 Pin 消息
 */
export declare function unpinMessage(messageId: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 表情反应
 */
export declare function react(messageId: string, emoji: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 发送附件（图片或文件）
 * @param receiveId - 接收人/群 ID
 * @param receiveIdType - 接收人 ID 类型 (open_id, user_id, chat_id)
 * @param filePath - 文件本地路径
 * @param fileName - 文件名（可选）
 */
export declare function sendAttachment(receiveId: string, receiveIdType: 'open_id' | 'user_id' | 'chat_id', filePath: string, fileName?: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any> | {
    ok: boolean;
    error: any;
}>;
/**
 * 话题回复
 */
export declare function replyInThread(messageId: string, content: string, replyInThread?: boolean, msgType?: 'text' | 'post' | 'interactive'): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 获取话题消息
 */
export declare function listThreadMessages(chatId: string, threadId: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 获取群聊信息
 * @param chatId - 群聊 ID
 */
export declare function getChatInfo(chatId: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 获取群聊列表
 */
export declare function listChats(pageToken?: string, pageSize?: number): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 获取群成员列表
 */
export declare function getChatMembers(chatId: string, memberIdType?: 'user_id' | 'union_id' | 'open_id', pageToken?: string, pageSize?: number): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 判断用户是否在群里
 */
export declare function isInChat(chatId: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 创建群聊
 */
export declare function createChat(params: {
    name?: string;
    description?: string;
    user_id_list?: string[];
    bot_id_list?: string[];
    chat_type?: 'private' | 'public';
}): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 拉人进群
 */
export declare function addChatMembers(chatId: string, idList: string[], memberIdType?: 'user_id' | 'union_id' | 'open_id'): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 踢人出群
 */
export declare function removeChatMembers(chatId: string, idList: string[], memberIdType?: 'user_id' | 'union_id' | 'open_id'): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
