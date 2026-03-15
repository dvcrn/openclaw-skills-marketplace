const md2img = require('./md_to_png.js');
const fs = require('fs');

// 示例：将markdown内容转换为图片
const mdContent = `
# 🥑 测试文档
这是一个测试文档，用于验证auto-md2img技能是否正常工作。

## 功能列表
- ✅ 中文支持
- ✅ Emoji 支持
- ✅ 代码块支持
- ✅ 表格支持

| 功能 | 状态 |
|------|------|
| 中文显示 | ✅ 正常 |
| Emoji显示 | ✅ 正常 |
| 代码高亮 | ✅ 正常 |

\`\`\`javascript
console.log("Hello, World!");
\`\`\`

> 这是一段引用文本
`;

// 生成临时文件路径
const tempMdPath = '/tmp/test.md';
const outputPath = '/tmp/test_output.png';

fs.writeFileSync(tempMdPath, mdContent);

// 调用转换
md2img(mdContent, outputPath)
  .then(() => {
    console.log(`图片生成成功：${outputPath}`);
    console.log('可以通过 <qqimg> 标签发送：');
    console.log(`<qqimg>${outputPath}</qqimg>`);
  })
  .catch(err => {
    console.error('转换失败：', err);
  });
