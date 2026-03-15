/**
 * Smart Search Router - ClawHub Skill
 * 
 * Intelligently routes search queries between SearXNG and Gemini Search
 * based on query complexity to optimize token usage and response quality.
 */

// Tool implementation
async function smartSearch(params, context) {
  const { query, forceEngine, limit = 10 } = params;
  const { config, logger } = context;
  
  const pluginConfig = {
    searxngBaseUrl: config?.searxng?.baseUrl,
    searxngEngines: config?.searxng?.engines || "google,bing,duckduckgo",
    searxngLanguage: config?.searxng?.language || "zh-CN",
    geminiApiKey: config?.gemini?.apiKey,
    complexityThreshold: config?.complexityThreshold || 0.6,
    useGeminiForComplex: config?.useGeminiForComplex ?? true,
  };
  
  if (!pluginConfig.searxngBaseUrl) {
    throw new Error("SearXNG baseUrl is required. Please configure it in openclaw.json");
  }

  // Estimate query complexity (0-1)
  function estimateComplexity(q) {
    const queryLower = q.toLowerCase();
    const complexPatterns = [
      /\b(compare|vs|versus|difference|better|worse)\b/,
      /\b(analyze|analysis|explain|why|how|reason|cause)\b/,
      /\b(list.*and|compare.*with|what.*how|why.*what)\b/,
      /\b(evaluate|review|opinion|pros|cons|advantage|disadvantage)\b/,
      /\b(technical|architecture|implementation|algorithm|mechanism)\b/,
      /.{50,}/,
    ];
    const simplePatterns = [
      /\b(what time|when|today|tomorrow|date)\b/,
      /\b(weather|temperature|rain|sunny)\b/,
      /\b(what is|who is|where is|define|meaning)\b/,
      /\b(news|latest|recent|today)\b/,
      /\b(is|are|do|does|can|will)\b\s+\w+\s*\?$/,
    ];
    
    let score = 0;
    for (const pattern of complexPatterns) {
      if (pattern.test(queryLower)) score += 0.2;
    }
    for (const pattern of simplePatterns) {
      if (pattern.test(queryLower)) score -= 0.15;
    }
    if (queryLower.length > 80) score += 0.1;
    if (queryLower.length > 120) score += 0.1;
    if (/\b(why|how)\b/.test(queryLower)) score += 0.1;
    return Math.max(0, Math.min(1, score));
  }

  // SearXNG search
  async function searxngSearch(query, options = {}) {
    const url = new URL(`${pluginConfig.searxngBaseUrl}/search`);
    url.searchParams.set("q", query);
    url.searchParams.set("engines", options.engines || pluginConfig.searxngEngines);
    url.searchParams.set("language", options.language || pluginConfig.searxngLanguage);
    url.searchParams.set("format", "json");
    
    const response = await fetch(url.toString(), {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(15000),
    });
    
    if (!response.ok) throw new Error(`SearXNG error: ${response.status}`);
    const data = await response.json();
    
    return {
      source: "searxng",
      query: data.query,
      results: (data.results || []).slice(0, limit).map(item => ({
        title: item.title,
        url: item.url,
        snippet: item.content || item.snippet || "",
        source: item.engine || "unknown",
      })),
      suggestions: data.suggestions || [],
      total: data.number_of_results || 0,
    };
  }

  // Gemini search
  async function geminiSearch(query) {
    if (!pluginConfig.geminiApiKey) {
      throw new Error("Gemini API key not configured");
    }
    
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${pluginConfig.geminiApiKey}`;
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: `Search and answer: ${query}. Provide concise answer with sources.` }] }],
        generationConfig: { maxOutputTokens: 2048, temperature: 0.7 },
        tools: [{ googleSearch: {} }]
      }),
      signal: AbortSignal.timeout(20000),
    });
    
    if (!response.ok) throw new Error(`Gemini error: ${response.status}`);
    const data = await response.json();
    
    return {
      source: "gemini",
      answer: data.candidates?.[0]?.content?.parts?.[0]?.text || "",
      groundingMetadata: data.candidates?.[0]?.groundingMetadata || null,
    };
  }

  // Route decision
  let useGemini = false;
  let complexity = 0;
  
  if (forceEngine === "gemini") {
    useGemini = true;
    complexity = 1.0;
  } else if (forceEngine === "searxng") {
    useGemini = false;
    complexity = 0.0;
  } else {
    complexity = estimateComplexity(query);
    useGemini = complexity >= pluginConfig.complexityThreshold && pluginConfig.useGeminiForComplex;
  }
  
  logger?.info(`Smart search: "${query}" (complexity: ${complexity.toFixed(2)}, engine: ${useGemini ? "Gemini" : "SearXNG"})`);
  
  // Execute search
  let result;
  if (useGemini) {
    result = await geminiSearch(query);
  } else {
    result = await searxngSearch(query);
  }
  
  return {
    engine: useGemini ? "gemini" : "searxng",
    complexity,
    query,
    ...result,
  };
}

// Export tools for ClawHub Skill
export const tools = {
  smart_search: {
    description: "Intelligently search the web using SearXNG (for simple queries) or Gemini Search (for complex queries) to optimize token usage and answer quality.",
    execute: smartSearch,
  },
};

// Default export for compatibility
export default {
  tools,
};
