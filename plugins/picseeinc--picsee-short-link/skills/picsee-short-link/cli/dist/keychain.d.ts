/**
 * Cross-platform secure token storage using AES-256-CBC encryption.
 * Key derivation: SHA-256(random-salt + hostname + username).
 * The random salt is generated once and stored alongside the token,
 * making the key unpredictable even if hostname/username are known.
 */
export declare function setToken(token: string): boolean;
export declare function getToken(): string | null;
export declare function deleteToken(): boolean;
