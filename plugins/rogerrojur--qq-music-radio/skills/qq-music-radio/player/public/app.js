// QQ 音乐电台播放器 - 完整版（带后端代理）

class RadioPlayer {
    constructor() {
        this.apiBase = window.location.origin;
        this.currentRadio = null;
        this.currentSongIndex = 0;
        this.playlist = [];
        this.audioPlayer = document.getElementById('audio-player');
        this.serverMode = 'mock'; // 'mock' 或 'production'
        
        // 绑定 DOM 元素
        this.radioListEl = document.getElementById('radio-list');
        this.currentPlayingEl = document.getElementById('current-playing');
        this.playlistEl = document.getElementById('playlist');
        this.playlistContainer = document.getElementById('playlist-container');
        this.messageContainer = document.getElementById('message-container');
        this.modeBadge = document.getElementById('mode-badge');
        
        // 歌曲信息元素
        this.songNameEl = document.getElementById('song-name');
        this.songArtistEl = document.getElementById('song-artist');
        this.songAlbumEl = document.getElementById('song-album');
        this.songCoverEl = document.getElementById('song-cover');
        
        // 按钮元素
        this.playPauseBtn = document.getElementById('play-pause-btn');
        this.prevBtn = document.getElementById('prev-btn');
        this.nextBtn = document.getElementById('next-btn');
        
        // 进度条
        this.progressEl = document.getElementById('progress');
        
        // 音量控制
        this.volumeSlider = document.getElementById('volume-slider');
        this.volumeValue = document.getElementById('volume-value');
        
        // 绑定事件
        this.bindEvents();
        
        // 检查服务器状态
        this.checkServerStatus();
        
        // 加载电台列表
        this.loadRadioList();
    }
    
    bindEvents() {
        // 播放/暂停
        this.playPauseBtn.addEventListener('click', () => this.togglePlay());
        
        // 上一曲/下一曲
        this.prevBtn.addEventListener('click', () => this.playPrevious());
        this.nextBtn.addEventListener('click', () => this.playNext());
        
        // 音频事件
        this.audioPlayer.addEventListener('timeupdate', () => this.updateProgress());
        this.audioPlayer.addEventListener('ended', () => this.playNext());
        this.audioPlayer.addEventListener('play', () => this.updatePlayButton(true));
        this.audioPlayer.addEventListener('pause', () => this.updatePlayButton(false));
        
        // 音量控制
        this.volumeSlider.addEventListener('input', (e) => {
            const volume = e.target.value;
            this.audioPlayer.volume = volume / 100;
            this.volumeValue.textContent = volume + '%';
        });
    }
    
    async checkServerStatus() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            const data = await response.json();
            
            this.serverMode = data.mode;
            this.updateModeBadge(data.mode, data.config);
        } catch (error) {
            console.error('Failed to check server status:', error);
            this.showMessage('无法连接到服务器', 'error');
        }
    }
    
    updateModeBadge(mode, config) {
        if (mode === 'production') {
            this.modeBadge.textContent = '🟢 真实 API 模式';
            this.modeBadge.className = 'status-badge production';
        } else {
            this.modeBadge.textContent = '🟡 演示模式';
            this.modeBadge.className = 'status-badge mock';
            this.showMessage('当前使用模拟数据。要使用真实 API，请在 .env 文件中配置 Token', 'info');
        }
    }
    
    async loadRadioList() {
        try {
            // 先尝试使用真实 API
            let response = await fetch(`${this.apiBase}/api/radio/list`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ payload: {} })
            });
            
            let data = await response.json();
            
            // 如果返回错误且建议使用模拟数据，则使用模拟数据
            if (data.useMockData) {
                response = await fetch(`${this.apiBase}/api/mock/radio/list`);
                data = await response.json();
            }
            
            if (data.payload && data.payload.radioInfos) {
                this.renderRadioList(data.payload.radioInfos);
            } else {
                throw new Error('Invalid response format');
            }
        } catch (error) {
            console.error('Failed to load radio list:', error);
            this.showMessage('加载电台列表失败: ' + error.message, 'error');
        }
    }
    
    renderRadioList(radios) {
        this.radioListEl.innerHTML = '';
        
        radios.forEach(radio => {
            const card = document.createElement('div');
            card.className = 'radio-card';
            card.innerHTML = `
                <img src="${radio.radioPic}" alt="${radio.radioName}" onerror="this.src='https://y.gtimg.cn/music/photo_new/T002R300x300M000003rmKmG3HZfbK.jpg'">
                <h3>${radio.radioName}</h3>
                <div class="listen-count">🎧 ${radio.listenNum}</div>
            `;
            
            card.addEventListener('click', () => this.selectRadio(radio, card));
            this.radioListEl.appendChild(card);
        });
    }
    
    async selectRadio(radio, cardElement) {
        try {
            // 更新选中状态
            document.querySelectorAll('.radio-card').forEach(c => c.classList.remove('active'));
            cardElement.classList.add('active');
            
            this.currentRadio = radio;
            this.showMessage('正在加载歌曲列表...', 'info');
            
            // 加载电台歌曲
            await this.loadRadioSongs(radio.radioId);
            
            // 清除消息
            this.clearMessage();
        } catch (error) {
            this.showMessage('加载电台歌曲失败: ' + error.message, 'error');
        }
    }
    
    async loadRadioSongs(radioId) {
        try {
            // 先尝试使用真实 API
            let response = await fetch(`${this.apiBase}/api/radio/detail`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    radioId: radioId,
                    pageSize: 20
                })
            });
            
            let data = await response.json();
            
            // 如果返回错误且建议使用模拟数据，则使用模拟数据
            if (data.useMockData) {
                response = await fetch(`${this.apiBase}/api/mock/radio/detail/${radioId}`);
                data = await response.json();
            }
            
            if (data.payload && data.payload.songInfos) {
                this.playlist = data.payload.songInfos;
                this.renderPlaylist();
                
                // 自动播放第一首
                if (this.playlist.length > 0) {
                    this.currentSongIndex = 0;
                    this.playSong(0);
                }
            } else {
                throw new Error('Invalid response format');
            }
        } catch (error) {
            console.error('Failed to load radio songs:', error);
            throw error;
        }
    }
    
    renderPlaylist() {
        this.playlistEl.innerHTML = '';
        
        this.playlist.forEach((song, index) => {
            const item = document.createElement('div');
            item.className = 'song-item';
            if (index === this.currentSongIndex) {
                item.classList.add('playing');
            }
            
            item.innerHTML = `
                <div>
                    <strong>${song.songName}</strong>
                    <div style="font-size: 0.9em; opacity: 0.7; margin-top: 3px;">
                        ${song.singerName} - ${song.albumName}
                    </div>
                </div>
                <div style="font-size: 0.9em;">
                    ${this.formatTime(song.songPlayTime)}
                </div>
            `;
            
            item.addEventListener('click', () => this.playSong(index));
            this.playlistEl.appendChild(item);
        });
        
        this.playlistContainer.style.display = 'block';
    }
    
    playSong(index) {
        if (index < 0 || index >= this.playlist.length) return;
        
        this.currentSongIndex = index;
        const song = this.playlist[index];
        
        // 更新歌曲信息
        this.songNameEl.textContent = song.songName;
        this.songArtistEl.textContent = '歌手: ' + song.singerName;
        this.songAlbumEl.textContent = '专辑: ' + song.albumName;
        this.songCoverEl.src = song.albumPic;
        
        // 设置播放源
        // 注意：真实场景需要通过 /api/song/detail 获取最新的播放链接
        this.audioPlayer.src = song.songPlayUrl;
        
        // 显示播放器
        this.currentPlayingEl.style.display = 'block';
        
        // 更新播放列表高亮
        document.querySelectorAll('.song-item').forEach((item, i) => {
            if (i === index) {
                item.classList.add('playing');
            } else {
                item.classList.remove('playing');
            }
        });
        
        // 播放
        this.audioPlayer.play().catch(err => {
            console.error('播放失败:', err);
            if (this.serverMode === 'mock') {
                this.showMessage('播放失败：模拟数据的播放链接可能已失效。使用真实 API 可获取有效链接。', 'error');
            } else {
                this.showMessage('播放失败：' + err.message, 'error');
            }
        });
    }
    
    togglePlay() {
        if (this.audioPlayer.paused) {
            this.audioPlayer.play();
        } else {
            this.audioPlayer.pause();
        }
    }
    
    playNext() {
        if (this.currentSongIndex < this.playlist.length - 1) {
            this.playSong(this.currentSongIndex + 1);
        } else {
            // 循环播放
            this.playSong(0);
        }
    }
    
    playPrevious() {
        if (this.currentSongIndex > 0) {
            this.playSong(this.currentSongIndex - 1);
        } else {
            // 跳到最后一首
            this.playSong(this.playlist.length - 1);
        }
    }
    
    updateProgress() {
        const progress = (this.audioPlayer.currentTime / this.audioPlayer.duration) * 100;
        this.progressEl.style.width = progress + '%';
    }
    
    updatePlayButton(isPlaying) {
        this.playPauseBtn.textContent = isPlaying ? '⏸ 暂停' : '▶ 播放';
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    showMessage(message, type = 'error') {
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
    new RadioPlayer();
});
