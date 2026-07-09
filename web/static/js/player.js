/**
 * 余音 - 音乐播放器JavaScript
 */

// 播放器状态
let audioElement = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    audioElement = document.getElementById('audio-player');
    if (!audioElement) {
        audioElement = document.createElement('audio');
        audioElement.id = 'audio-player';
        audioElement.preload = 'auto';
        document.body.appendChild(audioElement);
    }

    audioElement.addEventListener('timeupdate', onTimeUpdate);
    audioElement.addEventListener('loadedmetadata', onLoadedMetadata);

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

    audioElement.volume = 0.8;
});

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

function onLoadedMetadata() {
    var timeTotal = document.getElementById('time-total');
    if (audioElement && timeTotal) {
        timeTotal.textContent = formatTime(audioElement.duration);
    }
}

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

function seekBackward() {
    if (audioElement) {
        audioElement.currentTime = Math.max(0, audioElement.currentTime - 10);
    }
}

function seekForward() {
    if (audioElement && audioElement.duration) {
        audioElement.currentTime = Math.min(audioElement.duration, audioElement.currentTime + 10);
    }
}

function onSeek() {
    if (audioElement && audioElement.duration) {
        var slider = document.getElementById('progress-slider');
        audioElement.currentTime = (slider.value / 100) * audioElement.duration;
    }
}

function onVolumeChange() {
    if (audioElement) {
        audioElement.volume = document.getElementById('volume-slider').value / 100;
    }
}

function formatTime(seconds) {
    if (isNaN(seconds) || seconds === 0) return '0:00';
    var mins = Math.floor(seconds / 60);
    var secs = Math.floor(seconds % 60);
    return mins + ':' + secs.toString().padStart(2, '0');
}

function playTrackById(trackId) {
    if (!audioElement) return;
    var url = '/api/serve-audio/' + trackId;
    audioElement.src = url;
    audioElement.load();
    fetch('/api/track/' + trackId)
        .then(function(response) { return response.json(); })
        .then(function(track) {
            var titleEl = document.getElementById('track-title');
            var artistEl = document.getElementById('track-artist');
            if (titleEl) titleEl.textContent = track.title;
            if (artistEl) artistEl.textContent = track.artist;
        });
    audioElement.play().catch(function(err) {
        console.error('Play error:', err);
    });
}

window.playTrackById = playTrackById;
