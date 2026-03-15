// QQ 音乐电台播放器 - 直接播放版本

class RadioPlayer {
    constructor() {
        this.apiBase = window.location.origin;
        this.currentRadio = null;
        this.currentSong = null;
        this.playlist = [];
        this.audioPlayer = new Audio();
        
        // 绑定 DOM 元素
        this.radioListEl = document.getElementById('radio-list');
        this.playlistEl = document.getElementById('playlist');
        this.playlistContainer = document.getElementById('playlist-container');
        this.messageContainer = document.getElementById('message-container');
        this.playerContent = document.getElementById('player-content');
        this.currentSongEl = document.getElementById('current-song');
        this.currentSongNameEl = document.getElementById('current-song-name');
        this.currentSongArtistEl = document.getElementById('current-song-artist');
        
        // 绑定音频事件
        this.audioPlayer.addEventListener('error', (e) => {
            console.error('播放错误:', e);
            this.showPlayerMessage('播放失败，正在尝试下一首...', 'error');
            setTimeout(() => this.playNext(), 2000);
        });
        
        this.audioPlayer.addEventListener('ended', () => {
            this.playNext();
        });
        
        this.audioPlayer.addEventListener('play', () => {
            this.updatePlayButton(true);
        });
        
        this.audioPlayer.addEventListener('pause', () => {
            this.updatePlayButton(false);
        });
        
        // 加载电台列表
        this.loadRadioList();
    }
    
    async loadRadioList() {
        try {
            const response = await fetch(`${this.apiBase}/api/radio/list`);
            const data = await response.json();
            
            if (data.code === 0 && data.payload && data.payload.radioInfos) {
                this.renderRadioList(data.payload.radioInfos);
            } else {
                throw new Error('Invalid response format');
            }
        } catch (error) {
            console.error('Failed to load radio list:', error);
            this.showMessage('加载歌单列表失败: ' + error.message, 'error');
        }
    }
    
    renderRadioList(radios) {
        this.radioListEl.innerHTML = '';
        
        radios.forEach(radio => {
            const card = document.createElement('div');
            card.className = 'radio-card';
            card.innerHTML = `
                <img src="${radio.radioPic}" alt="${radio.radioName}" onerror="this.src='https://y.gtimg.cn/music/photo_new/T002R300x300M000003rmKmG3HZfbK.jpg'">
                <h3 title="${radio.radioName}">${radio.radioName}</h3>
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
            
            // 加载歌单歌曲
            await this.loadRadioSongs(radio.radioId);
            
            this.clearMessage();
        } catch (error) {
            this.showMessage('加载歌曲列表失败: ' + error.message, 'error');
        }
    }
    
    async loadRadioSongs(radioId) {
        try {
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
                this.currentSongIndex = 0;
                this.renderPlaylist();
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
        
        if (this.playlist.length === 0) {
            this.playlistEl.innerHTML = '<div class="info">暂无可播放歌曲</div>';
            this.playlistContainer.style.display = 'block';
            return;
        }
        
        this.playlist.forEach((song, index) => {
            const item = document.createElement('div');
            item.className = 'song-item';
            
            item.innerHTML = `
                <div class="song-info-text">
                    <strong>${song.songName}</strong>
                    <div class="artist">${song.singerName}</div>
                </div>
                <button class="play-btn" data-index="${index}">▶ 播放</button>
            `;
            
            const playBtn = item.querySelector('.play-btn');
            playBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.playSong(index);
            });
            
            this.playlistEl.appendChild(item);
        });
        
        this.playlistContainer.style.display = 'block';
    }
    
    async playSong(index) {
        if (index < 0 || index >= this.playlist.length) return;
        
        // 先停止并清理旧的音频
        if (this.audioPlayer) {
            this.audioPlayer.pause();
            this.audioPlayer.src = '';
        }
        
        this.currentSongIndex = index;
        const song = this.playlist[index];
        
        // 更新当前播放歌曲
        this.currentSong = song;
        
        // 更新播放列表高亮
        document.querySelectorAll('.song-item').forEach((item, i) => {
            if (i === index) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        // 更新当前歌曲信息
        this.currentSongNameEl.textContent = song.songName;
        this.currentSongArtistEl.textContent = `${song.singerName} - ${song.albumName}`;
        this.currentSongEl.style.display = 'block';
        
        // 显示加载状态
        this.showPlayerMessage('正在获取播放链接...', 'info');
        
        try {
            // 获取播放链接
            const response = await fetch(`${this.apiBase}/api/song/url`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ songMId: song.songMId })
            });
            
            const data = await response.json();
            
            if (data.code === 0 && data.url) {
                // 先清理旧的播放器
                if (this.audioPlayer && this.audioPlayer.src) {
                    this.audioPlayer.pause();
                    this.audioPlayer.src = '';
                }
                
                // 设置新的音频源
                this.audioPlayer.src = data.url;
                
                // 播放音乐
                this.audioPlayer.play().then(() => {
                    this.showPlayerUI();
                }).catch(err => {
                    console.error('播放失败:', err);
                    // 如果播放失败，提供在 QQ 音乐打开的选项
                    this.showPlayerFallback(song);
                });
            } else {
                // 没有播放链接，提供在 QQ 音乐打开的选项
                this.showPlayerFallback(song);
            }
        } catch (error) {
            console.error('获取播放链接失败:', error);
            this.showPlayerFallback(song);
        }
    }
    
    showPlayerUI() {
        this.playerContent.innerHTML = `
            <div class="audio-player">
                <div class="player-cover">
                    <img src="${this.currentSong.albumPic}" alt="封面" onerror="this.src='https://y.gtimg.cn/music/photo_new/T002R300x300M000003rmKmG3HZfbK.jpg'">
                </div>
                <div class="player-controls">
                    <button class="control-btn" id="prev-btn">⏮</button>
                    <button class="control-btn large" id="play-pause-btn">⏸</button>
                    <button class="control-btn" id="next-btn">⏭</button>
                </div>
                <div class="player-progress">
                    <span id="current-time">0:00</span>
                    <div class="progress-bar">
                        <div class="progress" id="progress"></div>
                    </div>
                    <span id="total-time">0:00</span>
                </div>
                <audio id="audio-display" controls style="width: 100%; margin-top: 15px;"></audio>
            </div>
        `;
        
        // 显示当前播放器状态（只是显示，不创建新的 audio）
        const audioDisplay = document.getElementById('audio-display');
        audioDisplay.src = this.audioPlayer.src;
        audioDisplay.currentTime = this.audioPlayer.currentTime;
        
        // 同步播放状态
        if (!this.audioPlayer.paused) {
            audioDisplay.play().catch(err => console.log('Display sync error:', err));
        }
        
        // 双向同步：用户在 HTML audio 控件上操作也要同步到主播放器
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
        document.getElementById('next-btn').addEventListener('click', () => this.playNext());
        document.getElementById('play-pause-btn').addEventListener('click', () => this.togglePlay());
    }
    
    showPlayerFallback(song) {
        const qqMusicUrl = `https://y.qq.com/n/ryqq/songDetail/${song.songMId}`;
        
        this.playerContent.innerHTML = `
            <div class="player-fallback">
                <div class="fallback-icon">⚠️</div>
                <h3>无法直接播放</h3>
                <p>由于版权限制，该歌曲无法在浏览器中直接播放</p>
                <div class="fallback-buttons">
                    <a href="${qqMusicUrl}" target="_blank" class="fallback-btn primary">
                        🎵 在 QQ 音乐打开
                    </a>
                    <button class="fallback-btn" onclick="window.qqPlayer.playNext()">
                        ⏭ 播放下一首
                    </button>
                </div>
            </div>
        `;
        
        // 暴露到全局以供按钮调用
        window.qqPlayer = this;
    }
    
    showPlayerMessage(message, type = 'info') {
        this.playerContent.innerHTML = `
            <div class="player-message ${type}">
                <div class="message-icon">${type === 'error' ? '❌' : 'ℹ️'}</div>
                <p>${message}</p>
            </div>
        `;
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
            this.playSong(0); // 循环播放
        }
    }
    
    playPrevious() {
        if (this.currentSongIndex > 0) {
            this.playSong(this.currentSongIndex - 1);
        } else {
            this.playSong(this.playlist.length - 1);
        }
    }
    
    updatePlayButton(isPlaying) {
        const btn = document.getElementById('play-pause-btn');
        if (btn) {
            btn.textContent = isPlaying ? '⏸' : '▶';
        }
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
