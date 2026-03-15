/**
 * Twitter DM API client
 * Uses same auth as bird CLI
 */
import type { TwitterCookies } from '@steipete/bird';
export declare function fetchDMInbox(cookies: TwitterCookies, count?: number): Promise<any>;
export declare function fetchDMConversation(cookies: TwitterCookies, conversationId: string, maxId?: string): Promise<any>;
export interface DMConversation {
    id: string;
    type: string;
    name?: string;
    participants: string[];
    lastMessage?: string;
    lastSender?: string;
    timestamp: string;
}
export interface DMMessage {
    id: string;
    text: string;
    sender: string;
    timestamp: string;
}
export declare function parseInbox(data: any): DMConversation[];
export declare function parseConversation(data: any): DMMessage[];
