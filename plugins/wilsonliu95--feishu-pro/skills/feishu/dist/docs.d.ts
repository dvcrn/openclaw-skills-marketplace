/**
 * 创建新版文档 (Docx)
 * @param title - 文档标题
 * @param folderToken - 所在文件夹 token（可选）
 */
export declare function createDocument(title: string, folderToken?: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 获取文档基本信息
 */
export declare function getDocument(documentId: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 获取文档纯文本内容
 */
export declare function getDocumentRawContent(documentId: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 列出文档所有块 (Blocks)
 */
export declare function listDocumentBlocks(documentId: string, pageToken?: string, pageSize?: number): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 向文档追加文本块
 * @param documentId - 文档 Token
 * @param text - 要追加的文本
 * @param targetBlockId - 目标块 ID（默认为文档本身，即 documentId）
 */
export declare function appendText(documentId: string, text: string, targetBlockId?: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 批量追加块
 */
export declare function appendBlocks(documentId: string, blocks: any[], targetBlockId?: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
type DocType = "doc" | "sheet" | "file" | "wiki" | "bitable" | "docx" | "mindnote" | "minutes" | "slides";
type MemberType = "email" | "openid" | "unionid" | "openchat" | "opendepartmentid" | "userid" | "groupid" | "wikispaceid";
/**
 * 获取公开权限设置
 */
export declare function getPublicPermission(token: string, type?: DocType): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 更新公开权限设置
 */
export declare function updatePublicPermission(token: string, type: DocType, data: any): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 添加协作者权限
 */
export declare function addMemberPermission(token: string, type: DocType, memberId: string, memberType: MemberType, role: 'view' | 'edit' | 'full_access'): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 列出云空间文件
 */
export declare function listFiles(folderToken?: string, pageToken?: string, pageSize?: number): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 上传文件到云空间
 */
export declare function uploadFile(filePath: string, parentNode: string, fileName?: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 创建文件夹
 */
export declare function createFolder(name: string, folderToken: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 列出知识库空间
 */
export declare function listWikiSpaces(pageToken?: string, pageSize?: number): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 获取知识库空间信息
 */
export declare function getWikiSpace(spaceId: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 列出知识库节点
 */
export declare function listWikiNodes(spaceId: string, parentNodeToken?: string, pageToken?: string, pageSize?: number): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 获取节点信息
 */
export declare function getNodeInfo(token: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
export {};
