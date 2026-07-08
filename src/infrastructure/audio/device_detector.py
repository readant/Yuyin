"""音频设备检测模块"""
import platform
from enum import Enum
from typing import Optional, List
from PyQt6.QtMultimedia import QMediaDevices, QAudioDevice
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class AudioDeviceType(Enum):
    """音频设备类型"""
    UNKNOWN = "unknown"
    SPEAKER = "speaker"
    HEADPHONE = "headphone"
    BLUETOOTH = "bluetooth"
    USB = "usb"
    HDMI = "hdmi"


class AudioDevice:
    """音频设备信息"""

    def __init__(self, device: QAudioDevice, device_type: AudioDeviceType = AudioDeviceType.UNKNOWN):
        self.device = device
        self.device_type = device_type
        self.name = device.description()
        self.is_default = device == QMediaDevices.defaultAudioOutput()

    @property
    def id(self) -> str:
        return self.device.id().data().decode() if self.device.id() else ""

    def __repr__(self):
        return f"AudioDevice({self.name}, {self.device_type.value})"


class AudioDeviceDetector(QObject):
    """音频设备检测器"""

    device_changed = pyqtSignal(str)  # 设备变化信号
    devices_updated = pyqtSignal(list)  # 设备列表更新信号

    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_device: Optional[AudioDevice] = None
        self._devices: List[AudioDevice] = []

        # 定时检测设备变化
        self._check_timer = QTimer()
        self._check_timer.setInterval(2000)  # 每2秒检查一次
        self._check_timer.timeout.connect(self._check_devices)
        self._check_timer.start()

        # 初始检测
        self._check_devices()

    def _check_devices(self):
        """检测音频设备"""
        try:
            # 获取当前设备
            current = QMediaDevices.defaultAudioOutput()

            # 检测设备类型
            device_type = self._detect_device_type(current)

            # 创建设备对象
            new_device = AudioDevice(current, device_type)

            # 检查是否变化
            if self._current_device is None or new_device.id != self._current_device.id:
                self._current_device = new_device
                self.device_changed.emit(new_device.name)

            # 更新设备列表
            self._update_device_list()

        except Exception as e:
            print(f"检测音频设备时出错: {e}")

    def _detect_device_type(self, device: QAudioDevice) -> AudioDeviceType:
        """检测设备类型"""
        name = device.description().lower()

        # 关键词匹配
        if any(keyword in name for keyword in ["耳机", "headphone", "headset", "earphone"]):
            return AudioDeviceType.HEADPHONE
        elif any(keyword in name for keyword in ["蓝牙", "bluetooth", "bt"]):
            return AudioDeviceType.BLUETOOTH
        elif any(keyword in name for keyword in ["usb"]):
            return AudioDeviceType.USB
        elif any(keyword in name for keyword in ["hdmi"]):
            return AudioDeviceType.HDMI
        elif any(keyword in name for keyword in ["扬声器", "speaker", "喇叭"]):
            return AudioDeviceType.SPEAKER
        else:
            return AudioDeviceType.UNKNOWN

    def _update_device_list(self):
        """更新设备列表"""
        self._devices.clear()

        for device in QMediaDevices.audioOutputs():
            device_type = self._detect_device_type(device)
            audio_device = AudioDevice(device, device_type)
            self._devices.append(audio_device)

        self.devices_updated.emit(self._devices)

    @property
    def current_device(self) -> Optional[AudioDevice]:
        """当前音频设备"""
        return self._current_device

    @property
    def devices(self) -> List[AudioDevice]:
        """所有可用设备"""
        return self._devices.copy()

    @property
    def is_headphone_connected(self) -> bool:
        """是否连接耳机"""
        return self._current_device and self._current_device.device_type == AudioDeviceType.HEADPHONE

    @property
    def is_bluetooth_connected(self) -> bool:
        """是否连接蓝牙"""
        return self._current_device and self._current_device.device_type == AudioDeviceType.BLUETOOTH

    @property
    def is_speaker(self) -> bool:
        """是否使用扬声器"""
        return self._current_device and self._current_device.device_type == AudioDeviceType.SPEAKER

    def get_device_type_name(self) -> str:
        """获取当前设备类型名称"""
        if self._current_device:
            type_names = {
                AudioDeviceType.HEADPHONE: "耳机",
                AudioDeviceType.BLUETOOTH: "蓝牙",
                AudioDeviceType.SPEAKER: "扬声器",
                AudioDeviceType.USB: "USB设备",
                AudioDeviceType.HDMI: "HDMI设备",
                AudioDeviceType.UNKNOWN: "未知设备"
            }
            return type_names.get(self._current_device.device_type, "未知设备")
        return "无设备"

    def get_device_icon(self) -> str:
        """获取当前设备图标"""
        if self._current_device:
            icons = {
                AudioDeviceType.HEADPHONE: "🎧",
                AudioDeviceType.BLUETOOTH: "📶",
                AudioDeviceType.SPEAKER: "🔊",
                AudioDeviceType.USB: "🔌",
                AudioDeviceType.HDMI: "📺",
                AudioDeviceType.UNKNOWN: "🔈"
            }
            return icons.get(self._current_device.device_type, "🔈")
        return "🔈"

    def set_device(self, device: QAudioDevice):
        """设置音频输出设备"""
        # 这里需要通过QMediaPlayer来设置设备
        # 由于QMediaPlayer的限制，我们只能通知设备变化
        device_type = self._detect_device_type(device)
        self._current_device = AudioDevice(device, device_type)
        self.device_changed.emit(device.description())


# 全局音频设备检测器实例
audio_device_detector = AudioDeviceDetector()