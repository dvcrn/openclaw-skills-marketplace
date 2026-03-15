/**
 * PicSee API client — thin wrapper over the REST endpoints.
 */
export interface ShortenParams {
    url: string;
    domain?: string;
    externalId?: string;
    encodeId?: string;
    title?: string;
    description?: string;
    imageUrl?: string;
    tags?: string[];
    fbPixel?: string;
    gTag?: string;
    utm?: Record<string, string>;
}
export interface ListParams {
    startTime: string;
    limit?: number;
    isAPI?: boolean;
    isStar?: boolean;
    prevMapId?: string;
    externalId?: string;
    tag?: string;
    encodeId?: string;
    keyword?: string;
    url?: string;
    authorId?: string;
    fbPixel?: string;
    gTag?: string;
}
export interface EditParams {
    encodeId?: string;
    url?: string;
    domain?: string;
    title?: string;
    description?: string;
    imageUrl?: string;
    tags?: string[];
    fbPixel?: string;
    gTag?: string;
    utm?: Record<string, string>;
    expireTime?: string;
}
/** Shorten URL — unauthenticated mode */
export declare function shortenUnauth(params: ShortenParams): Promise<any>;
/** Shorten URL — authenticated mode */
export declare function shortenAuth(token: string, params: ShortenParams): Promise<any>;
/** Get analytics for a link */
export declare function getAnalytics(token: string, encodeId: string): Promise<any>;
/** List links */
export declare function listLinks(token: string, params: ListParams): Promise<any>;
/** Edit a link */
export declare function editLink(token: string, originalEncodeId: string, params: EditParams): Promise<any>;
/** Delete or recover a link */
export declare function deleteLink(token: string, encodeId: string, action?: "delete" | "recover"): Promise<any>;
/** Verify token by calling API status endpoint */
export declare function verifyToken(token: string): Promise<any>;
