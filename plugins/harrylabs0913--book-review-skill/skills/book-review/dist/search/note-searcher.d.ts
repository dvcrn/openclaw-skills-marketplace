import { ParsedInsight, NoteSearchResult } from '../types';
export declare class NoteSearcher {
    private notePaths;
    private maxResults;
    private minRelevanceScore;
    private index;
    private documents;
    private lastIndexTime;
    private indexUpdateInterval;
    constructor(notePaths: string[], maxResults?: number, minRelevanceScore?: number);
    search(parsed: ParsedInsight): Promise<NoteSearchResult[]>;
    private ensureIndexUpdated;
    private buildIndex;
    private collectNoteFiles;
    private processNoteFile;
    private extractTitle;
    private extractMetadata;
    private extractTags;
    private cleanContent;
    private buildSearchQuery;
    private executeSearch;
    private filterResults;
    private formatResults;
    private extractExcerpt;
    private determineMatchType;
    private resolvePath;
}
//# sourceMappingURL=note-searcher.d.ts.map