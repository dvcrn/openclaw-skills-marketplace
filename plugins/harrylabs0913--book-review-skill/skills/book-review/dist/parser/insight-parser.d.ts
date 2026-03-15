import { ParsedInsight } from '../types';
export declare class InsightParser {
    constructor();
    parse(text: string): Promise<ParsedInsight>;
    private preprocess;
    private detectLanguage;
    private extractKeywords;
    private extractChineseKeywords;
    private extractEnglishKeywords;
    private simpleChineseKeywordExtraction;
    private isStopWord;
    private identifyThemes;
    private analyzeEmotion;
    private assessComplexity;
}
//# sourceMappingURL=insight-parser.d.ts.map