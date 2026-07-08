"""中国风配色方案"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class Palette:
    """配色方案"""
    name: str
    display_name: str

    background: str
    surface: str
    panel_bg: str

    primary: str
    primary_light: str
    primary_dark: str

    secondary: str
    accent: str

    text: str
    text_secondary: str
    text_light: str

    border: str
    border_light: str

    success: str
    warning: str
    error: str

    player_bg: str
    spectrum_1: str
    spectrum_2: str
    spectrum_3: str

    button_bg: str
    button_hover: str
    button_pressed: str
    button_disabled: str

    progress_bg: str
    progress_fill: str
    slider_bg: str
    slider_fill: str
    slider_handle: str

    input_bg: str
    input_border: str
    input_focus: str

    gold: str
    ink: str
    paper: str
    vermilion: str


# 水墨素雅（默认）
SHUI_MO = Palette(
    name="shui_mo",
    display_name="水墨素雅",
    background="#F5F0E8",
    surface="#EDE8DC",
    panel_bg="#FAF7F0",
    primary="#8B2500",
    primary_light="#A63200",
    primary_dark="#6B1D00",
    secondary="#9B7653",
    accent="#2B5B84",
    text="#2C2C2C",
    text_secondary="#6B6B6B",
    text_light="#9B9B9B",
    border="#C4B8A8",
    border_light="#D4CFC4",
    success="#4A7C59",
    warning="#C5A55A",
    error="#A63232",
    player_bg="#EDE8DC",
    spectrum_1="#2C2C2C",
    spectrum_2="#9B7653",
    spectrum_3="#8B2500",
    button_bg="#8B2500",
    button_hover="#A63200",
    button_pressed="#6B1D00",
    button_disabled="#C4B8A8",
    progress_bg="#D4CFC4",
    progress_fill="#8B2500",
    slider_bg="#D4CFC4",
    slider_fill="#8B2500",
    slider_handle="#8B2500",
    input_bg="#FFFFFF",
    input_border="#C4B8A8",
    input_focus="#8B2500",
    gold="#C5A55A",
    ink="#2C2C2C",
    paper="#F5F0E8",
    vermilion="#8B2500"
)

# 朱砂浓墨
ZHU_SHA = Palette(
    name="zhu_sha",
    display_name="朱砂浓墨",
    background="#1A1410",
    surface="#241E18",
    panel_bg="#2A231C",
    primary="#D4380D",
    primary_light="#E85A2E",
    primary_dark="#A82D0A",
    secondary="#8B7355",
    accent="#C5A55A",
    text="#F5F0E8",
    text_secondary="#B8A898",
    text_light="#7A6A5A",
    border="#3A3228",
    border_light="#4A4238",
    success="#5A8C6A",
    warning="#C5A55A",
    error="#D4380D",
    player_bg="#241E18",
    spectrum_1="#F5F0E8",
    spectrum_2="#C5A55A",
    spectrum_3="#D4380D",
    button_bg="#D4380D",
    button_hover="#E85A2E",
    button_pressed="#A82D0A",
    button_disabled="#3A3228",
    progress_bg="#3A3228",
    progress_fill="#D4380D",
    slider_bg="#3A3228",
    slider_fill="#D4380D",
    slider_handle="#D4380D",
    input_bg="#2A231C",
    input_border="#3A3228",
    input_focus="#D4380D",
    gold="#C5A55A",
    ink="#F5F0E8",
    paper="#1A1410",
    vermilion="#D4380D"
)

# 青瓷素雅
QING_CI = Palette(
    name="qing_ci",
    display_name="青瓷素雅",
    background="#F0F4F3",
    surface="#E4EAE8",
    panel_bg="#F8FAF9",
    primary="#3A7D6E",
    primary_light="#4A9D8E",
    primary_dark="#2A5D4E",
    secondary="#6B8E7E",
    accent="#8B6B5A",
    text="#2C3C38",
    text_secondary="#5A6A66",
    text_light="#8A9A96",
    border="#C4D4D0",
    border_light="#D4E4E0",
    success="#3A7D6E",
    warning="#C5A55A",
    error="#A65252",
    player_bg="#E4EAE8",
    spectrum_1="#2C3C38",
    spectrum_2="#6B8E7E",
    spectrum_3="#3A7D6E",
    button_bg="#3A7D6E",
    button_hover="#4A9D8E",
    button_pressed="#2A5D4E",
    button_disabled="#C4D4D0",
    progress_bg="#D4E4E0",
    progress_fill="#3A7D6E",
    slider_bg="#D4E4E0",
    slider_fill="#3A7D6E",
    slider_handle="#3A7D6E",
    input_bg="#FFFFFF",
    input_border="#C4D4D0",
    input_focus="#3A7D6E",
    gold="#B8966A",
    ink="#2C3C38",
    paper="#F0F4F3",
    vermilion="#A65252"
)

PRESETS: Dict[str, Palette] = {
    SHUI_MO.name: SHUI_MO,
    ZHU_SHA.name: ZHU_SHA,
    QING_CI.name: QING_CI
}

DEFAULT_PALETTE = SHUI_MO