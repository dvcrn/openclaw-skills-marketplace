import { UnattendedOptions } from '../security/approval.js';
import { ChromeProfile } from './chrome-profiles.js';
interface BrowserOptions {
    site?: string;
    autoVault?: boolean;
    headless?: boolean;
    timeout?: number;
    profile?: ChromeProfile;
    unattended?: UnattendedOptions;
}
export declare function startBrowser(url: string, options?: BrowserOptions): Promise<void>;
export declare function performAction(action: string, options?: {
    autoApprove?: boolean;
    unattended?: UnattendedOptions;
}): Promise<void>;
export declare function extractData(instruction: string, schema?: Record<string, unknown>): Promise<unknown>;
export declare function takeScreenshot(action?: string): Promise<string | null>;
export declare function closeBrowser(): Promise<void>;
export declare function getBrowserStatus(): {
    active: boolean;
    sessionId?: string;
    timeRemaining?: number;
    site?: string;
    actionCount: number;
    suspended?: boolean;
    warningShown?: boolean;
};
export declare function suspendSession(): void;
export declare function resumeSession(): void;
export {};
