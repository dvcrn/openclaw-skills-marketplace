const fs = require('fs');
const path = require('path');
const os = require('os');

class KnowledgeConnector {
  constructor(options = {}) {
    this.dataDir = options.dataDir || path.join(os.homedir(), '.local', 'share', 'knowledge-connector');
    this.conceptsFile = path.join(this.dataDir, 'concepts.json');
    this.relationsFile = path.join(this.dataDir, 'relations.json');
    
    this.init();
  }
  
  init() {
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }
    
    if (!fs.existsSync(this.conceptsFile)) {
      fs.writeFileSync(this.conceptsFile, JSON.stringify([]));
    }
    
    if (!fs.existsSync(this.relationsFile)) {
      fs.writeFileSync(this.relationsFile, JSON.stringify([]));
    }
  }
  
  // 加载概念
  loadConcepts() {
    try {
      const data = fs.readFileSync(this.conceptsFile, 'utf-8');
      return JSON.parse(data);
    } catch {
      return [];
    }
  }
  
  // 保存概念
  saveConceptsData(concepts) {
    fs.writeFileSync(this.conceptsFile, JSON.stringify(concepts, null, 2));
  }
  
  // 加载关系
  loadRelations() {
    try {
      const data = fs.readFileSync(this.relationsFile, 'utf-8');
      return JSON.parse(data);
    } catch {
      return [];
    }
  }
  
  // 保存关系
  saveRelationsData(relations) {
    fs.writeFileSync(this.relationsFile, JSON.stringify(relations, null, 2));
  }
  
  // 生成 UUID
  generateId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
  
  // 提取概念
  async extract(text, options = {}) {
    const concepts = [];
    
    // 提取引号中的内容作为概念
    const quotedPattern = /["""']([^"""']+)["""']/g;
    let match;
    while ((match = quotedPattern.exec(text)) !== null) {
      const name = match[1].trim();
      if (name.length > 1 && name.length < 50) {
        concepts.push({
          id: this.generateId(),
          name: name,
          type: 'term',
          source: text.substring(0, 100),
          createdAt: new Date().toISOString()
        });
      }
    }
    
    // 提取大写专有名词
    const properNounPattern = /[A-Z][a-zA-Z\s]{1,20}(?=[\s,;.!?：，。！])/g;
    while ((match = properNounPattern.exec(text)) !== null) {
      const name = match[0].trim();
      if (name.length > 1 && !concepts.find(c => c.name === name)) {
        concepts.push({
          id: this.generateId(),
          name: name,
          type: 'proper-noun',
          source: text.substring(0, 100),
          createdAt: new Date().toISOString()
        });
      }
    }
    
    // 提取中文专有名词（连续的2-8个汉字）
    const chinesePattern = /[\u4e00-\u9fa5]{2,8}/g;
    while ((match = chinesePattern.exec(text)) !== null) {
      const name = match[0];
      // 过滤常见停用词
      const stopWords = ['这是', '那是', '一个', '一些', '可以', '进行', '需要', '通过', '根据', '关于'];
      if (!stopWords.includes(name) && !concepts.find(c => c.name === name)) {
        concepts.push({
          id: this.generateId(),
          name: name,
          type: 'concept',
          source: text.substring(0, 100),
          createdAt: new Date().toISOString()
        });
      }
    }
    
    // 提取技术术语
    const techTerms = [
      '人工智能', '机器学习', '深度学习', '神经网络', '自然语言处理',
      '计算机视觉', '数据挖掘', '算法', '模型', '训练', '推理',
      'Python', 'JavaScript', 'Java', 'TypeScript', 'Node.js',
      'React', 'Vue', 'Angular', '数据库', 'API', '微服务',
      '云计算', '大数据', '区块链', '物联网', '5G', '边缘计算'
    ];
    
    techTerms.forEach(term => {
      if (text.includes(term) && !concepts.find(c => c.name === term)) {
        concepts.push({
          id: this.generateId(),
          name: term,
          type: 'tech',
          source: text.substring(0, 100),
          createdAt: new Date().toISOString()
        });
      }
    });
    
    // 去重
    const uniqueConcepts = [];
    const seen = new Set();
    for (const concept of concepts) {
      if (!seen.has(concept.name)) {
        seen.add(concept.name);
        uniqueConcepts.push(concept);
      }
    }
    
    return uniqueConcepts;
  }
  
  // 保存概念到知识库
  async saveConcepts(newConcepts) {
    const existing = this.loadConcepts();
    
    for (const concept of newConcepts) {
      if (!existing.find(c => c.name === concept.name)) {
        existing.push(concept);
      }
    }
    
    this.saveConceptsData(existing);
    return newConcepts;
  }
  
  // 建立关联
  async connect(options) {
    const { from, to, type = '相关', weight = 0.5 } = options;
    
    const concepts = this.loadConcepts();
    const fromConcept = concepts.find(c => c.name === from);
    const toConcept = concepts.find(c => c.name === to);
    
    if (!fromConcept) {
      throw new Error(`源概念不存在: ${from}`);
    }
    
    if (!toConcept) {
      throw new Error(`目标概念不存在: ${to}`);
    }
    
    const relations = this.loadRelations();
    
    // 检查是否已存在
    const existing = relations.find(r => 
      r.from === fromConcept.id && r.to === toConcept.id && r.type === type
    );
    
    if (existing) {
      return existing;
    }
    
    const relation = {
      id: this.generateId(),
      from: fromConcept.id,
      to: toConcept.id,
      type: type,
      weight: weight,
      createdAt: new Date().toISOString()
    };
    
    relations.push(relation);
    this.saveRelationsData(relations);
    
    return relation;
  }
  
  // 自动建立关联
  async autoConnect() {
    const concepts = this.loadConcepts();
    const relations = this.loadRelations();
    const newRelations = [];
    
    // 基于共现建立关联
    for (let i = 0; i < concepts.length; i++) {
      for (let j = i + 1; j < concepts.length; j++) {
        const c1 = concepts[i];
        const c2 = concepts[j];
        
        // 检查是否已有关联
        const existing = relations.find(r => 
          (r.from === c1.id && r.to === c2.id) ||
          (r.from === c2.id && r.to === c1.id)
        );
        
        if (!existing) {
          // 基于名称相似度建立关联
          const similarity = this.calculateSimilarity(c1.name, c2.name);
          if (similarity > 0.3) {
            const relation = {
              id: this.generateId(),
              from: c1.id,
              to: c2.id,
              type: similarity > 0.7 ? '相似' : '相关',
              weight: similarity,
              createdAt: new Date().toISOString()
            };
            relations.push(relation);
            newRelations.push(relation);
          }
        }
      }
    }
    
    this.saveRelationsData(relations);
    return newRelations;
  }
  
  // 计算字符串相似度
  calculateSimilarity(s1, s2) {
    const set1 = new Set(s1);
    const set2 = new Set(s2);
    const intersection = new Set([...set1].filter(x => set2.has(x)));
    const union = new Set([...set1, ...set2]);
    return intersection.size / union.size;
  }
  
  // 导入关系
  async importRelations(data) {
    const relations = this.loadRelations();
    const concepts = this.loadConcepts();
    const newRelations = [];
    
    for (const item of data) {
      const fromConcept = concepts.find(c => c.name === item.from || c.id === item.from);
      const toConcept = concepts.find(c => c.name === item.to || c.id === item.to);
      
      if (fromConcept && toConcept) {
        const relation = {
          id: this.generateId(),
          from: fromConcept.id,
          to: toConcept.id,
          type: item.type || '相关',
          weight: item.weight || 0.5,
          createdAt: new Date().toISOString()
        };
        relations.push(relation);
        newRelations.push(relation);
      }
    }
    
    this.saveRelationsData(relations);
    return newRelations;
  }
  
  // 搜索概念
  async search(keyword) {
    const concepts = this.loadConcepts();
    const results = concepts.filter(c => 
      c.name.toLowerCase().includes(keyword.toLowerCase()) ||
      (c.description && c.description.toLowerCase().includes(keyword.toLowerCase())) ||
      (c.aliases && c.aliases.some(a => a.toLowerCase().includes(keyword.toLowerCase())))
    );
    return results;
  }
  
  // 获取概念
  async getConcept(name) {
    const concepts = this.loadConcepts();
    return concepts.find(c => c.name === name);
  }
  
  // 获取关联概念
  async getRelated(conceptId) {
    const relations = this.loadRelations();
    const concepts = this.loadConcepts();
    
    const relatedRelations = relations.filter(r => 
      r.from === conceptId || r.to === conceptId
    );
    
    return relatedRelations.map(r => {
      const otherId = r.from === conceptId ? r.to : r.from;
      const otherConcept = concepts.find(c => c.id === otherId);
      return {
        ...otherConcept,
        relationType: r.type,
        relationWeight: r.weight
      };
    }).filter(Boolean);
  }
  
  // 自然语言查询
  async ask(question) {
    // 简单实现：提取关键词并搜索
    const keywords = question.match(/[\u4e00-\u9fa5]{2,}|[a-zA-Z]{3,}/g) || [];
    const results = [];
    
    for (const keyword of keywords) {
      const found = await this.search(keyword);
      results.push(...found);
    }
    
    // 去重
    const unique = [];
    const seen = new Set();
    for (const r of results) {
      if (!seen.has(r.id)) {
        seen.add(r.id);
        unique.push(r);
      }
    }
    
    return {
      answer: unique.length > 0 
        ? `找到 ${unique.length} 个相关概念: ${unique.map(c => c.name).join(', ')}`
        : '未找到相关信息',
      concepts: unique
    };
  }
  
  // 可视化
  async visualize(options = {}) {
    const { format = 'html', concept, depth = 2 } = options;
    
    const concepts = this.loadConcepts();
    const relations = this.loadRelations();
    
    let filteredConcepts = concepts;
    let filteredRelations = relations;
    
    // 如果指定了中心概念，过滤相关子图
    if (concept) {
      const centerConcept = concepts.find(c => c.name === concept);
      if (centerConcept) {
        const relatedIds = new Set([centerConcept.id]);
        
        // BFS 遍历
        for (let i = 0; i < depth; i++) {
          const currentIds = new Set(relatedIds);
          for (const r of relations) {
            if (currentIds.has(r.from) || currentIds.has(r.to)) {
              relatedIds.add(r.from);
              relatedIds.add(r.to);
            }
          }
        }
        
        filteredConcepts = concepts.filter(c => relatedIds.has(c.id));
        filteredRelations = relations.filter(r => 
          relatedIds.has(r.from) && relatedIds.has(r.to)
        );
      }
    }
    
    if (format === 'json') {
      return JSON.stringify({
        concepts: filteredConcepts,
        relations: filteredRelations
      }, null, 2);
    }
    
    if (format === 'dot') {
      let dot = 'digraph KnowledgeGraph {\n';
      dot += '  rankdir=LR;\n';
      dot += '  node [shape=box, style=rounded];\n\n';
      
      for (const c of filteredConcepts) {
        dot += `  "${c.id}" [label="${c.name}"];\n`;
      }
      
      dot += '\n';
      
      for (const r of filteredRelations) {
        dot += `  "${r.from}" -> "${r.to}" [label="${r.type}"];\n`;
      }
      
      dot += '}';
      return dot;
    }
    
    // HTML 格式
    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>知识图谱</title>
  <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
    #graph { width: 100%; height: 600px; border: 1px solid #ddd; }
    h1 { color: #333; }
    .stats { margin: 10px 0; color: #666; }
  </style>
</head>
<body>
  <h1>知识图谱</h1>
  <div class="stats">概念: ${filteredConcepts.length} | 关系: ${filteredRelations.length}</div>
  <div id="graph"></div>
  <script>
    const nodes = new vis.DataSet(${JSON.stringify(filteredConcepts.map(c => ({
      id: c.id,
      label: c.name,
      title: c.description || c.name,
      color: c.type === 'tech' ? '#e3f2fd' : '#f5f5f5'
    })))});
    
    const edges = new vis.DataSet(${JSON.stringify(filteredRelations.map(r => ({
      from: r.from,
      to: r.to,
      label: r.type,
      arrows: 'to'
    })))});
    
    const container = document.getElementById('graph');
    const data = { nodes: nodes, edges: edges };
    const options = {
      nodes: {
        shape: 'box',
        margin: 10,
        font: { size: 14 }
      },
      edges: {
        font: { size: 12 },
        smooth: { type: 'continuous' }
      },
      physics: {
        stabilization: false
      }
    };
    
    new vis.Network(container, data, options);
  </script>
</body>
</html>`;
    
    return html;
  }
  
  // 获取统计信息
  async getStats() {
    const concepts = this.loadConcepts();
    const relations = this.loadRelations();
    
    const types = new Set(concepts.map(c => c.type).filter(Boolean));
    
    const stats = {
      conceptCount: concepts.length,
      relationCount: relations.length,
      typeCount: types.size,
      dataSize: this.getDataSize()
    };
    
    return stats;
  }
  
  // 获取数据大小
  getDataSize() {
    try {
      const conceptsSize = fs.statSync(this.conceptsFile).size;
      const relationsSize = fs.statSync(this.relationsFile).size;
      const total = conceptsSize + relationsSize;
      
      if (total < 1024) return `${total} B`;
      if (total < 1024 * 1024) return `${(total / 1024).toFixed(2)} KB`;
      return `${(total / (1024 * 1024)).toFixed(2)} MB`;
    } catch {
      return '0 B';
    }
  }
  
  // 导出
  async export() {
    return {
      concepts: this.loadConcepts(),
      relations: this.loadRelations(),
      exportedAt: new Date().toISOString()
    };
  }
  
  // 导入
  async import(data) {
    if (data.concepts) {
      this.saveConceptsData(data.concepts);
    }
    if (data.relations) {
      this.saveRelationsData(data.relations);
    }
  }
  
  // 清空
  async clear() {
    this.saveConceptsData([]);
    this.saveRelationsData([]);
  }
  
  // 推荐
  async recommend(conceptName, limit = 5) {
    const concept = await this.getConcept(conceptName);
    if (!concept) {
      return [];
    }
    
    const related = await this.getRelated(concept.id);
    
    // 按权重排序
    const sorted = related
      .sort((a, b) => b.relationWeight - a.relationWeight)
      .slice(0, limit);
    
    return sorted.map(r => ({
      id: r.id,
      name: r.name,
      type: r.type,
      score: r.relationWeight,
      reason: `与 ${conceptName} 存在"${r.relationType}"关系`
    }));
  }
}

module.exports = KnowledgeConnector;
