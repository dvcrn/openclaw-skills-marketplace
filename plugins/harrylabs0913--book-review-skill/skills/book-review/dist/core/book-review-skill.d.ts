import { UserInput, SkillOutput, SkillConfig } from '../types';
export declare class BookReviewSkill {
    private parser;
    private searcher;
    private generator;
    private formatter;
    private config;
    constructor(config: SkillConfig);
    process(input: UserInput): Promise<SkillOutput>;
    private validateInput;
    private validateOption;
    private handleError;
    testConnection(): Promise<boolean>;
    getStatistics(): Promise<{
        noteCount: number;
        lastIndexTime: Date | null;
        config: Partial<SkillConfig>;
    }>;
    batchProcess(inputs: UserInput[]): Promise<SkillOutput[]>;
    updateConfig(newConfig: Partial<SkillConfig>): void;
    getConfig(): SkillConfig;
}
//# sourceMappingURL=book-review-skill.d.ts.map