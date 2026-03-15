import { ReviewResult, SkillOutput, OutputFormat } from '../types';
export declare class OutputFormatter {
    format(review: ReviewResult, format?: OutputFormat): SkillOutput;
    private formatMarkdown;
    private formatPlain;
    private formatHtml;
    private extractThemes;
    private escapeHtml;
    formatForConsole(review: ReviewResult): string;
    formatForClipboard(review: ReviewResult): string;
    formatForSharing(review: ReviewResult): string;
}
//# sourceMappingURL=formatter.d.ts.map