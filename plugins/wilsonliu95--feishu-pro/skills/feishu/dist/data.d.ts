/**
 * 创建电子表格
 */
export declare function createSpreadsheet(title: string, folderToken?: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 获取表格信息（元数据，包括子表列表）
 */
export declare function getSpreadsheet(spreadsheetToken: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 读取单元格数据
 * @param spreadsheetToken - 表格 Token
 * @param sheetId - 子表 ID
 * @param range - 范围（如 A1:D10）
 */
export declare function getSheetValues(spreadsheetToken: string, sheetId: string, range: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 更新单元格数据
 */
export declare function updateSheetValues(spreadsheetToken: string, sheetId: string, range: string, values: any[][]): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 追加单元格数据
 */
export declare function appendSheetValues(spreadsheetToken: string, sheetId: string, range: string, values: any[][]): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 前插单元格数据
 */
export declare function prependSheetValues(spreadsheetToken: string, sheetId: string, range: string, values: any[][]): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 列出记录
 */
export declare function listRecords(appToken: string, tableId: string, filter?: string, sort?: string, pageToken?: string, pageSize?: number): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 获取单个记录
 */
export declare function getRecord(appToken: string, tableId: string, recordId: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 创建单条记录
 */
export declare function createRecord(appToken: string, tableId: string, fields: Record<string, any>): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 批量创建记录
 */
export declare function batchCreateRecords(appToken: string, tableId: string, records: Array<{
    fields: Record<string, any>;
}>): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 更新单条记录
 */
export declare function updateRecord(appToken: string, tableId: string, recordId: string, fields: Record<string, any>): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 批量更新记录
 */
export declare function batchUpdateRecords(appToken: string, tableId: string, records: Array<{
    record_id: string;
    fields: Record<string, any>;
}>): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 删除单条记录
 */
export declare function deleteRecord(appToken: string, tableId: string, recordId: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 批量删除记录
 */
export declare function batchDeleteRecords(appToken: string, tableId: string, recordIds: string[]): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 复制多维表格
 */
export declare function copyBitable(appToken: string, name: string, folderToken?: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
