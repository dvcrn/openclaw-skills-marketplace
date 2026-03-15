import { ParsedInsight, NoteSearchResult, ReviewResult } from '../types';
export declare class ReviewGenerator {
    private aiProvider;
    private model;
    private temperature;
    private maxTokens;
    private apiKey;
    constructor(aiProvider?: 'deepseek' | 'openai' | 'local', model?: string, temperature?: number, maxTokens?: number);
    generate(parsed: ParsedInsight, notes: NoteSearchResult[]): Promise<ReviewResult>;
    private prepareContext;
    private generateWithAI;
    private generateWithDeepSeek;
    private generateWithOpenAI;
    private generateWithTemplate;
    private buildSystemPrompt;
    private buildPrompt;
    private postProcess;
    private extractReferences;
    private generateSuggestions;
    private calculateConfidence;
    private getApiKey;
}
//# sourceMappingURL=review-generator.d.ts.map