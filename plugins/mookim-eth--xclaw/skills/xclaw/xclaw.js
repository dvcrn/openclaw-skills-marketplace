
const http = require('https');

const API_KEY = process.env.XCLAW_API_KEY || process.env.CRYPTOHUNT_API_KEY;

function requestXClaw(path, method, body) {
    if (!API_KEY) {
        console.error("Error: XCLAW_API_KEY or CRYPTOHUNT_API_KEY environment variable is missing.");
        process.exit(1);
    }
    const BASE_URL = 'pro.xclaw.info';
    const DEBUG = false;
    return new Promise((resolve, reject) => {
        const options = {
            hostname: BASE_URL,
            path: path,
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': API_KEY
            }
        };
        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try {
                        const parsed = JSON.parse(data);
                        if (DEBUG) {
                            console.error("[Debug] API Response:", JSON.stringify(parsed, null, 2));
                        }
                        if (parsed && (parsed.status === false || (parsed.code && parsed.code !== 200))) {
                            reject(new Error(parsed.msg || parsed.errMsg || "API Error"));
                        } else {
                            resolve(parsed);
                        }
                    } catch (e) {
                        resolve(data);
                    }
                } else {
                    reject(new Error(`HTTP ${res.statusCode}: ${data}`));
                }
            });
        });
        req.on('error', (e) => reject(e));
        if (body) req.write(JSON.stringify(body));
        req.end();
    });
}

/**
 * 核心数据脱脂函数 (Data Slimming)
 * @param {Object} rawData 原始 API 返回数据
 * @param {Object} options { limit: 15, mode: 'slim' | 'full' }
 */
function slimTweets(rawData, options = { limit: 15, mode: 'slim' }) {
    if (!rawData) return [];
    const items = Array.isArray(rawData) ? rawData : (rawData.tweets || rawData.items || []);
    const mode = options.mode || 'slim';

    return items.slice(0, options.limit).map(item => {
        const t = item.tweet || item;
        const info = item.info || t.info || {};
        const ai = t.ai || {};

        // 基础脱脂数据 (Slim Mode)
        const base = {
            author: t.profile ? t.profile.name : (t.username || 'KOL'),
            title: ai.title_cn || '无标题',
            abstract: ai.abstract_cn || (info.html ? info.html.replace(/<[^>]*>?/gm, '').substring(0, 100) : (t.text ? t.text.substring(0, 100) : 'No summary')),
            engagement: t.statistic ? `❤️${t.statistic.likes} 🔁${t.statistic.retweet_count} 👁️${t.statistic.views || 0}` : 'N/A',
            time: t.create_time || t.created_at,
            link: t.link || `https://x.com/i/status/${t.id}`
        };

        // 如果是全文模式，注入重负载数据
        if (mode === 'full') {
            return {
                ...base,
                raw_text: t.text || '',
                html_content: info.html || '',
                kol_engagement: item.kol_engagement || t.kol_engagement || null
            };
        }

        return base;
    });
}

function requireArg(value, message) {
    if (!value || !String(value).trim()) throw new Error(message);
    return String(value).trim();
}

function pickFirst(...values) {
    for (const v of values) {
        if (v !== undefined && v !== null && String(v).trim() !== '') return v;
    }
    return null;
}

function normalizeSocialAction(action, options = {}) {
    const a = action || {};
    const target = a.target || a.user || a.profile || {};
    const preferredIdField = options.preferredIdField || null;

    const targetId = pickFirst(
        preferredIdField ? a[preferredIdField] : null,
        a.target_user_id, a.followed_user_id, a.unfollowed_user_id, a.to_user_id,
        a.following_id, a.follower_id,
        target.id, target.user_id, a.user_id, a.uid, a.id
    );

    const targetHandle = pickFirst(
        a.target_handle, a.handle, a.username, a.screen_name,
        target.handle, target.username, target.screen_name
    );

    const targetName = pickFirst(
        a.target_name, a.name, a.nickname,
        target.name, target.nickname
    );

    return {
        ...a,
        target_id: targetId,
        target_handle: targetHandle,
        target_name: targetName
    };
}

async function fetchProfileById(userId) {
    const id = String(userId || '').trim();
    if (!id) return null;

    const attempts = [
        ['/user/profile', { user_id: id }],
        ['/user/profile', { id }],
        ['/user/profile_by_id', { user_id: id }],
        ['/user/profile_by_id', { id }],
        ['/user/profile_detail', { user_id: id }]
    ];

    for (const [path, payload] of attempts) {
        try {
            const res = await requestXClaw(path, 'POST', payload);
            const root = (res && (res.data || res.profile || res.user)) || res;
            if (!root || typeof root !== 'object') continue;

            const handle = pickFirst(root.handle, root.username, root.screen_name, root.userName);
            const name = pickFirst(root.name, root.nickname, root.display_name, root.full_name);
            const resolvedId = pickFirst(root.id, root.user_id, id);

            if (handle || name) {
                return { id: resolvedId, handle, name };
            }
        } catch (_) {
            // try next candidate endpoint
        }
    }

    return null;
}

async function enrichSocialActions(actions, usersMap = {}, options = {}) {
    const list = Array.isArray(actions) ? actions : [];
    const normalized = list.map(item => normalizeSocialAction(item, options));
    const cache = new Map();

    // 1) 优先使用同一 API 返回中的 twitter_users（最准确也最快）
    Object.entries(usersMap || {}).forEach(([id, user]) => {
        const root = user || {};
        const profile = root.profile || {};
        const handle = pickFirst(root.username, profile.username, root.username_raw, profile.username_raw);
        const name = pickFirst(root.name, profile.name, profile.nickname);
        if (handle || name) {
            cache.set(String(id), { id: String(id), handle, name });
        }
    });

    // 2) 对仍缺失的信息再按 ID 兜底查询
    const idsToResolve = [...new Set(normalized.map(x => x.target_id).filter(Boolean))]
        .filter(id => !cache.has(String(id)));

    await Promise.all(idsToResolve.map(async (id) => {
        const profile = await fetchProfileById(id);
        if (profile) cache.set(String(id), profile);
    }));

    return normalized.map(item => {
        const profile = item.target_id ? cache.get(String(item.target_id)) : null;
        return {
            ...item,
            target_handle: item.target_handle || (profile ? profile.handle : null),
            target_name: item.target_name || (profile ? profile.name : null)
        };
    });
}

async function main() {
    let args = process.argv.slice(2);
    const command = (args[0] || '').toLowerCase();
    const normalizedCommand = (command === 'analyze' || command === 'crawl') ? 'tweets' : command;

    // --- 修复参数解析 Bug：全局提取标记位 ---
    const isFullMode = args.includes('--full');
    const isVerboseRequested = args.includes('--verbose');
    const mode = isFullMode ? 'full' : 'slim';

    // 过滤掉标记位，保留纯净的位置参数
    args = args.filter(arg => arg !== '--full' && arg !== '--verbose');

    try {
        switch (normalizedCommand) {
            case 'hot': {
                const hours = parseInt(args[1]) || 24;
                const group = args[2] || 'cn';
                const tag = args[3] || null; // 此时 args[3] 已经是真正的 tag，不再是 --full
                const payload = { hours, group };
                if (tag) payload.tag = tag;
                const rawData = await requestXClaw('/tweet/hot_tweets', 'POST', payload);
                const trending = slimTweets(rawData, { limit: 10, mode });
                console.log(JSON.stringify({
                    info: `Top hot tweets (${hours}h, ${group}${tag ? ', ' + tag : ''}) [Mode: ${mode}]`,
                    trending
                }, null, 2));
                break;
            }

            case 'tweets': {
                const username = requireArg(args[1], "Username/Handle is required.").replace('@', '').trim();
                const count = parseInt(args[2]) || 20;
                let result;
                
                // 极致精简：直接利用后端已优化的 verbose 逻辑
                // 默认 verbose: false (后端现在返回 原创+引用+转发，不含回复)
                const payload = { 
                    handle: username, 
                    maxResults: count, 
                    verbose: isVerboseRequested // 只有显式要求才传 true 以包含回复
                };

                try {
                    result = await requestXClaw('/tweet/kol_tweets', 'POST', payload);
                    // 如果后端返回 "User is not a tracking KOL" 或其他非数组错误信息，手动抛出异常以触发 fallback
                    if (!Array.isArray(result)) {
                        throw new Error("Not a tracking KOL, switch to fallback");
                    }
                } catch (e) {
                    try {
                        const profile = await requestXClaw('/user/profile_by_handle', 'POST', { handle: username });
                        if (!profile || !profile.id) throw new Error("User not found");
                        
                        payload.user_id = profile.id;
                        delete payload.handle;
                        const fallbackResult = await requestXClaw('/tweet/user_tweets', 'POST', payload);
                        // 修复：user_tweets 返回的是对象 { tweets: [...], next: ... }
                        result = (fallbackResult && fallbackResult.tweets) ? fallbackResult.tweets : fallbackResult;
                    } catch (fallbackError) {
                        console.error("Fallback failed:", fallbackError.message);
                        result = [];
                    }
                }

                console.log(JSON.stringify({ 
                    info: `Recent tweets for @${username} [Mode: ${mode}, Count: ${count}, Verbose: ${isVerboseRequested}]`, 
                    tweets: slimTweets(result, { limit: count, mode }) 
                }, null, 2));
                break;
            }

            case 'ghost': {
                const handle = requireArg(args[1], "Handle is required.").replace('@', '').trim();
                const deleted = slimTweets(await requestXClaw('/tweet/deleted_tweets', 'POST', { handle }), 10);
                console.log(JSON.stringify({
                    info: `Deleted (Ghost) tweets for @${handle}`,
                    deleted,
                    deleted_tweets: deleted
                }, null, 2));
                break;
            }

            case 'traces': {
                const handle = requireArg(args[1], "Handle is required.").replace('@', '').trim();
                const result = await requestXClaw('/user/profile_history', 'POST', { handle });
                console.log(JSON.stringify({ info: `Identity Traces (Profile change history) for @${handle}`, history: result.profile_history || result.data || result }, null, 2));
                break;
            }

            case 'social': {
                const handle = requireArg(args[1], "Handle is required.").replace('@', '').trim();
                console.log(`[XClaw] Checking social pulse (follows/unfollows) for @${handle}...`);
                const follows = await requestXClaw('/social/follow_relation', 'POST', { handle });
                const unfollows = await requestXClaw('/social/unfollow_relation', 'POST', { handle });

                const followActions = follows.following_action || follows.followed_action || follows.data || [];
                const unfollowActions = unfollows.unfollowing_action || unfollows.unfollowed_action || unfollows.data || [];

                const followUsers = follows.twitter_users || {};
                const unfollowUsers = unfollows.twitter_users || {};

                const [recentFollowing, recentUnfollowing] = await Promise.all([
                    enrichSocialActions(followActions, followUsers, { preferredIdField: 'following_id' }),
                    enrichSocialActions(unfollowActions, unfollowUsers, { preferredIdField: 'following_id' })
                ]);

                console.log(JSON.stringify({ 
                    info: `Social actions for @${handle}`,
                    recent_following: recentFollowing,
                    recent_unfollowing: recentUnfollowing
                }, null, 2));
                break;
            }

            case 'rank': {
                const handle = requireArg(args[1], "Handle is required.").replace('@', '').trim();
                
                // 并发请求：基础 Rank 数据 + 独立灵魂指数
                const [rankResult, soulResult] = await Promise.all([
                    requestXClaw('/data/xclaw', 'POST', { handle }),
                    requestXClaw('/ai/soul_index', 'POST', { handle })
                ]);
                
                const root = rankResult.data || rankResult;
                const user_info = root.user_info || {};
                const feature = user_info.feature || {};
                const rank = feature.rank || {};
                const mbti = feature.mbti ? feature.mbti.cn : null;
                const multi_field = feature.multi_field ? feature.multi_field.cn : null;
                
                // 从 /ai/soul_index 提取分数
                const soul_score = soulResult.data ? soulResult.data.score : (soulResult.score || 'N/A');

                console.log(JSON.stringify({
                    info: `Deep analysis for @${handle}`,
                    identity: {
                        name: user_info.name || root.name,
                        soul_score: soul_score, // 注入最新的灵魂指数分数
                        classification: user_info.ai ? user_info.ai.classification : 'unknown',
                        mbti: mbti ? mbti.mbti : 'unknown',
                        mbti_explanation: mbti ? mbti.explanation : ''
                    },
                    rankings: {
                        kol_cn_rank: rank.kolCnRank,
                        kol_global_rank: rank.kolGlobalRank,
                        total_rank: rank.kolRank
                    },
                    expertise: multi_field ? multi_field.fields : [],
                    expertise_summary: multi_field ? multi_field.summary : '',
                    social_stats: {
                        followers: user_info.profile ? user_info.profile.followers_count : 0,
                        tweets: user_info.profile ? user_info.profile.tweets_count : 0,
                        kol_followers_cn: feature.kol_followers ? feature.kol_followers.cnKolFollowersCount : 0,
                        kol_followers_global: feature.kol_followers ? feature.kol_followers.globalKolFollowersCount : 0
                    },
                    tags: user_info.tags || root.tags || []
                }, null, 2));
                break;
            }

            case 'detail': {
                const tweetArg = requireArg(args[1], "Tweet URL or ID is required.");
                const tweetId = tweetArg.includes('/') ? tweetArg.split('/').pop().split('?')[0] : tweetArg;
                const res = await requestXClaw('/tweet/tweet_detail', 'POST', { tweet_id: tweetId });
                console.log(JSON.stringify(res, null, 2));
                break;
            }

            case 'draft': {
                const hours = parseInt(args[1]) || 24;
                const group = args[2] || 'cn';
                const tag = args[3] || null;
                const payload = { hours, group };
                if (tag) payload.tag = tag;
                const rawData = await requestXClaw('/tweet/hot_tweets', 'POST', payload);
                const top5 = slimTweets(rawData, 5);
                console.log(JSON.stringify({
                    instruction: 'Based on these Top 5 viral topics, create 3 diverse tweet drafts.',
                    topics: top5
                }, null, 2));
                break;
            }

            default:
                console.log("Usage: node xclaw.js <hot|tweets|analyze|crawl|ghost|traces|social|rank|detail|draft> <params>");
        }
    } catch (error) {
        console.log(JSON.stringify({ error: error.message }, null, 2));
    }
}

main();
