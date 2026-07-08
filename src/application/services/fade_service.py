"""淡入淡出服务"""
import time
import threading
from typing import Callable, Optional
from dataclasses import dataclass


@dataclass
class FadeConfig:
    """淡入淡出配置"""
    fade_in_duration: float = 1.0  # 淡入时长（秒）
    fade_out_duration: float = 1.0  # 淡出时长（秒）
    steps: int = 20  # 渐变步数


class FadeController:
    """淡入淡出控制器"""

    def __init__(self, config: FadeConfig = None):
        self.config = config or FadeConfig()
        self._current_volume = 0.0
        self._target_volume = 0.0
        self._is_fading = False
        self._fade_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._volume_callback: Optional[Callable[[float], None]] = None

    def set_volume_callback(self, callback: Callable[[float], None]):
        """设置音量回调"""
        self._volume_callback = callback

    def fade_in(self, target_volume: float = 1.0, callback: Callable = None):
        """淡入"""
        if self._is_fading:
            self._stop_event.set()
            if self._fade_thread:
                self._fade_thread.join(timeout=1)

        self._target_volume = target_volume
        self._stop_event.clear()
        self._is_fading = True

        self._fade_thread = threading.Thread(
            target=self._fade_worker,
            args=(self._current_volume, target_volume, self.config.fade_in_duration, callback),
            daemon=True
        )
        self._fade_thread.start()

    def fade_out(self, callback: Callable = None):
        """淡出"""
        if self._is_fading:
            self._stop_event.set()
            if self._fade_thread:
                self._fade_thread.join(timeout=1)

        self._stop_event.clear()
        self._is_fading = True

        self._fade_thread = threading.Thread(
            target=self._fade_worker,
            args=(self._current_volume, 0.0, self.config.fade_out_duration, callback),
            daemon=True
        )
        self._fade_thread.start()

    def fade_to(self, target_volume: float, duration: float = None, callback: Callable = None):
        """渐变到指定音量"""
        if self._is_fading:
            self._stop_event.set()
            if self._fade_thread:
                self._fade_thread.join(timeout=1)

        self._stop_event.clear()
        self._is_fading = True

        if duration is None:
            duration = self.config.fade_in_duration

        self._fade_thread = threading.Thread(
            target=self._fade_worker,
            args=(self._current_volume, target_volume, duration, callback),
            daemon=True
        )
        self._fade_thread.start()

    def _fade_worker(self, start: float, end: float, duration: float, callback: Callable = None):
        """淡入淡出工作线程"""
        step_duration = duration / self.config.steps

        for i in range(self.config.steps + 1):
            if self._stop_event.is_set():
                break

            # 线性插值
            progress = i / self.config.steps
            self._current_volume = start + (end - start) * progress

            # 回调
            if self._volume_callback:
                self._volume_callback(self._current_volume)

            if callback:
                callback(self._current_volume)

            time.sleep(step_duration)

        self._current_volume = end
        self._is_fading = False

        if self._volume_callback:
            self._volume_callback(self._current_volume)

    @property
    def current_volume(self) -> float:
        return self._current_volume

    @property
    def is_fading(self) -> bool:
        return self._is_fading

    def stop(self):
        """停止淡入淡出"""
        self._stop_event.set()
        if self._fade_thread:
            self._fade_thread.join(timeout=1)
        self._is_fading = False


class CrossfadeController:
    """交叉淡入淡出控制器"""

    def __init__(self, fade_duration: float = 1.0):
        self.fade_duration = fade_duration
        self._fade_out_controller = FadeController(FadeConfig(fade_out_duration=fade_duration))
        self._fade_in_controller = FadeController(FadeConfig(fade_in_duration=fade_duration))
        self._on_fade_out_volume: Optional[Callable[[float], None]] = None
        self._on_fade_in_volume: Optional[Callable[[float], None]] = None

    def set_callbacks(self, fade_out_cb: Callable, fade_in_cb: Callable):
        """设置回调"""
        self._on_fade_out_volume = fade_out_cb
        self._on_fade_in_volume = fade_in_cb

        self._fade_out_controller.set_volume_callback(fade_out_cb)
        self._fade_in_controller.set_volume_callback(fade_in_cb)

    def crossfade(self, fade_out_callback: Callable = None, fade_in_callback: Callable = None):
        """交叉淡入淡出"""
        # 淡出当前
        self._fade_out_controller.fade_out(callback=fade_out_callback)

        # 延迟后淡入新的
        def delayed_fade_in():
            time.sleep(self.fade_duration * 0.5)
            self._fade_in_controller.fade_in(callback=fade_in_callback)

        thread = threading.Thread(target=delayed_fade_in, daemon=True)
        thread.start()

    def stop(self):
        """停止"""
        self._fade_out_controller.stop()
        self._fade_in_controller.stop()


# 全局淡入淡出控制器
fade_controller = FadeController()
crossfade_controller = CrossfadeController()