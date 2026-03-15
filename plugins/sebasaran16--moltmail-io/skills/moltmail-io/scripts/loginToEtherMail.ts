import { loadWallet } from "../lib/wallet.ts";
import { changePrivateWall, getWalletNonce, loginWalletInbox, saveLoginToken } from "../lib/ethermail.ts"

const WEB3_LOGIN_MESSAGE = "By signing this message you agree to the Terms and Conditions and Privacy Policy";

const main = async () => {
    const wallet = await loadWallet();

    const nonce = await getWalletNonce(wallet.address);

    const signMessage = `${WEB3_LOGIN_MESSAGE}\n\nNONCE: ${nonce}`;

    const signature = await wallet.signMessage(signMessage);

    const token = await loginWalletInbox(wallet.address, signature, false);

    await saveLoginToken(token);

    if (nonce <= 1) {
        await changePrivateWall('FILTER_ANY_EMAIL_WEB3');
    }

    return token;
}

main().then(token => {
    console.log("\n✨ EtherMail login successful");
    return { token };
}).catch(err => {
    console.error("\n❌ Error logging in to EtherMail");
    console.error(err instanceof Error ? err.message : err);
    process.exit(1);
})