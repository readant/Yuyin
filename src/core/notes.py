"""核心音符和调性数据"""
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Note:
    """音符数据类"""
    value: str  # 音符值 (1-7, _1-_7, 1_-7_)
    duration: float = 1.0  # 时值
    is_bar: bool = False  # 是否为小节线
    is_space: bool = False  # 是否为空格
    lyric: str = ""  # 歌词
    dot: bool = False  # 附点
    lines: int = 0  # 减时线数量


# 调性配置
KEY_CONFIGS = {
    'D': {
        'name': 'D调',
        'base_freq': 293.66,  # D4
        'fingering_types': ['5', '2'],
        'range': ('_5', '6_')
    },
    'G': {
        'name': 'G调',
        'base_freq': 392.00,  # G4
        'fingering_types': ['5', '2'],
        'range': ('_5', '6_')
    },
    'C': {
        'name': 'C调',
        'base_freq': 261.63,  # C4
        'fingering_types': ['1', '5'],
        'range': ('_1', '7_')
    },
    'F': {
        'name': 'F调',
        'base_freq': 349.23,  # F4
        'fingering_types': ['5'],
        'range': ('_5', '6_')
    },
    'E': {
        'name': 'E调',
        'base_freq': 329.63,  # E4
        'fingering_types': ['5', '2'],
        'range': ('_5', '6_')
    }
}

# 筒音作5的指法表
FINGERING_MAP_5 = {
    # 低音
    '(5)': [1, 1, 1, 1, 1, 1],  # ●●●●●●
    '(6)': [1, 1, 1, 1, 1, 0],  # ●●●●●○
    '(7)': [1, 1, 1, 1, 0, 0],  # ●●●●○○
    # 中音
    '1': [1, 1, 1, 0, 0, 0],    # ●●●○○○
    '2': [1, 1, 0, 0, 0, 0],    # ●●○○○○
    '3': [1, 0, 0, 0, 0, 0],    # ●○○○○○
    '4': [0, 1, 1, 0, 0, 0],    # ○●●○○○ (特殊指法)
    '5': [0, 1, 1, 1, 1, 1],    # ○●●●●●
    '6': [0, 0, 0, 0, 0, 1],    # ○○○○○● (或 [0,0,0,0,1,1])
    '7': [0, 0, 0, 0, 1, 1],    # ○○○○●●
    # 高音
    '[1]': [1, 1, 0, 0, 0, 0],  # ●●○○○○
    '[2]': [1, 0, 0, 0, 0, 0],  # ●○○○○○
    '[3]': [0, 1, 1, 0, 0, 0],  # ○●●○○○
    '[4]': [0, 1, 0, 0, 0, 0],  # ○●○○○○
    '[5]': [0, 0, 1, 0, 0, 0],  # ○○●○○○
}

# 筒音作1的指法表
FINGERING_MAP_1 = {
    # 中音
    '1': [1, 1, 1, 1, 1, 1],    # ●●●●●●
    '2': [1, 1, 1, 1, 1, 0],    # ●●●●●○
    '3': [1, 1, 1, 1, 0, 0],    # ●●●●○○
    '4': [1, 1, 1, 0, 0, 0],    # ●●●○○○
    '5': [1, 1, 0, 0, 0, 0],    # ●●○○○○
    '6': [1, 0, 0, 0, 0, 0],    # ●○○○○○
    '7': [0, 1, 1, 0, 0, 0],    # ○●●○○○
    # 高音
    '[1]': [0, 1, 1, 1, 1, 1],  # ○●●●●●
    '[2]': [0, 0, 0, 0, 0, 1],  # ○○○○○●
    '[3]': [0, 0, 0, 0, 1, 1],  # ○○○○●●
    '[4]': [0, 0, 0, 1, 1, 1],  # ○○○●●●
    '[5]': [0, 0, 1, 1, 1, 1],  # ○○●●●●
}

# 筒音作2的指法表
FINGERING_MAP_2 = {
    # 低音
    '_2': [1, 1, 1, 1, 1, 1],   # ●●●●●●
    '_1': [1, 1, 1, 1, 1, 0],   # ●●●●●○
    '7': [1, 1, 1, 1, 0, 0],    # ●●●●○○
    # 中音
    '1': [1, 1, 1, 0, 0, 0],    # ●●●○○○
    '2': [1, 1, 0, 0, 0, 0],    # ●●○○○○
    '3': [1, 0, 0, 0, 0, 0],    # ●○○○○○
    '4': [0, 1, 1, 0, 0, 0],    # ○●●○○○
    '5': [0, 1, 1, 1, 1, 1],    # ○●●●●●
    '6': [0, 0, 0, 0, 0, 1],    # ○○○○○●
    '7': [0, 0, 0, 0, 1, 1],    # ○○○○●●
    # 高音
    '[1]': [1, 1, 0, 0, 0, 0],  # ●●○○○○
    '[2]': [1, 0, 0, 0, 0, 0],  # ●○○○○○
    '[3]': [0, 1, 1, 0, 0, 0],  # ○●●○○○
    '[4]': [0, 1, 0, 0, 0, 0],  # ○●○○○○
    '[5]': [0, 0, 1, 0, 0, 0],  # ○○●○○○
}


def get_fingering_map(fingering_type: str) -> Dict[str, List[int]]:
    """获取指法映射表"""
    if fingering_type == '5':
        return FINGERING_MAP_5
    elif fingering_type == '1':
        return FINGERING_MAP_1
    elif fingering_type == '2':
        return FINGERING_MAP_2
    return FINGERING_MAP_5


def parse_notes(text: str) -> List[Note]:
    """解析简谱文本为音符列表"""
    notes = []
    parts = text.split()
    
    for part in parts:
        if part == '|':
            notes.append(Note(value='|', is_bar=True))
        elif part == '-':
            notes.append(Note(value='-', duration=1.0))
        else:
            # 处理音符
            note = Note(value=part)
            notes.append(note)
    
    return notes


def notes_to_text(notes: List[Note]) -> str:
    """将音符列表转换为文本"""
    parts = []
    for note in notes:
        if note.is_bar:
            parts.append('|')
        else:
            parts.append(note.value)
    return ' '.join(parts)


def get_note_display_name(note_value: str) -> str:
    """获取音符显示名称"""
    if note_value.startswith('(') and note_value.endswith(')'):
        return f"低音{note_value[1:-1]}"
    elif note_value.startswith('[') and note_value.endswith(']'):
        return f"高音{note_value[1:-1]}"
    else:
        return f"中音{note_value}"


def get_fingering_display(fingering: List[int]) -> str:
    """获取指法显示字符串"""
    return ''.join(['●' if f else '○' for f in fingering])


def get_all_notes_for_fingering(fingering_type: str) -> List[str]:
    """获取指定指法类型下的所有音符"""
    fingering_map = get_fingering_map(fingering_type)
    return list(fingering_map.keys())
