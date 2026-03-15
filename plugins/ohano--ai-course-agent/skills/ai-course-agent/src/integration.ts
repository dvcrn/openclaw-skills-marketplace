/**
 * Integration with OpenClaw Main Session
 *
 * This module detects course generation requests from user input
 * and automatically executes the course generation flow.
 */

import { generateCourse, parseCourseRequest } from "./agent";

/**
 * Check if user input is a course generation request
 */
export function isCourseLessonRequest(message: string): boolean {
  // Keywords that indicate a course generation request
  const keywords = [
    "帮我生成",
    "帮我创建",
    "帮我制作",
    "我想生成",
    "我想创建",
    "生成",
    "创建",
    "课程",
  ];

  // Check if message contains at least "课程" and one of the action verbs
  const hasCourseKeyword = /课程/.test(message);
  const hasActionVerb = keywords.some((kw) => message.includes(kw));

  // Must contain year_level pattern (supports both digits and Chinese numerals)
  // Matches: 6年级, 7年级, 六年级, 七年级, etc.
  const hasPattern = /(\d+|[一二三四五六七八九十零]+)年级/.test(message);

  return hasCourseKeyword && hasActionVerb && hasPattern;
}

/**
 * Handle course generation request from user input
 *
 * This is the main entry point for automatic course generation.
 */
export async function handleCourseGenerationRequest(
  userInput: string,
): Promise<{
  success: boolean;
  message: string;
  courseLink?: string;
  lessonRef?: string;
}> {
  console.log(
    `[Integration] Detecting course generation request: "${userInput}"`,
  );

  // Check if this is a course request
  if (!isCourseLessonRequest(userInput)) {
    console.log("[Integration] Not a course generation request");
    return {
      success: false,
      message: "Not a course generation request",
    };
  }

  console.log("[Integration] Course generation request detected!");

  // Parse the request
  const request = parseCourseRequest(userInput);
  if (!request) {
    console.log("[Integration] Failed to parse course request");
    return {
      success: false,
      message:
        '无法理解你的请求。请按照这样的格式：\n"帮我生成[X年级][科目][内容]的课程"\n例如：帮我生成6年级数学分数乘除法的课程',
    };
  }

  console.log("[Integration] Parsed request:", request);

  // Generate the course
  console.log("[Integration] Generating course...");
  const result = await generateCourse(request);

  return result;
}

/**
 * Format the response for user display
 *
 * For Telegram: Returns plain text format with URL
 * Telegram will auto-detect and make the URL clickable
 */
export function formatCourseResponse(result: {
  success: boolean;
  message: string;
  courseLink?: string;
  lessonRef?: string;
}): string {
  if (!result.success) {
    return `❌ ${result.message}`;
  }

  // Return in plain text format with URL embedded
  // With blank line between message and link for better readability
  // Telegram will auto-detect the URL as clickable
  return `✅ ${result.message}\n\n📚 课程链接: ${result.courseLink}`;
}

/**
 * Main integration function to call from main session
 *
 * Usage in main session:
 * ```
 * import { processUserMessage } from './integration';
 *
 * // When user sends a message:
 * const response = await processUserMessage(userInput);
 * // Send response to user
 * ```
 */
export async function processUserMessage(userInput: string): Promise<string> {
  try {
    const result = await handleCourseGenerationRequest(userInput);
    return formatCourseResponse(result);
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    console.error("[Integration] Error processing message:", errorMsg);
    return `⚠️ 处理请求时出错: ${errorMsg}`;
  }
}

export default {
  isCourseLessonRequest,
  handleCourseGenerationRequest,
  formatCourseResponse,
  processUserMessage,
};
