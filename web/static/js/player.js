/**
 * 余音 - 音乐播放器JavaScript
 */

// 播放器状态
let audioElement = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 获取或创建音频元素
    audioElement = document.getElementById('audio-player');
    if (!audioElement) {
        audioElement = document.createElement('audio');
        audioElement.id = 'audio-player';
        audioElement.preload = 'auto';
        document.body.appendChild(audioElement);
    }

    // 监听音频事件
    audioElement.addEventListener('timeupdate', onTimeUpdate);
    audioElement.addEventListener('loadedmetadata', onLoadedMetadata);

    // 绑定按钮事件
    var playBtn = document.getElementById('play-btn');
    var prevBtn = document.getElementById('prev-btn');
    var nextBtn = document.getElementById('next-btn');
    var progressSlider = document.getElementById('progress-slider');
    var volumeSlider = document.getElementById('volume-slider');

    if (playBtn) playBtn.addEventListener('click', togglePlay);
    if (prevBtn) prevBtn.addEventListener('click', seekBackward);
    if (nextBtn) nextBtn.addEventListener('click', seekForward);
    if (progressSlider) progressSlider.addEventListener('input', onSeek);
    if (volumeSlider) volumeSlider.addEventListener('input', onVolumeChange);

    // 初始音量
    audioElement.volume = 0.8;
});

// 时间更新
function onTimeUpdate() {
    if (!audioElement || !audioElement.duration) return;

    var current = audioElement.currentTime;
    var duration = audioElement.duration;
    var percent = (current / duration) * 100;

    var slider = document.getElementById('progress-slider');
    var timeCurrent = document.getElementById('time-current');

    if (slider && !slider.matches(':active')) {
        slider.value = percent;
    }
    if (timeCurrent) {
        timeCurrent.textContent = formatTime(current);
    }
}

// 元数据加载完成
function onLoadedMetadata() {
    var timeTotal = document.getElementById('time-total');
    if (audioElement && timeTotal) {
        timeTotal.textContent = formatTime(audioElement.duration);
    }
}

// 播放/暂停切换
function togglePlay() {
    if (!audioElement || !audioElement.src) return;

    if (audioElement.paused) {
        audioElement.play();
        document.getElementById('play-btn').textContent = '||';
    } else {
        audioElement.pause();
        document.getElementById('play-btn').textContent = '>';
    }
}

// 快退10秒
function seekBackward() {
    if (audioElement) {
        audioElement.currentTime = Math.max(0, audioElement.currentTime - 10);
    }
}

// 快进10秒
function seekForward() {
    if (audioElement && audioElement.duration) {
        audioElement.currentTime = Math.min(audioElement.duration, audioElement.currentTime + 10);
    }
}

// 跳转
function onSeek() {
    if (audioElement && audioElement.duration) {
        var slider = document.getElementById('progress-slider');
        audioElement.currentTime = (slider.value / 100) * audioElement.duration;
    }
}

// 音量
function onVolumeChange() {
    if (audioElement) {
        audioElement.volume = document.getElementById('volume-slider').value / 100;
    }
}

// 时间更新
function onTimeUpdate() {
    if (!audioElement || !audioElement.duration) return;

    var current = audioElement.currentTime;
    var duration = audioElement.duration;
    var percent = (current / duration) * 100;

    var slider = document.getElementById('progress-slider');
    var timeCurrent = document.getElementById('time-current');

    if (slider && !slider.matches(':active')) {
        slider.value = percent;
    }
    if (timeCurrent) {
        timeCurrent.textContent = formatTime(current);
    }
}

// 格式化时间
function formatTime(seconds) {
    if (isNaN(seconds) || seconds === 0) return '00:00';
    var mins = Math.floor(seconds / 60);
    var secs = Math.floor(seconds % 60);
    return mins.toString().padStart(2, '0') + ':' + secs.toString().padStart(2, '0');
}

// 播放指定曲目
function playTrackById(trackId) {
    if (!audioElement) return;

    var url = '/api/serve-audio/' + trackId;
    audioElement.src = url;
    audioElement.load();

    fetch('/api/track/' + trackId)
        .then(function(response) { return response.json(); })
        .then(function(track) {
            document.getElementById('track-title').textContent = track.title;
            document.getElementById('track-artist').textContent = track.artist;
        });

    audioElement.play().catch(function(err) {
        console.error('Play error:', err);
    });
}

// 暴露到全局
window.playTrackById = playTrackById;