// QQ 音乐电台播放器 - 自动推荐版

class AutoRadioPlayer {
    constructor() {
        this.apiBase = window.location.origin;
        this.playlist = [];
        this.currentIndex = 0;
        this.audioPlayer = new Audio();
        this.isLoading = false;
        this.isStarted = false;  // 添加启动标记
        
        // 绑定 DOM 元素
        this.playerContent = document.getElementById('player-content');
        this.messageContainer = document.getElementById('message-container');
        
        // 绑定音频事件
        this.audioPlayer.addEventListener('ended', () => this.playNext());
        this.audioPlayer.addEventListener('error', (e) => {
            console.error('播放错误:', e);
            this.playNext();
        });
        
        // 绑定开始按钮
        const startBtn = document.getElementById('start-btn');
        if (startBtn) {
            startBtn.addEventListener('click', () => {
                console.log('👆 用户点击了开始按钮');
                this.start();
            });
        }
    }
    
    async start() {
        if (this.isStarted) {
            console.log('⚠️ 已经启动过了');
            return;
        }
        
        this.isStarted = true;
        console.log('🚀 开始启动播放器...');
        
        // 显示加载状态
        this.playerContent.innerHTML = '<div class="loading">正在加载推荐歌曲...</div>';
        
        // 初始化
        await this.init();
    }
    
    async init() {
        try {
            console.log('🎵 开始初始化...');
            this.showMessage('正在为你推荐好听的歌曲... 🎵', 'info');
            
            // 随机选择一个热门歌单
            console.log('📋 正在获取歌单列表...');
            const radios = await this.getRadioList();
            console.log(`✅ 获取到 ${radios.length} 个歌单`);
            
            const randomRadio = radios[Math.floor(Math.random() * radios.length)];
            console.log(`🎲 随机选择: ${randomRadio.radioName}`);
            
            this.showMessage(`正在加载「${randomRadio.radioName}」...`, 'info');
            
            // 加载歌单歌曲（后端已过滤，只返回可播放的）
            console.log('🔍 正在获取可播放歌曲...');
            await this.loadPlaylist(randomRadio.radioId);
            console.log(`✅ 获取到 ${this.playlist.length} 首可播放歌曲`);
            
            if (this.playlist.length === 0) {
                console.warn('⚠️ 没有可播放的歌曲，重新加载...');
                throw new Error('没有可播放的歌曲，正在重新加载...');
            }
            
            this.showMessage(`成功加载 ${this.playlist.length} 首可播放歌曲！`, 'info');
            
            // 打乱歌曲顺序（模拟个性化推荐）
            console.log('🎲 打乱播放顺序...');
            this.shufflePlaylist();
            
            // 开始播放第一首
            console.log('▶️ 准备播放第一首歌曲...');
            setTimeout(() => {
                this.clearMessage();
                console.log('🎵 开始播放!');
                this.playSong(0);
            }, 1000);
            
        } catch (error) {
            console.error('❌ 初始化失败:', error);
            this.showMessage('加载失败，正在重试...', 'error');
            
            // 3秒后重试
            setTimeout(() => {
                console.log('🔄 重新初始化...');
                this.init();
            }, 3000);
        }
    }
    
    async getRadioList() {
        const response = await fetch(`${this.apiBase}/api/radio/list`);
        const data = await response.json();
        
        if (data.code === 0 && data.payload && data.payload.radioInfos) {
            return data.payload.radioInfos;
        }
        throw new Error('获取歌单列表失败');
    }
    
    async loadPlaylist(radioId) {
        const response = await fetch(`${this.apiBase}/api/radio/detail`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ radioId })
        });
        
        const data = await response.json();
        
        if (data.code === 0 && data.payload && data.payload.songInfos) {
            this.playlist = data.payload.songInfos;
            if (this.playlist.length === 0) {
                throw new Error('歌单为空');
            }
        } else {
            throw new Error('获取歌曲列表失败');
        }
    }
    
    shufflePlaylist() {
        // Fisher-Yates 洗牌算法
        for (let i = this.playlist.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.playlist[i], this.playlist[j]] = [this.playlist[j], this.playlist[i]];
        }
    }
    
    async playSong(index) {
        if (index < 0 || index >= this.playlist.length || this.isLoading) {
            console.log(`⚠️ 播放条件不满足: index=${index}, total=${this.playlist.length}, loading=${this.isLoading}`);
            return;
        }
        
        console.log(`\n🎵 ============ 播放歌曲 #${index} ============`);
        
        this.isLoading = true;
        this.currentIndex = index;
        const song = this.playlist[index];
        
        console.log(`📀 歌曲信息:`, {
            name: song.songName,
            artist: song.singerName,
            hasPlayUrl: !!song.playUrl
        });
        
        // 停止旧的音频
        if (this.audioPlayer.src) {
            console.log('⏹ 停止旧音频');
            this.audioPlayer.pause();
            this.audioPlayer.src = '';
        }
        
        // 显示加载状态
        this.showLoadingUI(song);
        
        try {
            // 如果歌曲已经有播放链接，直接使用
            if (song.playUrl) {
                console.log('✅ 使用后端返回的播放链接');
                console.log('🔗 播放链接:', song.playUrl.substring(0, 80) + '...');
                
                this.audioPlayer.src = song.playUrl;
                
                console.log('▶️ 开始播放...');
                await this.audioPlayer.play();
                
                console.log('✅ 播放成功！显示播放器UI');
                this.showPlayerUI(song);
            } else {
                console.log('⚠️ 歌曲没有播放链接，尝试获取...');
                
                // 否则尝试获取播放链接
                const response = await fetch(`${this.apiBase}/api/song/url`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ songMId: song.songMId })
                });
                
                const data = await response.json();
                
                if (data.code === 0 && data.url) {
                    console.log('✅ 获取播放链接成功');
                    this.audioPlayer.src = data.url;
                    await this.audioPlayer.play();
                    this.showPlayerUI(song);
                } else {
                    console.log('❌ 无法获取播放链接');
                    // 没有播放链接，显示降级 UI
                    this.showFallbackUI(song);
                }
            }
        } catch (error) {
            console.error('❌ 播放失败:', error);
            // 播放失败，自动跳到下一首
            console.log('⏭ 2秒后自动播放下一首');
            setTimeout(() => this.playNext(), 2000);
        } finally {
            this.isLoading = false;
            console.log(`============ 播放流程结束 ============\n`);
        }
    }
    
    showLoadingUI(song) {
        const fallbackCover = this.generateFallbackCover(song);
        
        this.playerContent.innerHTML = `
            <div class="album-cover">
                <img src="${song.albumPic}" alt="封面" onerror="this.src='${fallbackCover}'">
            </div>
            <div class="song-info">
                <h2>${song.songName}</h2>
                <p>${song.singerName}</p>
            </div>
            <div class="loading">正在加载...</div>
        `;
    }
    
    generateFallbackCover(song) {
        // 根据歌曲名称生成颜色
        const colors = [
            ['#667eea', '#764ba2'],  // 紫色
            ['#f093fb', '#f5576c'],  // 粉红
            ['#4facfe', '#00f2fe'],  // 蓝色
            ['#43e97b', '#38f9d7'],  // 绿色
            ['#fa709a', '#fee140'],  // 橙粉
            ['#30cfd0', '#330867'],  // 青紫
            ['#a8edea', '#fed6e3'],  // 淡彩
            ['#ff9a9e', '#fecfef'],  // 粉嫩
            ['#ffecd2', '#fcb69f'],  // 暖橙
            ['#ff6e7f', '#bfe9ff'],  // 红蓝
        ];
        
        // 使用歌曲名的哈希值选择颜色
        let hash = 0;
        const str = song.songName + song.singerName;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        const colorIndex = Math.abs(hash) % colors.length;
        const [color1, color2] = colors[colorIndex];
        
        // 创建 SVG 作为占位图
        const svg = `
            <svg xmlns="http://www.w3.org/2000/svg" width="300" height="300">
                <defs>
                    <linearGradient id="grad${hash}" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:${color1};stop-opacity:1" />
                        <stop offset="100%" style="stop-color:${color2};stop-opacity:1" />
                    </linearGradient>
                </defs>
                <rect width="300" height="300" fill="url(#grad${hash})" />
                <text x="50%" y="45%" text-anchor="middle" fill="white" font-size="24" font-weight="bold" font-family="Arial, sans-serif" opacity="0.9">
                    ${this.escapeHtml(song.songName.substring(0, 12))}
                </text>
                <text x="50%" y="55%" text-anchor="middle" fill="white" font-size="16" font-family="Arial, sans-serif" opacity="0.7">
                    ${this.escapeHtml(song.singerName.substring(0, 20))}
                </text>
                <text x="50%" y="65%" text-anchor="middle" fill="white" font-size="48" font-family="Arial, sans-serif" opacity="0.3">
                    🎵
                </text>
            </svg>
        `;
        
        return 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)));
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showPlayerUI(song) {
        const fallbackCover = this.generateFallbackCover(song);
        
        this.playerContent.innerHTML = `
            <div class="album-cover">
                <img src="${song.albumPic}" alt="封面" onerror="this.src='${fallbackCover}'">
            </div>
            
            <div class="song-info">
                <h2>${song.songName}</h2>
                <p>${song.singerName} - ${song.albumName}</p>
            </div>
            
            <div class="player-controls">
                <button class="control-btn" id="prev-btn">⏮</button>
                <button class="control-btn large" id="play-pause-btn">⏸</button>
                <button class="control-btn" id="next-btn">⏭</button>
            </div>
            
            <div class="progress-container">
                <div class="progress-bar" id="progress-bar">
                    <div class="progress" id="progress"></div>
                </div>
                <div class="time-display">
                    <span id="current-time">0:00</span>
                    <span id="total-time">0:00</span>
                </div>
            </div>
            
            <div class="volume-control">
                <span>🔊</span>
                <div class="volume-slider" id="volume-slider">
                    <div class="volume-level" id="volume-level"></div>
                </div>
            </div>
            
            <audio id="audio-display" controls></audio>
            
            <div class="playlist-section">
                <h3>
                    <span>📋</span>
                    <span>播放列表</span>
                </h3>
                <div style="text-align: center; color: #666; margin-bottom: 10px;">
                    共 ${this.playlist.length} 首 · 当前第 ${this.currentIndex + 1} 首 · 剩余 ${this.playlist.length - this.currentIndex - 1} 首
                </div>
                <div id="upcoming-list"></div>
            </div>
        `;
        
        // 设置 audio 显示元素
        const audioDisplay = document.getElementById('audio-display');
        audioDisplay.src = this.audioPlayer.src;
        audioDisplay.currentTime = this.audioPlayer.currentTime;
        
        // 同步播放状态
        if (!this.audioPlayer.paused) {
            audioDisplay.play().catch(err => console.log('Display sync:', err));
        }
        
        // 双向同步
        audioDisplay.addEventListener('play', () => {
            if (this.audioPlayer.paused) this.audioPlayer.play();
        });
        audioDisplay.addEventListener('pause', () => {
            if (!this.audioPlayer.paused) this.audioPlayer.pause();
        });
        audioDisplay.addEventListener('seeked', () => {
            this.audioPlayer.currentTime = audioDisplay.currentTime;
        });
        
        // 绑定控制按钮
        document.getElementById('prev-btn').addEventListener('click', () => this.playPrevious());
        document.getElementById('play-pause-btn').addEventListener('click', () => this.togglePlay());
        document.getElementById('next-btn').addEventListener('click', () => this.playNext());
        
        // 更新播放列表
        this.updateUpcomingList();
        
        // 更新进度条
        this.audioPlayer.addEventListener('timeupdate', () => this.updateProgress());
        
        // 播放/暂停事件
        this.audioPlayer.addEventListener('play', () => {
            const btn = document.getElementById('play-pause-btn');
            if (btn) btn.textContent = '⏸';
        });
        this.audioPlayer.addEventListener('pause', () => {
            const btn = document.getElementById('play-pause-btn');
            if (btn) btn.textContent = '▶';
        });
    }
    
    showFallbackUI(song) {
        const qqMusicUrl = `https://y.qq.com/n/ryqq/songDetail/${song.songMId}`;
        const fallbackCover = this.generateFallbackCover(song);
        
        this.playerContent.innerHTML = `
            <div class="album-cover">
                <img src="${song.albumPic}" alt="封面" onerror="this.src='${fallbackCover}'">
            </div>
            
            <div class="song-info">
                <h2>${song.songName}</h2>
                <p>${song.singerName} - ${song.albumName}</p>
            </div>
            
            <div class="fallback-container">
                <div class="icon">⚠️</div>
                <h3>无法直接播放</h3>
                <p>由于版权限制，该歌曲无法在浏览器中播放</p>
                <div>
                    <a href="${qqMusicUrl}" target="_blank" class="fallback-btn">
                        🎵 在 QQ 音乐打开
                    </a>
                    <button class="fallback-btn" onclick="window.autoPlayer.playNext()">
                        ⏭ 下一首
                    </button>
                </div>
            </div>
        `;
        
        // 暴露到全局
        window.autoPlayer = this;
        
        // 5秒后自动播放下一首
        setTimeout(() => this.playNext(), 5000);
    }
    
    updateUpcomingList() {
        const upcomingList = document.getElementById('upcoming-list');
        if (!upcomingList) return;
        
        upcomingList.innerHTML = '';
        
        // 显示接下来的5首歌
        const upcomingSongs = this.playlist.slice(this.currentIndex + 1, this.currentIndex + 6);
        
        if (upcomingSongs.length === 0) {
            upcomingList.innerHTML = '<div style="text-align: center; color: #999; padding: 20px;">播放完毕，即将加载新推荐...</div>';
            return;
        }
        
        upcomingSongs.forEach((song, index) => {
            const item = document.createElement('div');
            item.className = 'playlist-item';
            item.innerHTML = `
                <div class="playlist-item-info">
                    <strong>下一首 ${index === 0 ? '🎵' : `+${index}`} ${song.songName}</strong>
                    <div class="artist">${song.singerName}</div>
                </div>
            `;
            upcomingList.appendChild(item);
        });
    }
    
    updateProgress() {
        const progress = document.getElementById('progress');
        const currentTime = document.getElementById('current-time');
        const totalTime = document.getElementById('total-time');
        
        if (!progress || !currentTime || !totalTime) return;
        
        const percent = (this.audioPlayer.currentTime / this.audioPlayer.duration) * 100 || 0;
        progress.style.width = percent + '%';
        
        currentTime.textContent = this.formatTime(this.audioPlayer.currentTime);
        totalTime.textContent = this.formatTime(this.audioPlayer.duration);
    }
    
    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    togglePlay() {
        if (this.audioPlayer.paused) {
            this.audioPlayer.play();
        } else {
            this.audioPlayer.pause();
        }
    }
    
    playNext() {
        if (this.isLoading) return;
        
        // 如果到了播放列表末尾，重新加载新的推荐
        if (this.currentIndex >= this.playlist.length - 1) {
            this.showMessage('正在加载更多推荐...', 'info');
            this.init();
        } else {
            this.playSong(this.currentIndex + 1);
        }
    }
    
    playPrevious() {
        if (this.isLoading) return;
        
        if (this.currentIndex > 0) {
            this.playSong(this.currentIndex - 1);
        }
    }
    
    showMessage(message, type = 'info') {
        const messageEl = document.createElement('div');
        messageEl.className = type;
        messageEl.textContent = message;
        this.messageContainer.innerHTML = '';
        this.messageContainer.appendChild(messageEl);
    }
    
    clearMessage() {
        this.messageContainer.innerHTML = '';
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    console.log('📱 页面加载完成，等待用户点击开始按钮');
    new AutoRadioPlayer();
});
