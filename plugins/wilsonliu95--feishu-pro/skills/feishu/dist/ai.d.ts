/**
 * 翻译文本
 */
export declare function translateText(text: string, sourceLang: string, targetLang: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 检测语种
 */
export declare function detectLanguage(text: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 基础图片 OCR 识别
 */
export declare function ocrImage(filePath: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
/**
 * 语音文件识别 (STT)
 * @param filePath - 语音文件路径
 * @param format - 格式 (pcm, adpcm, wav, opus, amr, m4a)
 */
export declare function speechToText(filePath: string, format?: string): Promise<import("@openclaw-feishu/feishu-client").FeishuResponse<any>>;
