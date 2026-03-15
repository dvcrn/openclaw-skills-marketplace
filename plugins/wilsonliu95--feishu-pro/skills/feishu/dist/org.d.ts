/**
 * 获取用户信息
 */
export declare function getUser(userId: string, userIdType?: 'user_id' | 'union_id' | 'open_id'): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 获取部门信息
 */
export declare function getDepartment(departmentId: string, userIdType?: 'user_id' | 'union_id' | 'open_id'): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 列出部门下的用户
 */
export declare function listDepartmentUsers(departmentId: string, pageToken?: string, pageSize?: number): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 获取用户组信息
 */
export declare function getGroup(groupId: string, userIdType?: 'user_id' | 'union_id' | 'open_id'): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 列出日历
 */
export declare function listCalendars(pageToken?: string, pageSize?: number): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 创建日程
 */
export declare function createCalendarEvent(calendarId: string, summary: string, startTime: string, endTime: string, description?: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 删除日程
 */
export declare function deleteCalendarEvent(calendarId: string, eventId: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 列出任务
 */
export declare function listTasks(pageToken?: string, pageSize?: number): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 创建任务
 */
export declare function createTask(summary: string, description?: string, dueTime?: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 完成任务
 */
export declare function completeTask(taskId: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
