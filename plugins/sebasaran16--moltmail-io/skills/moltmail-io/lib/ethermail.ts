import { ethers } from "ethers";
import axios from "axios";
import fs from "fs/promises";
import path from "path";

const ENDPOINT_URL = "https://srv.ethermail.io";
const DOMAIN = "moltmail.io";

const STATE_DIR = path.resolve(process.cwd(), "state");
const AUTH_PATH = path.join(STATE_DIR, "auth.json");

type AuthData = {
    token: string;
    issuedAt: string;
    userId?: string;
};

export type PrivacyWallType = 'FILTER_ANY_EMAIL_WEB3' | 'FILTER_ANYONE_MY_COMMUNITIES' | 'FILTER_ONLY_COMPANIES_MY_COMMUNITIES';

export const getWalletNonce = async (walletAddress: string) => {
    if (!walletAddress) {
        throw new Error("Wallet address is required");
    } else if (!ethers.isAddress(walletAddress)) {
        throw new Error(`Wallet ${walletAddress} is not a valid EVM address`);
    }

    const headers = await getRequestHeaders();
    const response = await axios.post(
        `${ENDPOINT_URL}/nonce`,
        {
            walletAddress: walletAddress.toLowerCase()
        },
        {
            headers
        }
    );

    return response.data.nonce;
}

export const loginWalletInbox = async (walletAddress: string, signature: string, isMPC: boolean) => {
    if (!ethers.isAddress(walletAddress)) {
        throw new Error(`Wallet ${walletAddress} is not a valid EVM address`);
    }

    const web3Address = getEmailFromWallet(walletAddress);
    const headers = await getRequestHeaders();

    const response = await axios.post(
        `${ENDPOINT_URL}/authenticate`,
        {
            web3Address,
            signature,
            isMPC,
            platformData: {
              ai_agent: true,
              platform: "openclaw"
            }
        },
        {
            headers,
        }
    );

    return response.data.token;
}

export const completeOnboarding = async (walletAddress: string) => {
    if (!ethers.isAddress(walletAddress)) {
        throw new Error(`Wallet ${walletAddress} is not a valid EVM address`);
    }

    const headers = await getRequestHeaders();
    const response = await axios.post(
        `${ENDPOINT_URL}/users/onboarding`,
        {
            email: getEmailFromWallet(walletAddress),
            isSso: false,
        },
        { headers }
    );

    return response.data;
}

export const saveLoginToken = async (token: string) => {
    const tokenPayload = decodeJwtPayload(token);

    const tokenData = {
        token,
        issuedAt: new Date(tokenPayload['iat'] * 1000),
        expiringAt: new Date(tokenPayload['exp'] * 1000),
        userId: tokenPayload['sub'],
    }

    await fs.writeFile(
        AUTH_PATH,
        JSON.stringify(tokenData, null, 2),
        { mode: 0o600 }
    );
}

export const changePrivateWall = async (privacySetting: PrivacyWallType) => {
    const headers = await getRequestHeaders();
    const response = await axios.put(
        `${ENDPOINT_URL}/paywall/configuration-paywall`,
        {
            paywall: {
                typeWeb: "WEB3",
                configurationPaywall: privacySetting
            }
        },
        { headers }
    );

    return response.data;
}

export const getLoginToken = async (): Promise<string> => {
    try {
        const raw = await fs.readFile(AUTH_PATH, "utf8");
        const data: AuthData = JSON.parse(raw);

        if (typeof data.token === "string" && data.token.length > 0) {
            return data.token;
        }

        return "";
    } catch {
        return "";
    }
};

export const getRequestHeaders = async () => {
    const headers = {
        "Content-Type": "application/json",
            "Accept": "application/json",
    }

    const loginToken = await getLoginToken();
    if (loginToken) {
        headers['X-Access-Token'] = loginToken
    }

    return headers;
}

export const getEmailFromWallet = (walletAddress: string) => {
    if (!ethers.isAddress(walletAddress)) {
        throw new Error(`Wallet ${walletAddress} is not a valid EVM address`);
    }

    return `${walletAddress.toLowerCase()}@${DOMAIN}`;
}

function decodeJwtPayload<T = any>(token: string): T {
    try {
        const base64Url = token.split('.')[1];                    // get payload part
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
            atob(base64)
                .split('')
                .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                .join('')
        );
        return JSON.parse(jsonPayload);
    } catch (err) {
        console.error("Invalid JWT format", err);
        throw err;
    }
}