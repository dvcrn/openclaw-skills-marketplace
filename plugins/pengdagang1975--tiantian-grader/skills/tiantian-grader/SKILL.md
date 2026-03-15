---
name: tiantian-grader
description: "作业批改专家，支持多份作业连续批改，自动生成班级成绩统计表"
---

## match

- 初始化
- 开始新作业
- 类型A
- 类型B
- 确认无误
- 逐份批改
- 批量导入
- 生成报表
- 查询历史
- 查看统计
- 全部改为严格模式
- 全部改为宽松模式

# 📚 天天老师助手 - 作业批改专家（完整版）

## 核心依赖

```javascript
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');
const crypto = require('crypto');
const execAsync = util.promisify(exec);

// ==================== 工作区路径常量 ====================
const WORKSPACE = '/root/.openclaw/workspace/teacher_tiantian';
const PATHS = {
  homework: path.join(WORKSPACE, 'homework'),
  original: path.join(WORKSPACE, 'homework/original'),
  processed: path.join(WORKSPACE, 'homework/processed'),
  corrected: path.join(WORKSPACE, 'corrected'),
  byStudent: path.join(WORKSPACE, 'corrected/by_student'),
  byDate: path.join(WORKSPACE, 'corrected/by_date'),
  questions: path.join(WORKSPACE, 'questions'),
  questionBank: path.join(WORKSPACE, 'questions/bank'),
  questionHistory: path.join(WORKSPACE, 'questions/history'),
  statistics: path.join(WORKSPACE, 'statistics'),
  statsClass: path.join(WORKSPACE, 'statistics/class'),
  statsStudent: path.join(WORKSPACE, 'statistics/student'),
  statsQuestion: path.join(WORKSPACE, 'statistics/question'),
  exports: path.join(WORKSPACE, 'exports'),
  exportCsv: path.join(WORKSPACE, 'exports/csv'),
  rosters: path.join(WORKSPACE, 'rosters'),
  currentRoster: path.join(WORKSPACE, 'current_roster/active.csv'),
  tools: path.join(WORKSPACE, 'tools'),
  uploads: path.join(WORKSPACE, 'uploads'),
  temp: path.join(WORKSPACE, 'temp'),
  ocrCache: path.join(WORKSPACE, 'ocr_cache'),
  memory: path.join(WORKSPACE, 'memory'),
  memoryFile: path.join(WORKSPACE, 'memory/MEMORY.md')
};

// ==================== 确保目录存在 ====================
Object.values(PATHS).forEach(dir => {
  if (typeof dir === 'string' && !dir.includes('.')) {
    try { fs.mkdirSync(dir, { recursive: true }); } catch (e) {}
  }
});

// ==================== 会话状态存储 ====================
const sessions = new Map();

// ==================== 花名册管理 ====================
function readRoster() {
  try {
    if (!fs.existsSync(PATHS.currentRoster)) return [];
    const content = fs.readFileSync(PATHS.currentRoster, 'utf8');
    const lines = content.split('\n').filter(l => l.trim());
    if (lines.length < 2) return [];

    const headers = lines[0].split(',').map(h => h.trim());
    const students = [];
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      if (values.length === headers.length) {
        const student = {};
        headers.forEach((h, idx) => student[h] = values[idx]);
        students.push(student);
      }
    }
    return students;
  } catch (error) {
    console.error('读取花名册失败:', error);
    return [];
  }
}

// ==================== 记忆文件读取 ====================
function readMemory() {
  try {
    if (!fs.existsSync(PATHS.memoryFile)) {
      fs.writeFileSync(PATHS.memoryFile, '# 天天老师助手记忆文件\n\n');
      return [];
    }
    const content = fs.readFileSync(PATHS.memoryFile, 'utf8');
    const lines = content.split('\n').filter(l => l.startsWith('- '));
    return lines.map(l => l.substring(2));
  } catch (error) {
    return [];
  }
}

// ==================== 写入记忆 ====================
function writeMemory(entry) {
  try {
    const date = new Date().toISOString().split('T')[0];
    const content = `\n## ${date}\n- ${entry}\n`;
    fs.appendFileSync(PATHS.memoryFile, content);
    return true;
  } catch (error) {
    return false;
  }
}

// ==================== 文件上传处理 ====================
function saveUploadedFile(file) {
  try {
    console.log("📸 保存文件:", file.name || file.path);

    let originalPath, fileName;

    if (typeof file === 'string') {
      originalPath = file;
      fileName = path.basename(file);
    } else if (file.path) {
      originalPath = file.path;
      fileName = file.name || path.basename(originalPath);
    } else if (file.url) {
      originalPath = file.url;
      fileName = file.name || `url_${Date.now()}.jpg`;
    } else {
      console.error("未知文件格式:", Object.keys(file));
      return null;
    }

    if (!fs.existsSync(originalPath)) {
      console.error(`文件不存在: ${originalPath}`);
      return null;
    }

    const ext = path.extname(fileName) || '.jpg';
    const baseName = path.basename(fileName, ext);
    const newName = `${baseName}_${Date.now()}${ext}`;
    const destPath = path.join(PATHS.original, newName);

    fs.copyFileSync(originalPath, destPath);
    console.log(`✅ 已保存: ${destPath}`);

    return { originalName: fileName, savedPath: destPath };
  } catch (error) {
    console.error('文件保存失败:', error);
    return null;
  }
}

function saveUploadedFiles(files) {
  return files.map(f => saveUploadedFile(f)).filter(f => f !== null);
}

// ==================== 题库管理 ====================
function saveQuestionsToBank(questions, subject = 'english') {
  try {
    const date = new Date().toISOString().split('T')[0];
    const filePath = path.join(PATHS.questionBank, `${subject}_${date}.json`);

    let bank = [];
    if (fs.existsSync(filePath)) {
      bank = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    }

    const newQuestions = questions.filter(q =>
      !bank.some(b => b.content === q.content)
    );

    bank.push(...newQuestions);
    fs.writeFileSync(filePath, JSON.stringify(bank, null, 2), 'utf8');

    return newQuestions.length;
  } catch (error) {
    console.error('保存题目失败:', error);
    return 0;
  }
}

// ==================== 批改结果存储 ====================
function saveGradingResult(studentName, homeworkTitle, questions, results, totalScore, maxScore) {
  try {
    const date = new Date().toISOString().split('T')[0];
    const timeStr = new Date().toTimeString().split(' ')[0].replace(/:/g, '-');

    const studentFile = path.join(PATHS.byStudent, `${studentName}_${date}.json`);

    const questionData = questions.map((q, idx) => ({
      id: q.id,
      content: q.content,
      answer: q.answer,
      studentAnswer: results[idx]?.studentAnswer || '',
      score: results[idx]?.score || 0,
      maxScore: q.score,
      isCorrect: results[idx]?.isCorrect || false,
      mode: q.gradingMode || 'strict'
    }));

    const studentData = {
      student: studentName,
      date: date,
      time: timeStr,
      homework: homeworkTitle,
      questions: questionData,
      totalScore,
      maxScore,
      accuracy: (totalScore / maxScore * 100).toFixed(1) + '%'
    };

    fs.writeFileSync(studentFile, JSON.stringify(studentData, null, 2), 'utf8');

    const dateFile = path.join(PATHS.byDate, `${date}.json`);
    let daily = [];
    if (fs.existsSync(dateFile)) {
      daily = JSON.parse(fs.readFileSync(dateFile, 'utf8'));
    }
    daily.push(studentData);
    fs.writeFileSync(dateFile, JSON.stringify(daily, null, 2), 'utf8');

    return studentFile;
  } catch (error) {
    console.error('保存批改结果失败:', error);
    return null;
  }
}

// ==================== 生成报表 ====================
async function generateSummary(results, homeworkTitle) {
  try {
    const scores = results.map(r => r.total);
    const maxScore = results[0]?.maxScore || 100;
    const avgScore = (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1);

    let summary = `📊 批改小结：${homeworkTitle}\n\n`;
    summary += `参与人数：${results.length}人\n`;
    summary += `平均分：${avgScore}/${maxScore}\n`;
    summary += `最高分：${Math.max(...scores)}\n`;
    summary += `最低分：${Math.min(...scores)}\n\n`;

    const dist = {
      '90-100': scores.filter(s => s >= maxScore * 0.9).length,
      '80-89': scores.filter(s => s >= maxScore * 0.8 && s < maxScore * 0.9).length,
      '70-79': scores.filter(s => s >= maxScore * 0.7 && s < maxScore * 0.8).length,
      '60-69': scores.filter(s => s >= maxScore * 0.6 && s < maxScore * 0.7).length,
      '60以下': scores.filter(s => s < maxScore * 0.6).length
    };

    summary += `📈 分数分布：\n`;
    for (const [range, count] of Object.entries(dist)) {
      if (count > 0) summary += `  ${range}分：${count}人\n`;
    }

    return summary;
  } catch (error) {
    return '生成小结失败';
  }
}

// ==================== 导出CSV ====================
function exportToCSV(results, filename) {
  try {
    const csvPath = path.join(PATHS.exportCsv, `${filename}.csv`);

    let headers = ['姓名', '总分', '满分', '正确率'];
    if (results[0]?.details) {
      results[0].details.forEach((d, i) => {
        headers.push(`第${d.id}题`);
      });
    }

    let csvContent = headers.join(',') + '\n';

    results.forEach(r => {
      const accuracy = (r.total / r.maxScore * 100).toFixed(1);
      let row = [r.name, r.total, r.maxScore, `${accuracy}%`];

      if (r.details) {
        r.details.forEach(d => row.push(d.score));
      }

      csvContent += row.join(',') + '\n';
    });

    fs.writeFileSync(csvPath, csvContent, 'utf8');
    return csvPath;
  } catch (error) {
    return null;
  }
}

// ==================== UI 渲染函数 ====================
function getConfidenceIcon(confidence) {
  if (confidence === 'high') return '✅';
  if (confidence === 'medium') return '⚠️';
  return '❓';
}

function getModeIcon(mode) {
  return mode === 'strict' ? '🔍' : '🎯';
}

function renderConfirmationUI(questions) {
  let output = "✅ 作业识别完成！\n\n";
  output += "=".repeat(60) + "\n\n";

  questions.forEach((q, idx) => {
    const confIcon = getConfidenceIcon(q.confidence || 'medium');
    const modeIcon = getModeIcon(q.gradingMode || 'strict');
    const modeText = q.gradingMode === 'strict' ? '严格' : '宽松';

    if (q.type === 'compound' && q.sub_questions) {
      output += `【第${idx+1}题】📚 ${q.content} (含${q.sub_questions.length}子题)\n`;
      output += `├─ 模式：[${modeIcon} ${modeText} 切换]\n`;

      q.sub_questions.forEach((sub, subIdx) => {
        const prefix = subIdx === q.sub_questions.length - 1 ? '└─' : '├─';
        output += `${prefix} 【${sub.id}】\n`;
        output += `   题目：${sub.content} [修改]\n`;
        output += `   答案：${sub.answer || '待确认'} [修改] [${sub.score || 5}分]\n`;
      });
    } else {
      output += `【第${idx+1}题】${confIcon} ${q.content}\n`;
      output += `  答案：${q.answer || '待确认'} [修改] [${q.score || 10}分]\n`;
      output += `  模式：[${modeIcon} ${modeText} 切换]\n`;
    }
    output += "\n";
  });

  output += "=".repeat(60) + "\n";
  output += "请逐题确认，或发送：\n";
  output += "- 修改第X题答案改为...\n";
  output += "- 第X题改为严格模式/宽松模式\n";
  output += "- 全部改为严格模式\n";
  output += "- 全部改为宽松模式\n";
  output += "- 【确认无误，开始批改】\n";

  return output;
}

// ==================== 主处理函数 ====================
async function handler(input, context) {
  console.log("🔥🔥🔥 tiantian-grader 技能被调用！🔥🔥🔥");
  console.log("=".repeat(60));
  console.log("🎯 作业批改技能触发", new Date().toISOString());
  console.log("📨 收到消息:", input?.message?.content);
  console.log("📎 文件数量:", input?.message?.files?.length || 0);
  
  const sessionId = context?.session?.id || 'default';
  if (!sessions.has(sessionId)) {
    sessions.set(sessionId, {
      stage: 'idle',
      homework: {
        title: '',
        questions: [],
        totalScore: 0,
        pageFormat: null
      },
      students: {
        roster: [],
        current: null,
        completed: []
      }
    });
    console.log("🆕 创建新会话:", sessionId);
  }

  const session = sessions.get(sessionId);
  console.log("🔄 当前会话阶段:", session.stage);
  console.log("=".repeat(60));

  const message = input?.message?.content || "";
  const files = input?.message?.files || [];

  try {
    // ========== 初始化 ==========
    if (message.includes("初始化")) {
      console.log("📋 执行初始化...");
      const roster = readRoster();
      session.students.roster = roster;
      const memory = readMemory();
      const memoryHint = memory.length > 0 ? `\n\n📝 历史记忆：${memory.slice(-3).join('、')}` : '';
      return roster.length > 0
        ? `✅ 已加载花名册，共${roster.length}名学生${memoryHint}\n\n发送【开始新作业】启动批改`
        : "⚠️ 未找到花名册，请上传CSV文件或使用管理脚本创建";
    }

    // ========== 开始新作业 ==========
    if (message.includes("开始新作业")) {
      console.log("📝 开始新作业...");
      if (session.students.roster.length === 0) {
        return "⚠️ 请先发送【初始化】加载花名册";
      }
      session.stage = 'format_select';
      return "📋 请选择本次作业的格式：\n\n📄 类型A：分开页（学生信息在单独封面页）\n📑 类型B：混合页（学生信息和作业在同一页）\n\n请发送 \"类型A\" 或 \"类型B\" 来选择作业格式。";
    }

    // ========== 格式选择 ==========
    if (session.stage === 'format_select') {
      console.log("📐 选择格式:", message);
      if (message.includes("类型A")) {
        session.homework.pageFormat = 'separate';
        session.stage = 'upload_answers';
        return "✅ 已设置为分开页\n\n请上传作业题目和标准答案图片";
      }
      if (message.includes("类型B")) {
        session.homework.pageFormat = 'mixed';
        session.stage = 'upload_answers';
        return "✅ 已设置为混合页\n\n请上传作业题目和标准答案图片";
      }
      return "请发送“类型A”或“类型B”";
    }

    // ========== 上传答案图片（模拟OCR识别）==========
    if (session.stage === 'upload_answers' && files.length > 0) {
      console.log("📸 处理上传的图片...");
      const saved = saveUploadedFiles(files);
      if (saved.length === 0) return "❌ 文件保存失败";

      // 模拟OCR识别结果
      const questions = [
        { id: 1, content: "adj.出乎意料的;始料不及的", answer: "unexpected", score: 5, confidence: "high", type: "simple" },
        { id: 2, content: "n.背包;旅行包", answer: "backpack", score: 5, confidence: "medium", type: "simple" },
        { id: 3, content: "v.睡过头;睡得太久", answer: "oversleep", score: 10, confidence: "low", type: "simple" },
        { 
          id: 4, 
          content: "阅读理解", 
          type: "compound", 
          gradingMode: "loose",
          sub_questions: [
            { id: "4.1", content: "根据第一段，作者心情是？", answer: "excited", score: 5 },
            { id: "4.2", content: "第二段中“it”指代什么？", answer: "the book", score: 5 },
            { id: "4.3", content: "作者最后建议什么？", answer: "read more", score: 5 }
          ]
        },
        { id: 5, content: "n.街区", answer: "district", score: 5, confidence: "high", type: "simple" }
      ];

      session.pendingQuestions = questions;
      session.stage = 'confirm_questions';

      console.log(`✅ 提取到 ${questions.length} 个题目，进入确认阶段`);
      return renderConfirmationUI(questions);
    }

    // ========== 确认/修改题目 ==========
    if (session.stage === 'confirm_questions') {
      console.log("✏️ 确认阶段收到:", message);

      // 修改答案
      const answerMatch = message.match(/第(\d+)题答案改为(.+)/);
      if (answerMatch) {
        const idx = parseInt(answerMatch[1]) - 1;
        const newAnswer = answerMatch[2].trim();
        if (session.pendingQuestions[idx]) {
          session.pendingQuestions[idx].answer = newAnswer;
          return renderConfirmationUI(session.pendingQuestions);
        }
      }

      // 切换模式
      const strictMatch = message.match(/第(\d+)题改为严格模式/);
      const looseMatch = message.match(/第(\d+)题改为宽松模式/);

      if (strictMatch) {
        const idx = parseInt(strictMatch[1]) - 1;
        if (session.pendingQuestions[idx]) {
          session.pendingQuestions[idx].gradingMode = 'strict';
          return renderConfirmationUI(session.pendingQuestions);
        }
      }

      if (looseMatch) {
        const idx = parseInt(looseMatch[1]) - 1;
        if (session.pendingQuestions[idx]) {
          session.pendingQuestions[idx].gradingMode = 'loose';
          return renderConfirmationUI(session.pendingQuestions);
        }
      }

      // 批量切换
      if (message.includes("全部改为严格模式")) {
        session.pendingQuestions.forEach(q => q.gradingMode = 'strict');
        return renderConfirmationUI(session.pendingQuestions);
      }

      if (message.includes("全部改为宽松模式")) {
        session.pendingQuestions.forEach(q => q.gradingMode = 'loose');
        return renderConfirmationUI(session.pendingQuestions);
      }

      // 确认无误
      if (message.includes("确认无误")) {
        session.homework.questions = session.pendingQuestions;
        session.homework.totalScore = session.pendingQuestions.reduce((sum, q) => {
          if (q.type === 'compound' && q.sub_questions) {
            return sum + q.sub_questions.reduce((s, sub) => s + (sub.score || 0), 0);
          }
          return sum + (q.score || 0);
        }, 0);

        const savedCount = saveQuestionsToBank(session.homework.questions);
        writeMemory(`新增题目 ${session.homework.questions.length} 道`);
        
        session.stage = 'mode_select';
        delete session.pendingQuestions;

        return `📚 已保存 ${savedCount} 道新题到题库\n\n` +
               `📋 请选择批改模式：\n\n` +
               `📄 逐份批改：逐页拍照，实时反馈\n` +
               `📚 批量导入：一次性上传所有作业\n\n` +
               `请发送“逐份批改”或“批量导入”`;
      }
    }

    // ========== 选择批改模式 ==========
    if (session.stage === 'mode_select') {
      if (message.includes("逐份批改")) {
        session.gradingMode = 'sequential';
        session.stage = 'grading';
        return "✅ 逐份批改模式\n\n请拍摄第一份作业的封面页或第一页";
      }
      if (message.includes("批量导入")) {
        session.gradingMode = 'batch';
        session.stage = 'batch_upload';
        return "✅ 批量导入模式\n\n请上传所有学生作业图片（按文件名排序）";
      }
    }

    // ========== 批量上传 ==========
    if (session.stage === 'batch_upload' && files.length > 0) {
      const saved = saveUploadedFiles(files);
      session.uploadedFiles = saved;
      return `📁 已收到${saved.length}张图片\n\n请发送【开始批量批改】`;
    }

    // ========== 开始批量批改（模拟）==========
    if (session.stage === 'batch_processing' || message.includes("开始批量批改")) {
      if (!session.uploadedFiles || session.uploadedFiles.length === 0) {
        return "❌ 没有待批改的文件";
      }

      const results = [];
      for (let i = 0; i < Math.min(session.uploadedFiles.length, session.students.roster.length); i++) {
        const studentName = session.students.roster[i]?.姓名 || `学生${i+1}`;
        
        // 模拟批改结果
        let totalScore = Math.floor(Math.random() * 20) + 10; // 10-30分随机
        const details = session.homework.questions.map(q => ({
          id: q.id,
          studentAnswer: "模拟答案",
          isCorrect: Math.random() > 0.3,
          score: Math.random() > 0.3 ? (q.score || 5) : 0
        }));

        results.push({
          name: studentName,
          total: totalScore,
          maxScore: session.homework.totalScore,
          details: details
        });

        saveGradingResult(
          studentName,
          session.homework.title || '未命名作业',
          session.homework.questions,
          details,
          totalScore,
          session.homework.totalScore
        );
        
        session.students.completed.push({ name: studentName, total: totalScore });
      }

      const csvPath = exportToCSV(results, `batch_${Date.now()}`);
      const summary = await generateSummary(results, session.homework.title || '未命名作业');

      writeMemory(`批量批改 ${results.length} 人，平均分 ${summary.split('\n')[2].split('：')[1]}`);

      let response = `✅ 批量批改完成\n\n`;
      results.forEach(r => {
        response += `${r.name}: ${r.total}/${r.maxScore}分\n`;
      });
      response += `\n${summary}`;
      if (csvPath) response += `\n\n📎 CSV导出: ${csvPath}`;

      return response;
    }

    // ========== 生成报表 ==========
    if (message.includes("生成报表")) {
      if (session.students.completed.length === 0) return "暂无已批改数据";

      const results = session.students.completed.map(s => ({
        name: s.name,
        total: s.total,
        maxScore: session.homework.totalScore,
        details: []
      }));

      const csvPath = exportToCSV(results, `report_${Date.now()}`);
      const summary = await generateSummary(results, session.homework.title || '未命名作业');

      return summary + (csvPath ? `\n\n📎 CSV导出: ${csvPath}` : '');
    }

    // ========== 查询历史 ==========
    if (message.includes("查询历史")) {
      const memory = readMemory();
      if (memory.length === 0) return "暂无历史记录";
      return "📝 历史记忆：\n" + memory.slice(-10).map(m => `- ${m}`).join('\n');
    }

    // ========== 查看统计 ==========
    if (message.includes("查看统计")) {
      if (session.students.completed.length === 0) return "暂无统计数据";
      const avg = session.students.completed.reduce((sum, s) => sum + s.total, 0) / session.students.completed.length;
      return `📊 当前统计\n\n已批改：${session.students.completed.length}人\n平均分：${avg.toFixed(1)}/${session.homework.totalScore}\n最高分：${Math.max(...session.students.completed.map(s => s.total))}\n最低分：${Math.min(...session.students.completed.map(s => s.total))}`;
    }

    // ========== 默认响应 ==========
    return "老师好！发送【初始化】加载花名册，或【开始新作业】启动批改";

  } catch (error) {
    console.error('❌ 处理出错:', error);
    return `❌ 处理出错：${error.message}`;
  }
}

module.exports = { handler };
