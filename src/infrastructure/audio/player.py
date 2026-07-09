"""音频播放器模块"""
import os
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices
from PyQt6.QtCore import QUrl
import sounddevice as sd

from .device_detector import audio_device_detector, AudioDeviceType


class AudioPlayer(QObject):
    """音频播放器"""

    # 信号
    position_changed = pyqtSignal(float)  # 当前位置(秒)
    duration_changed = pyqtSignal(float)  # 总时长(秒)
    state_changed = pyqtSignal(str)  # 状态: playing, paused, stopped
    playback_finished = pyqtSignal()
    device_changed = pyqtSignal(str)  # 设备变化信号

    def __init__(self):
        super().__init__()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)  # 设置默认音量为最大

        # 连接音频设备检测器
        audio_device_detector.device_changed.connect(self._on_device_changed)

        # 设置音频输出设备为系统默认
        self._set_default_audio_device()

        self.player.setAudioOutput(self.audio_output)

        # 连接信号
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
        self.player.mediaStatusChanged.connect(self._on_media_status)

        # 进度更新定时器
        self.progress_timer = QTimer()
        self.progress_timer.setInterval(50)  # 50ms更新一次
        self.progress_timer.timeout.connect(self._update_progress)

        # 状态
        self.current_file = None
        self.duration = 0
        self.is_playing = False

        # 音符时间映射
        self.note_timeline = []
        self.current_note_index = 0

    def _set_default_audio_device(self):
        """设置默认音频输出设备"""
        try:
            # 使用音频设备检测器获取默认设备
            device = audio_device_detector.current_device
            if device and device.device:
                self.audio_output.setDevice(device.device)
                print(f"使用音频设备: {device.name} ({device.device_type.value})")
            else:
                # 使用系统默认音频输出设备
                default_device = QMediaDevices.defaultAudioOutput()
                if not default_device.isNull():
                    self.audio_output.setDevice(default_device)
                    print(f"使用音频设备: {default_device.description()}")
                else:
                    print("警告: 未找到默认音频输出设备")
        except Exception as e:
            print(f"设置音频设备时出错: {e}")

    def _on_device_changed(self, device_name: str):
        """音频设备变化回调"""
        device = audio_device_detector.current_device
        if device:
            self.audio_output.setDevice(device.device)
            print(f"音频设备切换: {device.name} ({device.device_type.value})")
            self.device_changed.emit(device.name)

    def get_audio_devices(self):
        """获取可用的音频输出设备列表"""
        devices = []
        for device in QMediaDevices.audioOutputs():
            devices.append({
                'name': device.description(),
                'device': device
            })
        return devices

    def set_audio_device(self, device):
        """设置音频输出设备"""
        self.audio_output.setDevice(device)
    
    def load_file(self, file_path: str):
        """加载音频文件"""
        if os.path.exists(file_path):
            self.current_file = file_path
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.duration = self.player.duration() / 1000.0
    
    def play(self):
        """播放"""
        if self.current_file:
            self.player.play()
            self.progress_timer.start()
            self.is_playing = True
    
    def pause(self):
        """暂停"""
        self.player.pause()
        self.progress_timer.stop()
        self.is_playing = False
    
    def stop(self):
        """停止"""
        self.player.stop()
        self.progress_timer.stop()
        self.is_playing = False
        self.current_note_index = 0
    
    def set_position(self, position_ms: int):
        """设置播放位置(毫秒)"""
        self.player.setPosition(position_ms)
    
    def set_volume(self, volume: float):
        """设置音量 (0.0 - 1.0)"""
        self.audio_output.setVolume(volume)
    
    def get_position(self) -> float:
        """获取当前位置(秒)"""
        return self.player.position() / 1000.0
    
    def get_duration(self) -> float:
        """获取总时长(秒)"""
        return self.duration
    
    def set_note_timeline(self, timeline: list):
        """设置音符时间线 [(start_time, end_time, note_index), ...]"""
        self.note_timeline = timeline
        self.current_note_index = 0
    
    def get_current_note_index(self) -> int:
        """根据当前播放位置获取音符索引"""
        current_time = self.get_position()
        
        for start, end, index in self.note_timeline:
            if start <= current_time < end:
                return index
        
        return -1
    
    def _update_progress(self):
        """更新播放进度"""
        if self.is_playing:
            self.position_changed.emit(self.get_position())
    
    def _on_position_changed(self, position):
        """位置改变回调"""
        pass
    
    def _on_duration_changed(self, duration):
        """时长改变回调"""
        self.duration = duration / 1000.0
        self.duration_changed.emit(self.duration)
    
    def _on_state_changed(self, state):
        """状态改变回调"""
        from PyQt6.QtMultimedia import QMediaPlayer
        
        state_map = {
            QMediaPlayer.PlaybackState.StoppedState: 'stopped',
            QMediaPlayer.PlaybackState.PlayingState: 'playing',
            QMediaPlayer.PlaybackState.PausedState: 'paused'
        }
        
        self.state_changed.emit(state_map.get(state, 'unknown'))
    
    def _on_media_status(self, status):
        """媒体状态改变回调"""
        from PyQt6.QtMultimedia import QMediaPlayer
        
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.playback_finished.emit()
            self.progress_timer.stop()
            self.is_playing = False


class DemoPlayer(QObject):
    """演示播放器 - 播放音符MIDI"""
    
    note_played = pyqtSignal(int, str)  # 索引, 音符
    demo_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.notes = []
        self.fingering_map = {}
        self.bpm = 80
        self.is_playing = False
        self.current_index = 0
        
        # 播放线程
        self.play_thread = None
    
    def set_notes(self, notes: list, fingering_map: dict):
        """设置要播放的音符"""
        self.notes = notes
        self.fingering_map = fingering_map
    
    def set_bpm(self, bpm: int):
        """设置BPM"""
        self.bpm = bpm
    
    def play(self, start_index: int = 0):
        """开始播放演示"""
        if not self.notes:
            return
        
        self.is_playing = True
        self.current_index = start_index
        
        import threading
        import time
        
        def play_notes():
            beat_duration = 60.0 / self.bpm
            
            while self.is_playing and self.current_index < len(self.notes):
                note = self.notes[self.current_index]
                
                if not note.is_bar and not note.is_space:
                    # 发送信号播放音符
                    self.note_played.emit(self.current_index, note.value)
                
                # 根据音符时值等待
                wait_time = beat_duration * note.duration
                time.sleep(wait_time)
                
                self.current_index += 1
            
            self.is_playing = False
            self.demo_finished.emit()
        
        self.play_thread = threading.Thread(target=play_notes, daemon=True)
        self.play_thread.start()
    
    def stop(self):
        """停止播放"""
        self.is_playing = False
    
    def pause(self):
        """暂停"""
        self.is_playing = False
    
    def get_position(self) -> int:
        """获取当前音符索引"""
        return self.current_index
