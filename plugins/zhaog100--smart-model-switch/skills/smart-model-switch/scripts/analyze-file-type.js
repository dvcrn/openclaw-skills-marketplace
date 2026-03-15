#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// 读取配置文件
const configPath = path.join(__dirname, '..', 'config', 'model-rules.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

function analyzeFileType(filePath) {
  if (!filePath) {
    return { hasFile: false, fileType: null, model: null };
  }
  
  const ext = path.extname(filePath).toLowerCase();
  
  // 文件类型映射
  const fileTypes = {
    // 视觉文件
    '.jpg': 'vision',
    '.jpeg': 'vision', 
    '.png': 'vision',
    '.gif': 'vision',
    '.webp': 'vision',
    '.bmp': 'vision',
    '.tiff': 'vision',
    '.mp4': 'vision',
    '.avi': 'vision',
    '.mov': 'vision',
    '.mkv': 'vision',
    '.webm': 'vision',
    
    // 文档文件
    '.pdf': 'complex',
    '.doc': 'complex',
    '.docx': 'complex',
    '.ppt': 'complex',
    '.pptx': 'complex',
    '.xls': 'complex',
    '.xlsx': 'complex',
    '.txt': 'main',
    '.md': 'main',
    '.csv': 'main',
    
    // 代码文件
    '.js': 'coding',
    '.jsx': 'coding',
    '.ts': 'coding',
    '.tsx': 'coding',
    '.py': 'coding',
    '.java': 'coding',
    '.cpp': 'coding',
    '.c': 'coding',
    '.html': 'coding',
    '.css': 'coding',
    '.json': 'coding',
    '.xml': 'coding',
    '.yaml': 'coding',
    '.yml': 'coding'
  };
  
  const fileType = fileTypes[ext] || 'main';
  let model = config.models.main.id;
  
  switch(fileType) {
    case 'vision':
      model = config.models.vision.id;
      break;
    case 'coding':
      model = config.models.coding.id;
      break;
    case 'complex':
      model = config.models.complex.id;
      break;
    default:
      model = config.models.main.id;
  }
  
  return {
    hasFile: true,
    fileType: fileType,
    fileExtension: ext,
    model: model
  };
}

// 主函数
if (require.main === module) {
  const filePath = process.argv[2];
  const result = analyzeFileType(filePath);
  console.log(JSON.stringify(result, null, 2));
}

module.exports = { analyzeFileType };