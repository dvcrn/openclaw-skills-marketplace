#!/usr/bin/env node
/**
 * Cognitive Brain - 知识图谱可视化
 * 生成记忆网络的可视化图表
 */

const fs = require('fs');
const path = require('path');
const { resolveModule } = require('./module_resolver.cjs');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');
const OUTPUT_DIR = path.join(HOME, '.openclaw/workspace/brain-visuals');

const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

// 确保输出目录存在
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * 生成 DOT 格式（Graphviz）
 */
async function generateDotGraph() {
  const { Pool } = resolveModule('pg');
  const pool = new Pool(config.storage.primary);
  
  try {
    console.log('📊 生成 DOT 知识图谱...\n');
    
    // 获取概念和关联
    const concepts = await pool.query(`
      SELECT id, name, access_count, importance
      FROM concepts
      ORDER BY access_count DESC, importance DESC
      LIMIT 100
    `);
    
    const associations = await pool.query(`
      SELECT a.from_id, a.to_id, a.weight, a.type, c1.name as from_name, c2.name as to_name
      FROM associations a
      JOIN concepts c1 ON a.from_id = c1.id
      JOIN concepts c2 ON a.to_id = c2.id
      LIMIT 200
    `);
    
    // 生成 DOT
    let dot = 'digraph BrainNetwork {\n';
    dot += '  rankdir=LR;\n';
    dot += '  node [shape=box, style=rounded, fontname="Arial"];\n';
    dot += '  edge [fontname="Arial", fontsize=10];\n\n';
    
    // 添加节点
    const nodeMap = new Map();
    for (const c of concepts.rows) {
      const size = Math.max(0.5, Math.min(2.0, (c.access_count || 0) * 0.1 + 0.5));
      const color = c.importance > 0.7 ? '#ff9999' : 
                    c.importance > 0.4 ? '#99ccff' : '#99ff99';
      
      const safeName = c.name.replace(/"/g, '\\"');
      dot += `  "${c.id}" [label="${safeName}", width=${size.toFixed(1)}, fillcolor="${color}", style="filled,rounded"];\n`;
      nodeMap.set(c.id, c);
    }
    
    dot += '\n';
    
    // 添加边
    for (const a of associations.rows) {
      if (nodeMap.has(a.from_id) && nodeMap.has(a.to_id)) {
        const penwidth = Math.max(0.5, a.weight * 2);
        const label = a.type !== 'related' ? a.type : '';
        dot += `  "${a.from_id}" -> "${a.to_id}" [weight=${a.weight.toFixed(2)}, penwidth=${penwidth.toFixed(1)}, label="${label}"];\n`;
      }
    }
    
    dot += '}\n';
    
    // 保存
    const dotPath = path.join(OUTPUT_DIR, 'brain-network.dot');
    fs.writeFileSync(dotPath, dot);
    
    console.log(`✅ DOT 图谱已保存: ${dotPath}`);
    console.log(`   节点: ${concepts.rows.length}`);
    console.log(`   边: ${associations.rows.length}`);
    
    return { dot, concepts: concepts.rows.length, edges: associations.rows.length };
    
  } finally {
    await pool.end();
  }
}

/**
 * 生成 Mermaid 格式（Markdown 友好）
 */
async function generateMermaidGraph() {
  const { Pool } = resolveModule('pg');
  const pool = new Pool(config.storage.primary);
  
  try {
    console.log('\n📊 生成 Mermaid 知识图谱...\n');
    
    // 获取前30个最重要的概念和关联
    const concepts = await pool.query(`
      SELECT id, name, access_count, importance
      FROM concepts
      ORDER BY importance DESC, access_count DESC
      LIMIT 30
    `);
    
    const conceptIds = concepts.rows.map(c => c.id);
    
    const associations = await pool.query(`
      SELECT a.from_id, a.to_id, a.weight, c1.name as from_name, c2.name as to_name
      FROM associations a
      JOIN concepts c1 ON a.from_id = c1.id
      JOIN concepts c2 ON a.to_id = c2.id
      WHERE a.from_id = ANY($1) AND a.to_id = ANY($1)
      ORDER BY a.weight DESC
      LIMIT 50
    `, [conceptIds]);
    
    // 生成 Mermaid
    let mermaid = '```mermaid\ngraph LR\n';
    
    // 添加节点定义（带样式）
    for (const c of concepts.rows) {
      const safeName = c.name.replace(/[\[\](){}]/g, '_');
      if (c.importance > 0.7) {
        mermaid += `  ${c.id}["${safeName}"]:::important\n`;
      } else if (c.importance > 0.4) {
        mermaid += `  ${c.id}["${safeName}"]:::normal\n`;
      } else {
        mermaid += `  ${c.id}["${safeName}"]:::minor\n`;
      }
    }
    
    mermaid += '\n';
    
    // 添加边
    for (const a of associations.rows) {
      mermaid += `  ${a.from_id} -->|${a.weight.toFixed(1)}| ${a.to_id}\n`;
    }
    
    // 样式定义
    mermaid += '\n  classDef important fill:#ff9999,stroke:#ff6666,stroke-width:2px;\n';
    mermaid += '  classDef normal fill:#99ccff,stroke:#6699cc,stroke-width:1px;\n';
    mermaid += '  classDef minor fill:#99ff99,stroke:#66cc66,stroke-width:1px;\n';
    mermaid += '```\n';
    
    // 保存
    const mermaidPath = path.join(OUTPUT_DIR, 'brain-network.md');
    fs.writeFileSync(mermaidPath, mermaid);
    
    console.log(`✅ Mermaid 图谱已保存: ${mermaidPath}`);
    
    return { mermaid, concepts: concepts.rows.length, edges: associations.rows.length };
    
  } finally {
    await pool.end();
  }
}

/**
 * 生成简单的文本网络图
 */
async function generateTextGraph() {
  const { Pool } = resolveModule('pg');
  const pool = new Pool(config.storage.primary);
  
  try {
    console.log('\n📊 生成文本知识图谱...\n');
    
    // 获取核心概念（重要性最高的15个）
    const concepts = await pool.query(`
      SELECT name, importance, access_count
      FROM concepts
      ORDER BY importance DESC, access_count DESC
      LIMIT 15
    `);
    
    // 获取关联
    const associations = await pool.query(`
      SELECT c1.name as from_name, c2.name as to_name, a.weight, a.type
      FROM associations a
      JOIN concepts c1 ON a.from_id = c1.id
      JOIN concepts c2 ON a.to_id = c2.id
      ORDER BY a.weight DESC
      LIMIT 20
    `);
    
    let text = '# 🧠 知识网络可视化\n\n';
    text += `生成时间: ${new Date().toLocaleString('zh-CN')}\n\n`;
    
    text += '## 核心概念\n\n';
    text += '| 概念 | 重要性 | 访问次数 |\n';
    text += '|------|--------|----------|\n';
    for (const c of concepts.rows) {
      const stars = '★'.repeat(Math.floor(c.importance * 5)) + '☆'.repeat(5 - Math.floor(c.importance * 5));
      text += `| ${c.name} | ${stars} | ${c.access_count} |\n`;
    }
    
    text += '\n## 重要关联\n\n';
    text += '```\n';
    for (const a of associations.rows) {
      const arrow = '─'.repeat(Math.floor(a.weight * 10)) + '→';
      text += `${a.from_name} ${arrow} ${a.to_name}`;
      if (a.type !== 'related') {
        text += ` [${a.type}]`;
      }
      text += '\n';
    }
    text += '```\n';
    
    text += '\n## 统计\n\n';
    const stats = await pool.query(`
      SELECT 
        (SELECT COUNT(*) FROM concepts) as total_concepts,
        (SELECT COUNT(*) FROM associations) as total_associations,
        (SELECT AVG(weight) FROM associations) as avg_weight
    `);
    
    text += `- 总概念数: ${stats.rows[0].total_concepts}\n`;
    text += `- 总关联数: ${stats.rows[0].total_associations}\n`;
    text += `- 平均关联强度: ${parseFloat(stats.rows[0].avg_weight).toFixed(3)}\n`;
    
    // 保存
    const textPath = path.join(OUTPUT_DIR, 'brain-network.txt');
    fs.writeFileSync(textPath, text);
    
    console.log(`✅ 文本图谱已保存: ${textPath}`);
    
    return { text, path: textPath };
    
  } finally {
    await pool.end();
  }
}

/**
 * 生成 HTML 交互式可视化
 */
async function generateHtmlGraph() {
  const { Pool } = resolveModule('pg');
  const pool = new Pool(config.storage.primary);
  
  try {
    console.log('\n📊 生成 HTML 交互式图谱...\n');
    
    // 获取数据
    const concepts = await pool.query(`
      SELECT id, name, access_count, importance
      FROM concepts
      ORDER BY importance DESC
      LIMIT 50
    `);
    
    const conceptIds = concepts.rows.map(c => `'${c.id}'`).join(',');
    
    const associations = await pool.query(`
      SELECT from_id, to_id, weight, type
      FROM associations
      WHERE from_id IN (${conceptIds}) AND to_id IN (${conceptIds})
      LIMIT 100
    `);
    
    // 生成 D3.js 可视化
    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Brain Network Visualization</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
    #graph { width: 100%; height: 800px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .node { cursor: pointer; }
    .node text { font-size: 12px; pointer-events: none; }
    .link { stroke-opacity: 0.6; }
    .controls { margin-bottom: 20px; }
    .info { position: absolute; top: 20px; right: 20px; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 250px; }
    h1 { color: #333; margin-bottom: 10px; }
    .stat { margin: 5px 0; color: #666; }
  </style>
</head>
<body>
  <h1>🧠 Cognitive Brain 知识网络</h1>
  <div class="controls">
    <button onclick="resetZoom()">重置视图</button>
    <button onclick="togglePhysics()">暂停/继续</button>
  </div>
  <div id="graph"></div>
  <div class="info">
    <h3>网络统计</h3>
    <div class="stat">节点: ${concepts.rows.length}</div>
    <div class="stat">边: ${associations.rows.length}</div>
    <div class="stat">点击节点查看详情</div>
  </div>

  <script>
    const nodes = ${JSON.stringify(concepts.rows)};
    const links = ${JSON.stringify(associations.rows.map(a => ({source: a.from_id, target: a.to_id, weight: a.weight, type: a.type})))};

    const width = document.getElementById('graph').clientWidth;
    const height = 800;

    const svg = d3.select('#graph').append('svg')
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g');

    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => g.attr('transform', event.transform));

    svg.call(zoom);

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => Math.max(20, (d.access_count || 0) * 3 + 15)));

    const link = g.append('g')
      .selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('class', 'link')
      .attr('stroke', '#999')
      .attr('stroke-width', d => Math.max(1, d.weight * 3));

    const node = g.append('g')
      .selectAll('g')
      .data(nodes)
      .enter().append('g')
      .attr('class', 'node')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    node.append('circle')
      .attr('r', d => Math.max(15, (d.access_count || 0) * 3 + 10))
      .attr('fill', d => d.importance > 0.7 ? '#ff6b6b' : d.importance > 0.4 ? '#4ecdc4' : '#95e1d3')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    node.append('text')
      .attr('dx', 0)
      .attr('dy', d => Math.max(15, (d.access_count || 0) * 3 + 10) + 15)
      .attr('text-anchor', 'middle')
      .text(d => d.name.length > 8 ? d.name.substring(0, 8) + '...' : d.name);

    node.append('title')
      .text(d => \`\${d.name}\\n重要性: \${(d.importance * 100).toFixed(1)}%\\n访问: \${d.access_count}\`);

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node.attr('transform', d => \`translate(\${d.x},\${d.y})\`);
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    function resetZoom() {
      svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
    }

    let physicsEnabled = true;
    function togglePhysics() {
      physicsEnabled = !physicsEnabled;
      simulation[physicsEnabled ? 'restart' : 'stop']();
    }
  </script>
</body>
</html>`;
    
    // 保存
    const htmlPath = path.join(OUTPUT_DIR, 'brain-network.html');
    fs.writeFileSync(htmlPath, html);
    
    console.log(`✅ HTML 交互式图谱已保存: ${htmlPath}`);
    console.log(`   用浏览器打开即可查看`);
    
    return { html, path: htmlPath };
    
  } finally {
    await pool.end();
  }
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const format = args[0] || 'all';
  
  console.log('🎨 Cognitive Brain 知识图谱可视化\n');
  console.log('=' .repeat(50));
  
  try {
    switch (format) {
      case 'dot':
        await generateDotGraph();
        break;
      case 'mermaid':
        await generateMermaidGraph();
        break;
      case 'text':
        await generateTextGraph();
        break;
      case 'html':
        await generateHtmlGraph();
        break;
      case 'all':
        await generateDotGraph();
        await generateMermaidGraph();
        await generateTextGraph();
        await generateHtmlGraph();
        break;
      default:
        console.log(`
用法:
  node visualize.cjs [format]

格式:
  dot      - Graphviz DOT 格式
  mermaid  - Mermaid 图表（Markdown）
  text     - 文本表格
  html     - D3.js 交互式可视化
  all      - 生成所有格式（默认）

输出目录: ${OUTPUT_DIR}
        `);
        return;
    }
    
    console.log('\n' + '='.repeat(50));
    console.log(`✨ 可视化完成！输出目录: ${OUTPUT_DIR}\n`);
    console.log('生成文件:');
    fs.readdirSync(OUTPUT_DIR).forEach(f => {
      const stats = fs.statSync(path.join(OUTPUT_DIR, f));
      console.log(`  - ${f} (${(stats.size / 1024).toFixed(1)} KB)`);
    });
    
  } catch (err) {
    console.error('❌ 错误:', err.message);
    process.exit(1);
  }
}

module.exports = {
  generateDotGraph,
  generateMermaidGraph,
  generateTextGraph,
  generateHtmlGraph
};

if (require.main === module) {
  main();
}
