/**
 * OpenClaw Smart Search Router Plugin
 * 
 * Intelligently routes search queries between SearXNG and Gemini Search
 * based on query complexity to optimize token usage and response quality.
 * 
 * Routing Rules:
 * - Simple queries (facts, news, weather) → SearXNG (saves ~40% tokens)
 * - Complex queries (analysis, comparison, deep dive) → Gemini Search (better quality)
 */

export default async function(api) {
  const { logger, config } = api;

  const pluginConfig = {
    // SearXNG config
    searxngBaseUrl: config?.searxng?.baseUrl,
    searxngEngines: config?.searxng?.engines || "google,bing,duckduckgo",
    searxngLanguage: config?.searxng?.language || "zh-CN",
    
    // Gemini config (fallback)
    geminiApiKey: config?.gemini?.apiKey || process.env.GEMINI_API_KEY,
    
    // Routing thresholds
    complexityThreshold: config?.complexityThreshold || 0.6,
    useGeminiForComplex: config?.useGeminiForComplex ?? true,
  };

  logger.info(`Smart Search Router loaded (SearXNG: ${pluginConfig.searxngBaseUrl})`);

  // ============================================================================
  // Helper: Estimate query complexity (0-1)
  // ============================================================================
  
  function estimateComplexity(query) {
    const q = query.toLowerCase();
    
    // Complexity indicators
    const complexPatterns = [
      // Comparison questions
      /\b(compare|vs|versus|difference|better|worse)\b/,
      // Analysis questions
      /\b(analyze|analysis|explain|why|how|reason|cause)\b/,
      // Multi-step questions
      /\b(list.*and|compare.*with|what.*how|why.*what)\b/,
      // Opinion/evaluation
      /\b(evaluate|review|opinion|pros|cons|advantage|disadvantage)\b/,
      // Technical depth
      /\b(technical|architecture|implementation|algorithm|mechanism)\b/,
      // Long queries (>50 chars tend to be more complex)
      /.{50,}/,
    ];
    
    // Simple patterns (factual, quick answers)
    const simplePatterns = [
      // Time/date questions
      /\b(what time|when|today|tomorrow|date)\b/,
      // Weather
      /\b(weather|temperature|rain|sunny)\b/,
      // Simple facts
      /\b(what is|who is|where is|define|meaning)\b/,
      // News
      /\b(news|latest|recent|today)\b/,
      // Yes/No questions
      /\b(is|are|do|does|can|will)\b\s+\w+\s*\?$/,
    ];
    
    let complexityScore = 0;
    
    // Add complexity for each complex pattern match
    for (const pattern of complexPatterns) {
      if (pattern.test(q)) {
        complexityScore += 0.2;
      }
    }
    
    // Reduce complexity for simple patterns
    for (const pattern of simplePatterns) {
      if (pattern.test(q)) {
        complexityScore -= 0.15;
      }
    }
    
    // Length factor
    if (q.length > 80) complexityScore += 0.1;
    if (q.length > 120) complexityScore += 0.1;
    
    // Question word factor
    if (/\b(why|how)\b/.test(q)) complexityScore += 0.1;
    
    // Normalize to 0-1
    return Math.max(0, Math.min(1, complexityScore));
  }

  // ============================================================================
  // Helper: SearXNG Search
  // ============================================================================
  
  async function searxngSearch(query, options = {}) {
    const { engines = pluginConfig.searxngEngines, language = pluginConfig.searxngLanguage, limit = 10 } = options;
    
    const url = new URL(`${pluginConfig.searxngBaseUrl}/search`);
    url.searchParams.set("q", query);
    url.searchParams.set("engines", engines);
    url.searchParams.set("language", language);
    url.searchParams.set("format", "json");
    
    const response = await fetch(url.toString(), {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(15000),
    });
    
    if (!response.ok) {
      throw new Error(`SearXNG error: ${response.status}`);
    }
    
    const data = await response.json();
    
    return {
      source: "searxng",
      query: data.query,
      results: data.results.slice(0, limit).map(item => ({
        title: item.title,
        url: item.url,
        snippet: item.content || item.snippet || "",
        source: item.engine || "unknown",
      })),
      suggestions: data.suggestions || [],
      total: data.number_of_results || 0,
    };
  }

  // ============================================================================
  // Helper: Gemini Search (fallback for complex queries)
  // ============================================================================
  
  async function geminiSearch(query, options = {}) {
    const { limit = 5 } = options;
    
    if (!pluginConfig.geminiApiKey) {
      throw new Error("Gemini API key not configured");
    }
    
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${pluginConfig.geminiApiKey}`;
    
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: `Search and answer: ${query}. Provide a concise answer with key facts and sources.`
          }]
        }],
        generationConfig: {
          maxOutputTokens: 2048,
          temperature: 0.7,
        },
        tools: [{
          googleSearch: {}
        }]
      }),
      signal: AbortSignal.timeout(20000),
    });
    
    if (!response.ok) {
      throw new Error(`Gemini error: ${response.status}`);
    }
    
    const data = await response.json();
    
    return {
      source: "gemini",
      answer: data.candidates?.[0]?.content?.parts?.[0]?.text || "",
      groundingMetadata: data.candidates?.[0]?.groundingMetadata || null,
    };
  }

  // ============================================================================
  // Smart Search Tool
  // ============================================================================
  
  api.registerTool(
    {
      name: "smart_search",
      label: "Smart Search",
      description: "Intelligently search the web using SearXNG (for simple queries) or Gemini Search (for complex queries) to optimize token usage and answer quality.",
      parameters: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "Search query string",
          },
          forceEngine: {
            type: "string",
            description: "Force use of specific engine (optional): 'searxng' or 'gemini'",
            enum: ["searxng", "gemini"],
          },
          limit: {
            type: "number",
            description: "Maximum results to return (default: 10)",
            minimum: 1,
            maximum: 50,
          },
        },
        required: ["query"],
      },
      execute: async (toolCallId, params, signal) => {
        const { query, forceEngine, limit = 10 } = params;
        
        try {
          // Determine which engine to use
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
          
          const engine = useGemini ? "Gemini Search" : "SearXNG";
          logger.info(`Smart search: "${query}" (complexity: ${complexity.toFixed(2)}, engine: ${engine})`);
          
          let result;
          if (useGemini) {
            result = await geminiSearch(query, { limit });
          } else {
            result = await searxngSearch(query, { limit });
          }
          
          return {
            content: `Search completed using ${engine} (complexity: ${complexity.toFixed(2)})`,
            details: {
              engine: useGemini ? "gemini" : "searxng",
              complexity,
              query,
              ...result,
            },
          };
        } catch (error) {
          logger.error(`Smart search failed: ${error.message}`);
          
          // Fallback: try the other engine
          try {
            logger.info(`Falling back to alternative engine...`);
            const fallbackResult = await searxngSearch(query, { limit });
            return {
              content: `Search completed using SearXNG (fallback)`,
              details: {
                engine: "searxng",
                fallback: true,
                query,
                ...fallbackResult,
              },
            };
          } catch (fallbackError) {
            return {
              content: `Search failed: ${error.message}`,
              details: {
                status: "error",
                message: error.message,
                query,
              },
            };
          }
        }
      },
    },
    { name: "smart_search" },
  );

  // ============================================================================
  // Lifecycle
  // ============================================================================
  
  return {
    async shutdown() {
      logger.info("Smart Search Router shutting down");
    },
  };
}
