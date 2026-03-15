import { z } from 'zod';
import * as fs from 'fs';
import * as path from 'path';
import { spawn } from 'child_process';

const MEMORY_FILE = path.join(process.cwd(), 'memory', 'vector-memory.json');
const OLLAMA_HOST = 'http://localhost:11434';

// 确保记忆文件存在
function ensureMemoryFile() {
  const dir = path.dirname(MEMORY_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  if (!fs.existsSync(MEMORY_FILE)) {
    fs.writeFileSync(MEMORY_FILE, JSON.stringify({ memories: [] }, null, 2));
  }
}

// 加载记忆
function loadMemories() {
  ensureMemoryFile();
  const data = fs.readFileSync(MEMORY_FILE, 'utf-8');
  return JSON.parse(data).memories;
}

// 保存记忆
function saveMemories(memories: any[]) {
  fs.writeFileSync(MEMORY_FILE, JSON.stringify({ memories }, null, 2));
}

// 调用 Ollama 获取 embedding
async function getEmbedding(text: string): Promise<number[]> {
  return new Promise((resolve, reject) => {
    const proc = spawn('curl', [
      '-s', OLLAMA_HOST + '/api/embeddings',
      '-d', JSON.stringify({ model: 'nomic-embed-text', prompt: text })
    ], { shell: true });

    let data = '';
    proc.stdout.on('data', (chunk) => { data += chunk; });
    proc.on('close', (code) => {
      if (code !== 0) reject(new Error(`curl failed: ${code}`));
      try {
        const json = JSON.parse(data);
        resolve(json.embedding);
      } catch (e) {
        reject(new Error(`Parse error: ${data}`));
      }
    });
    proc.on('error', reject);
  });
}

// 余弦相似度
function cosineSimilarity(a: number[], b: number[]): number {
  const dot = a.reduce((sum, v, i) => sum + v * b[i], 0);
  const magA = Math.sqrt(a.reduce((sum, v) => sum + v * v, 0));
  const magB = Math.sqrt(b.reduce((sum, v) => sum + v * v, 0));
  if (magA === 0 || magB === 0) return 0;
  return dot / (magA * magB);
}

export const riverMemory = {
  name: 'river_memory',
  description: '本地向量记忆管理 - 存储和搜索语义记忆',
  schema: {
    memory_store: {
      description: '存储重要信息到记忆库',
      input: z.object({
        content: z.string().describe('要记忆的内容'),
        category: z.enum(['fact', 'preference', 'decision', 'other']).optional().default('other'),
        importance: z.number().min(0).max(10).optional().default(5)
      })
    },
    memory_search: {
      description: '语义搜索记忆',
      input: z.object({
        query: z.string().describe('搜索查询'),
        limit: z.number().optional().default(5),
        threshold: z.number().optional().default(0.3)
      })
    },
    memory_list: {
      description: '列出所有记忆',
      input: z.object({
        limit: z.number().optional().default(20)
      })
    },
    memory_delete: {
      description: '删除记忆',
      input: z.object({
        id: z.string().describe('记忆ID')
      })
    }
  },

  async memory_store({ content, category = 'other', importance = 5 }) {
    console.log('[RiverMemory] Storing:', content.substring(0, 50) + '...');
    
    try {
      const embedding = await getEmbedding(content);
      const memories = loadMemories();
      
      const memory = {
        id: Date.now().toString(36) + Math.random().toString(36).substr(2, 9),
        content,
        category,
        importance,
        embedding,
        createdAt: new Date().toISOString()
      };
      
      memories.push(memory);
      saveMemories(memories);
      
      return { success: true, id: memory.id, count: memories.length };
    } catch (e: any) {
      return { success: false, error: e.message };
    }
  },

  async memory_search({ query, limit = 5, threshold = 0.3 }) {
    console.log('[RiverMemory] Searching:', query);
    
    try {
      const queryEmbedding = await getEmbedding(query);
      const memories = loadMemories();
      
      // 计算相似度
      const results = memories
        .map(m => ({
          ...m,
          similarity: cosineSimilarity(queryEmbedding, m.embedding)
        }))
        .filter(m => m.similarity >= threshold)
        .sort((a, b) => b.similarity - a.similarity)
        .slice(0, limit);
      
      return { 
        success: true, 
        results: results.map(r => ({
          id: r.id,
          content: r.content,
          category: r.category,
          similarity: Math.round(r.similarity * 100) / 100,
          createdAt: r.createdAt
        })),
        total: memories.length
      };
    } catch (e: any) {
      return { success: false, error: e.message };
    }
  },

  async memory_list({ limit = 20 }) {
    const memories = loadMemories();
    const recent = memories.slice(-limit).reverse();
    
    return {
      success: true,
      memories: recent.map(m => ({
        id: m.id,
        content: m.content.substring(0, 100) + (m.content.length > 100 ? '...' : ''),
        category: m.category,
        createdAt: m.createdAt
      })),
      total: memories.length
    };
  },

  async memory_delete({ id }) {
    const memories = loadMemories();
    const filtered = memories.filter(m => m.id !== id);
    
    if (filtered.length === memories.length) {
      return { success: false, error: 'Memory not found' };
    }
    
    saveMemories(filtered);
    return { success: true, remaining: filtered.length };
  }
};

export default riverMemory;
