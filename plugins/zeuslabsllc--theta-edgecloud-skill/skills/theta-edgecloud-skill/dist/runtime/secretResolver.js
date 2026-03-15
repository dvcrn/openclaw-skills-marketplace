async function resolveSecret(ctx, key, baseValue) {
    const env = ctx.env ?? {};
    if (ctx.getSecret) {
        try {
            const secret = await ctx.getSecret(key);
            if (secret && secret.trim())
                return secret.trim();
        }
        catch {
            // Intentionally swallow provider errors; continue chain.
        }
    }
    const envValue = env[key];
    if (envValue && envValue.trim())
        return envValue.trim();
    if (baseValue && String(baseValue).trim())
        return String(baseValue).trim();
    return undefined;
}
export async function resolveThetaOnDemandToken(ctx, baseToken) {
    const token = await resolveSecret(ctx, 'THETA_ONDEMAND_API_TOKEN', baseToken);
    if (token)
        return token;
    return resolveSecret(ctx, 'THETA_ONDEMAND_API_KEY', baseToken);
}
export async function resolveThetaInferenceAuth(ctx, baseAuth) {
    const token = await resolveSecret(ctx, 'THETA_INFERENCE_AUTH_TOKEN', baseAuth?.token);
    if (token)
        return { token };
    const user = await resolveSecret(ctx, 'THETA_INFERENCE_AUTH_USER', baseAuth?.user);
    const pass = await resolveSecret(ctx, 'THETA_INFERENCE_AUTH_PASS', baseAuth?.pass);
    if (user && pass)
        return { user, pass };
    return undefined;
}
