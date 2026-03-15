/**
 * Cross-platform secure token storage using AES-256-CBC encryption.
 * Compatible with the existing OpenClaw skill's keychain.mjs.
 */
export declare function setToken(token: string): boolean;
export declare function getToken(): string | null;
export declare function deleteToken(): boolean;
