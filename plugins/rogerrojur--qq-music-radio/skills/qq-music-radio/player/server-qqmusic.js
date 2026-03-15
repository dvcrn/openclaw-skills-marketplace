const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// 日志中间件
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
    next();
});

// QQ 音乐接口工具函数
async function qqMusicSearch(keyword) {
    try {
        const response = await axios.get('https://c.y.qq.com/soso/fcgi-bin/client_search_cp', {
            params: {
                ct: 24,
                qqmusic_ver: 1298,
                new_json: 1,
                remoteplace: 'txt.yqq.song',
                searchid: Date.now(),
                t: 0,
                aggr: 1,
                cr: 1,
                catZhida: 1,
                lossless: 0,
                flag_qc: 0,
                p: 1,
                n: 20,
                w: keyword,
                g_tk: 5381,
                loginUin: 0,
                hostUin: 0,
                format: 'json',
                inCharset: 'utf8',
                outCharset: 'utf-8',
                notice: 0,
                platform: 'yqq.json',
                needNewCode: 0
            },
            headers: {
                'Referer': 'https://y.qq.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        return response.data;
    } catch (error) {
        console.error('QQ Music search error:', error.message);
        throw error;
    }
}

async function getSongUrl(songmid) {
    try {
        const response = await axios.get('https://u.y.qq.com/cgi-bin/musicu.fcg', {
            params: {
                format: 'json',
                data: JSON.stringify({
                    req_0: {
                        module: 'vkey.GetVkeyServer',
                        method: 'CgiGetVkey',
                        param: {
                            guid: '10000',
                            songmid: [songmid],
                            songtype: [0],
                            uin: '0',
                            loginflag: 1,
                            platform: '20'
                        }
                    }
                })
            },
            headers: {
                'Referer': 'https://y.qq.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        
        const data = response.data;
        if (data.req_0 && data.req_0.data && data.req_0.data.midurlinfo) {
            const purl = data.req_0.data.midurlinfo[0].purl;
            if (purl) {
                return `https://dl.stream.qqmusic.qq.com/${purl}`;
            }
        }
        return '';
    } catch (error) {
        console.error('Get song URL error:', error.message);
        return '';
    }
}

async function getRecommendPlaylists() {
    try {
        const response = await axios.get('https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg', {
            params: {
                picmid: 1,
                rnd: Math.random(),
                g_tk: 5381,
                loginUin: 0,
                hostUin: 0,
                format: 'json',
                inCharset: 'utf8',
                outCharset: 'utf-8',
                notice: 0,
                platform: 'yqq.json',
                needNewCode: 0,
                categoryId: 10000000,
                sortId: 5,
                sin: 0,
                ein: 19
            },
            headers: {
                'Referer': 'https://y.qq.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        return response.data;
    } catch (error) {
        console.error('Get playlists error:', error.message);
        throw error;
    }
}

async function getPlaylistDetail(dissid) {
    try {
        // 使用新的歌单详情接口
        const response = await axios.get('https://c.y.qq.com/v8/fcg-bin/fcg_v8_playlist_cp.fcg', {
            params: {
                id: dissid,
                format: 'json',
                newsong: 1,
                platform: 'jqspaframe.json'
            },
            headers: {
                'Referer': 'https://y.qq.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        return response.data;
    } catch (error) {
        console.error('Get playlist detail error:', error.message);
        throw error;
    }
}

// ============ API 路由 ============

// 1. 获取推荐歌单（作为电台）
app.get('/api/radio/list', async (req, res) => {
    try {
        const data = await getRecommendPlaylists();
        
        if (data.code === 0 && data.data && data.data.list) {
            const radioInfos = data.data.list.slice(0, 12).map(item => ({
                radioId: item.dissid,
                radioName: item.dissname,
                radioPic: item.imgurl,
                listenNum: `${Math.floor(item.listennum / 10000)}万`
            }));
            
            res.json({
                code: 0,
                message: 'success',
                payload: { radioInfos }
            });
        } else {
            throw new Error('Invalid response from QQ Music');
        }
    } catch (error) {
        console.error('Failed to fetch playlists:', error.message);
        res.status(500).json({
            error: 'Failed to fetch radio list',
            message: error.message
        });
    }
});

// 2. 获取歌单详情（电台歌曲）- 优化版：只返回可播放的歌曲
app.post('/api/radio/detail', async (req, res) => {
    try {
        const { radioId } = req.body;
        const data = await getPlaylistDetail(radioId);
        
        if (data.code === 0 && data.data && data.data.cdlist && data.data.cdlist[0]) {
            const songs = data.data.cdlist[0].songlist;
            
            console.log(`[${radioId}] 原始歌曲数量: ${songs.length}`);
            
            // 批量获取播放链接，过滤掉无法播放的歌曲
            const songInfos = [];
            let checkedCount = 0;
            
            for (const song of songs) {
                // 最多检查50首，避免请求过多
                if (checkedCount >= 50) break;
                checkedCount++;
                
                try {
                    const playUrl = await getSongUrl(song.mid);
                    
                    // 只保留有播放链接的歌曲
                    if (playUrl) {
                        songInfos.push({
                            songId: song.id,
                            songMId: song.mid,
                            songName: song.name,
                            singerName: song.singer.map(s => s.name).join('/'),
                            albumName: song.album.name,
                            albumPic: `https://y.gtimg.cn/music/photo_new/T002R300x300M000${song.album.mid}.jpg`,
                            songPlayTime: song.interval,
                            playUrl: playUrl  // 直接返回播放链接
                        });
                        
                        // 获取到30首可播放的就够了
                        if (songInfos.length >= 30) break;
                    }
                } catch (err) {
                    console.log(`[${song.name}] 检测失败，跳过`);
                }
                
                // 每检查10首歌休息一下，避免请求过快
                if (checkedCount % 10 === 0) {
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
            }
            
            console.log(`[${radioId}] 可播放歌曲数量: ${songInfos.length}/${checkedCount}`);
            
            res.json({
                code: 0,
                message: 'success',
                payload: {
                    radioId: radioId,
                    songInfos: songInfos
                }
            });
        } else {
            throw new Error('Invalid response from QQ Music');
        }
    } catch (error) {
        console.error('Failed to fetch radio detail:', error.message);
        res.status(500).json({
            error: 'Failed to fetch radio detail',
            message: error.message
        });
    }
});

// 3. 获取歌曲播放链接
app.post('/api/song/url', async (req, res) => {
    try {
        const { songMId } = req.body;
        const url = await getSongUrl(songMId);
        
        res.json({
            code: url ? 0 : 1,
            message: url ? 'success' : 'No play URL available',
            url: url
        });
    } catch (error) {
        console.error('Failed to get song URL:', error.message);
        res.status(500).json({
            code: 1,
            error: 'Failed to get song URL',
            message: error.message,
            url: ''
        });
    }
});

// 4. 搜索歌曲
app.post('/api/search', async (req, res) => {
    try {
        const { keyword } = req.body;
        const data = await qqMusicSearch(keyword);
        
        if (data.code === 0 && data.data && data.data.song) {
            const songs = data.data.song.list.slice(0, 20);
            const songInfos = songs.map(song => ({
                songId: song.songid,
                songMId: song.songmid,
                songName: song.songname,
                singerName: song.singer.map(s => s.name).join('/'),
                albumName: song.albumname
            }));
            
            res.json({
                code: 0,
                message: 'success',
                payload: { songs: songInfos }
            });
        } else {
            throw new Error('Invalid response from QQ Music');
        }
    } catch (error) {
        console.error('Failed to search:', error.message);
        res.status(500).json({
            error: 'Failed to search songs',
            message: error.message
        });
    }
});

// 健康检查
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        config: {
            mode: 'qq-music-unofficial-api'
        },
        mode: 'production'
    });
});

// 主页
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// 404 处理
app.use((req, res) => {
    res.status(404).json({
        error: 'Not Found',
        path: req.path
    });
});

// 错误处理
app.use((err, req, res, next) => {
    console.error('Server Error:', err);
    res.status(500).json({
        error: 'Internal Server Error',
        message: err.message
    });
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════╗
║     QQ 音乐电台播放器服务器已启动                   ║
╠═══════════════════════════════════════════════════╣
║  访问地址: http://localhost:${PORT}                    
║  健康检查: http://localhost:${PORT}/health             
║  模式: 真实 QQ 音乐（非官方 API）
╚═══════════════════════════════════════════════════╝
    `);
    
    console.log(`
✅ 使用 QQ 音乐非官方 API
✅ 真实歌曲，来自 QQ 音乐
✅ 无需配置 Token
⚠️  注意：部分歌曲可能因版权限制无法播放
    `);
});
