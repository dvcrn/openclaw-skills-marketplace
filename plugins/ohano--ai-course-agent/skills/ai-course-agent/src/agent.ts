/**
 * AI Course Generator Agent
 *
 * Main orchestration layer that:
 * 1. Parses user request (grade, subject, content)
 * 2. Gathers curriculum information
 * 3. Calls Edustem API via api-edustem-skill
 * 4. Returns course link
 */

import {
  login,
  createLessonPlan,
  acceptLessonPlan,
  generateLessonUrl,
} from "./edustem-api";
import { gatherCurriculumContent, generateTeacherNotes } from "./utils";
import { getEdustemConfig } from "./config";

/**
 * Types
 */

export interface CourseRequest {
  grade: string;
  subject: string;
  content: string;
}

export interface GeneratedCourseResponse {
  success: boolean;
  courseLink?: string;
  lessonRef?: string;
  message: string;
}

/**
 * Main course generation function
 *
 * Orchestrates the full flow:
 * 1. Gather curriculum content
 * 2. Login to Edustem API
 * 3. Create lesson plan
 * 4. Accept lesson plan
 * 5. Return course link
 */
export async function generateCourse(
  request: CourseRequest,
): Promise<GeneratedCourseResponse> {
  try {
    console.log(`[Agent] Processing course request:`, request);

    // Get credentials from config (environment or gateway)
    let credentials;
    try {
      credentials = getEdustemConfig();
    } catch (error) {
      return {
        success: false,
        message: `配置错误: ${error instanceof Error ? error.message : "Missing credentials"}`,
      };
    }

    // Step 1: Gather curriculum content
    console.log("[Agent] Gathering curriculum content...");
    const curriculumData = await gatherCurriculumContent(
      request.subject,
      request.content,
      request.grade,
    );

    // Step 2: Login to Edustem API
    console.log("[Agent] Logging in to Edustem API...");
    const token = await login(credentials.username, credentials.password);
    console.log("[Agent] Login successful, token received");

    // Step 3: Create lesson plan
    console.log("[Agent] Creating lesson plan...");
    const createResponse = await createLessonPlan(token, {
      subject: curriculumData.subject,
      year_level: request.grade,
      teaching_time_minutes: "45",
      topic: curriculumData.topic,
      curriculum_text: curriculumData.curriculum_text,
      elaborations: curriculumData.elaborations,
      teacher_notes: curriculumData.teacher_notes,
      concepts: "",
      subject_specific_instructions: "",
    });

    const lessonRef = createResponse.data.lesson_ref;
    console.log(`[Agent] Lesson plan created: ${lessonRef}`);

    // Step 4: Accept lesson plan
    console.log("[Agent] Accepting lesson plan...");
    const acceptResponse = await acceptLessonPlan(token, lessonRef);
    console.log("[Agent] Lesson plan accepted");

    // Step 5: Generate and return course link
    const courseLink = generateLessonUrl(lessonRef);

    return {
      success: true,
      courseLink,
      lessonRef,
      message: `成功为${request.grade}年级${request.subject}《${request.content}》生成课程！`,
    };
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    console.error("[Agent] Error:", errorMsg);
    return {
      success: false,
      message: `生成课程失败: ${errorMsg}`,
    };
  }
}

/**
 * Convert Chinese numerals to Arabic numerals
 */
function chineseNumberToArabic(chinese: string): string {
  const map: { [key: string]: string } = {
    零: "0",
    一: "1",
    二: "2",
    三: "3",
    四: "4",
    五: "5",
    六: "6",
    七: "7",
    八: "8",
    九: "9",
    十: "10",
  };

  if (map[chinese]) {
    return map[chinese];
  }

  // For compound numbers like 十一, 十二, etc.
  if (chinese.includes("十")) {
    if (chinese === "十") return "10";
    const digit = chinese.charAt(1);
    return "1" + (map[digit] || digit);
  }

  return chinese;
}

/**
 * Parse user input to extract course request
 *
 * Example: "帮我生成6年级数学分数乘除法的课程"
 *          "帮我创建一个七年级语文从百草园到三味书屋的课程"
 * Output: { grade: '6', subject: '数学', content: '分数乘除法' }
 */
export function parseCourseRequest(userInput: string): CourseRequest | null {
  try {
    // Match both Arabic and Chinese numerals for year level
    const gradeMatch = userInput.match(/(\d+|[一二三四五六七八九十零]+)年级/);
    const subjectMatch = userInput.match(
      /(数学|语文|英语|科学|历史|地理|物理|化学|生物)/,
    );

    if (!gradeMatch || !subjectMatch) {
      return null;
    }

    // Convert Chinese numeral to Arabic if needed
    let gradeStr = gradeMatch[1];
    if (!/^\d+$/.test(gradeStr)) {
      gradeStr = chineseNumberToArabic(gradeStr);
    }

    // Extract content - everything between subject and "课程"
    const subject = subjectMatch[1];
    const subjectIndex = userInput.indexOf(subject);
    const contentStart = subjectIndex + subject.length;
    const contentEnd = userInput.indexOf("课程", contentStart);
    const content = userInput
      .substring(contentStart, contentEnd >= 0 ? contentEnd : undefined)
      .trim();

    return {
      grade: gradeStr,
      subject,
      content: content || subject,
    };
  } catch (error) {
    console.error("[Parser] Error parsing request:", error);
    return null;
  }
}

/**
 * Main entry point for testing
 */
async function main() {
  // Test input
  const userInput = "帮我生成6年级数学分数乘除法的课程";
  console.log(`[Main] User input: "${userInput}"`);

  // Parse request
  const request = parseCourseRequest(userInput);
  if (!request) {
    console.error("[Main] Failed to parse user input");
    return;
  }

  console.log("[Main] Parsed request:", request);

  // Generate course
  const result = await generateCourse(request);
  console.log("[Main] Result:", result);

  if (result.success) {
    console.log(`\n✅ Course generated successfully!`);
    console.log(`📚 Course Link: ${result.courseLink}`);
  } else {
    console.log(`\n❌ Failed to generate course: ${result.message}`);
  }
}

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}

export default { generateCourse, parseCourseRequest };
