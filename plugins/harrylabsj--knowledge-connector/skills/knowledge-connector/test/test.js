const KnowledgeConnector = require('../src/index.js');
const assert = require('assert');

async function runTests() {
  console.log('🧪 开始运行测试...\n');
  
  const kc = new KnowledgeConnector();
  let passed = 0;
  let failed = 0;
  
  // 测试 1: 提取概念
  try {
    const concepts = await kc.extract('人工智能是机器学习的基础，深度学习是人工智能的重要分支');
    assert(concepts.length > 0, '应该提取到概念');
    console.log('✅ 测试 1: 概念提取 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 1: 概念提取 - 失败:', e.message);
    failed++;
  }
  
  // 测试 2: 保存概念
  try {
    const concepts = await kc.extract('测试概念 A 和测试概念 B');
    await kc.saveConcepts(concepts);
    const saved = kc.loadConcepts();
    assert(saved.length > 0, '应该保存了概念');
    console.log('✅ 测试 2: 保存概念 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 2: 保存概念 - 失败:', e.message);
    failed++;
  }
  
  // 测试 3: 建立关联
  try {
    const concepts = kc.loadConcepts();
    if (concepts.length >= 2) {
      await kc.connect({
        from: concepts[0].name,
        to: concepts[1].name,
        type: '相关'
      });
      console.log('✅ 测试 3: 建立关联 - 通过');
      passed++;
    } else {
      console.log('⚠️  测试 3: 建立关联 - 跳过 (概念不足)');
    }
  } catch (e) {
    console.log('❌ 测试 3: 建立关联 - 失败:', e.message);
    failed++;
  }
  
  // 测试 4: 搜索
  try {
    const results = await kc.search('测试');
    console.log('✅ 测试 4: 搜索功能 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 4: 搜索功能 - 失败:', e.message);
    failed++;
  }
  
  // 测试 5: 统计信息
  try {
    const stats = await kc.getStats();
    assert(typeof stats.conceptCount === 'number', '应该有概念数量');
    console.log('✅ 测试 5: 统计信息 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 5: 统计信息 - 失败:', e.message);
    failed++;
  }
  
  // 测试 6: 可视化
  try {
    const html = await kc.visualize({ format: 'html' });
    assert(html.includes('<html>'), '应该生成 HTML');
    console.log('✅ 测试 6: 可视化 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 6: 可视化 - 失败:', e.message);
    failed++;
  }
  
  // 测试 7: 导出
  try {
    const data = await kc.export();
    assert(data.concepts, '应该有概念数据');
    assert(data.relations, '应该有关系数据');
    console.log('✅ 测试 7: 导出功能 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 7: 导出功能 - 失败:', e.message);
    failed++;
  }
  
  // 测试 8: 推荐
  try {
    const concepts = kc.loadConcepts();
    if (concepts.length > 0) {
      const recommendations = await kc.recommend(concepts[0].name, 3);
      console.log('✅ 测试 8: 推荐功能 - 通过');
      passed++;
    } else {
      console.log('⚠️  测试 8: 推荐功能 - 跳过 (概念不足)');
    }
  } catch (e) {
    console.log('❌ 测试 8: 推荐功能 - 失败:', e.message);
    failed++;
  }
  
  console.log('\n' + '='.repeat(40));
  console.log(`测试结果: ${passed} 通过, ${failed} 失败`);
  console.log('='.repeat(40));
  
  process.exit(failed > 0 ? 1 : 0);
}

runTests();
