"""实时音频分析播放器"""
import numpy as np
import sounddevice as sd
import librosa
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
import queue
import threading
import time

from ...config import settings


class RealtimeAnalyzer(QObject):
    """实时音频分析器 - 分析传入的音频数据"""

    note_detected = pyqtSignal(str, float)  # 音符, 置信度

    def __init__(self):
        super().__init__()

        self.sample_rate = settings.audio.sample_rate
        self.is_running = False
        
        # 音高检测参数
        self.min_freq = 100
        self.max_freq = 2000
        
        # 频率到音符的映射
        self.note_freq_map = self._build_note_freq_map()
        
        # 分析线程
        self.analysis_thread = None
        self.audio_queue = queue.Queue(maxsize=10)
    
    def _build_note_freq_map(self):
        """构建频率到音符的映射表"""
        note_map = {}
        base_freq = 440.0
        base_note = 69
        
        for i in range(128):
            freq = base_freq * (2 ** ((i - base_note) / 12.0))
            note_name = self._midi_to_note(i)
            if note_name:
                note_map[i] = (note_name, freq)
        
        return note_map
    
    def _midi_to_note(self, midi_note):
        """MIDI编号转音符名称"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_note // 12) - 1
        note_index = midi_note % 12
        
        if octave < 2 or octave > 6:
            return None
        
        return f"{notes[note_index]}{octave}"
    
    def _note_name_to_simple(self, note_name):
        """音符名称转简谱"""
        if not note_name:
            return None
        
        note = note_name[:-1]
        octave = int(note_name[-1])
        
        note_map = {
            'C': '1', 'D': '2', 'E': '3', 'F': '4',
            'G': '5', 'A': '6', 'B': '7'
        }
        
        simple_note = note_map.get(note)
        if not simple_note:
            return None
        
        if octave == 3:
            return f"({simple_note})"
        elif octave == 4:
            return simple_note
        elif octave == 5:
            return f"[{simple_note}]"
        
        return simple_note
    
    def start(self):
        """开始分析"""
        self.is_running = True
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
    
    def stop(self):
        """停止分析"""
        self.is_running = False
        # 清空队列
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
    
    def feed_audio(self, audio_data):
        """传入音频数据进行分析"""
        if self.is_running:
            try:
                self.audio_queue.put_nowait(audio_data.copy())
            except queue.Full:
                pass
    
    def _analysis_loop(self):
        """分析循环"""
        while self.is_running:
            try:
                audio_data = self.audio_queue.get(timeout=0.1)
                
                # 检测音高
                pitch = self._detect_pitch(audio_data)
                
                if pitch > 0:
                    note_name, confidence = self._find_nearest_note(pitch)
                    
                    if note_name:
                        simple_note = self._note_name_to_simple(note_name)
                        if simple_note:
                            self.note_detected.emit(simple_note, confidence)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Analysis error: {e}")
    
    def _detect_pitch(self, audio_data):
        """检测音高"""
        try:
            # 根据音频长度调整 n_fft
            n_fft = min(2048, len(audio_data))
            if n_fft < 256:
                return 0
            
            pitches, magnitudes = librosa.piptrack(
                y=audio_data.astype(np.float32),
                sr=self.sample_rate,
                n_fft=n_fft,
                fmin=self.min_freq,
                fmax=self.max_freq
            )
            
            if magnitudes.shape[1] > 0:
                index = magnitudes[:, 0].argmax()
                pitch = pitches[index, 0]
                return pitch if pitch > 0 else 0
            
            return 0
        except:
            return 0
    
    def _find_nearest_note(self, freq):
        """找到最近的音符"""
        if freq <= 0:
            return None, 0
        
        best_note = None
        best_diff = float('inf')
        
        for midi_note, (note_name, note_freq) in self.note_freq_map.items():
            diff = abs(np.log2(freq / note_freq))
            
            if diff < best_diff:
                best_diff = diff
                best_note = note_name
        
        confidence = max(0, 1 - best_diff * 2)
        
        return best_note, confidence


class AudioPlaybackAnalyzer(QObject):
    """带分析的音频播放器"""
    
    position_changed = pyqtSignal(float)  # 位置(秒)
    note_detected = pyqtSignal(str)  # 检测到的音符
    playback_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.analyzer = RealtimeAnalyzer()
        self.analyzer.note_detected.connect(self._on_note_detected)

        # 播放状态
        self.is_playing = False
        self.audio_data = None
        self.sample_rate = settings.audio.sample_rate
        self.current_position = 0.0
        self.current_sample = 0
        
        # 播放线程
        self.play_thread = None
        self.stop_event = threading.Event()
    
    def load_file(self, file_path: str):
        """加载音频文件"""
        import soundfile as sf
        
        self.audio_data, self.sample_rate = sf.read(file_path, dtype='float32')
        
        if len(self.audio_data.shape) > 1:
            self.audio_data = np.mean(self.audio_data, axis=1)
        
        self.current_position = 0.0
        self.current_sample = 0
    
    def play(self):
        """开始播放和分析"""
        if self.audio_data is None:
            return
        
        self.is_playing = True
        self.stop_event.clear()
        
        # 启动分析器
        self.analyzer.start()
        
        # 启动播放线程
        self.play_thread = threading.Thread(target=self._play_loop, daemon=True)
        self.play_thread.start()
    
    def pause(self):
        """暂停"""
        self.is_playing = False
        self.analyzer.stop()
    
    def stop(self):
        """停止"""
        self.is_playing = False
        self.stop_event.set()
        self.analyzer.stop()
        self.current_position = 0.0
        self.current_sample = 0
    
    def _play_loop(self):
        """播放循环"""
        block_size = 1024
        
        def callback(outdata, frames, time_info, status):
            if self.stop_event.is_set() or not self.is_playing:
                raise sd.CallbackStop()
            
            start = self.current_sample
            end = start + frames
            
            if end >= len(self.audio_data):
                remaining = len(self.audio_data) - start
                if remaining > 0:
                    outdata[:remaining, 0] = self.audio_data[start:]
                    # 将音频数据传给分析器
                    self.analyzer.feed_audio(self.audio_data[start:])
                outdata[remaining:, 0] = 0
                self.playback_finished.emit()
                raise sd.CallbackStop()
            else:
                outdata[:, 0] = self.audio_data[start:end]
                # 将音频数据传给分析器
                self.analyzer.feed_audio(self.audio_data[start:end])
            
            self.current_sample = end
            self.current_position = self.current_sample / self.sample_rate
            self.position_changed.emit(self.current_position)
        
        with sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=block_size,
            callback=callback
        ) as stream:
            while self.is_playing and not self.stop_event.is_set():
                time.sleep(0.1)
    
    def _on_note_detected(self, note: str, confidence: float):
        """音符检测回调"""
        if confidence > 0.5:
            self.note_detected.emit(note)
    
    def get_position(self):
        """获取当前位置"""
        return self.current_position
    
    def get_duration(self):
        """获取总时长"""
        if self.audio_data is not None:
            return len(self.audio_data) / self.sample_rate
        return 0
