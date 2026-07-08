# 可复用UI组件
from .vinyl import VinylWidget
from .spectrum import SpectrumWidget
from .progress import ProgressWidget
from .fingering import FingeringWidget, FingeringDisplay
from .lyrics import LyricsWidget
from .animated_bg import AnimatedBackground, DynamicBackground
from .chinese_controls import QingButton, ScrollProgressBar, PluckVolumeSlider
from .transitions import CurtainTransition, InkSplashTransition, PageFlipTransition, TransitionManager

__all__ = ['VinylWidget', 'SpectrumWidget', 'ProgressWidget', 'FingeringWidget', 'FingeringDisplay', 'LyricsWidget', 'AnimatedBackground', 'DynamicBackground', 'QingButton', 'ScrollProgressBar', 'PluckVolumeSlider', 'CurtainTransition', 'InkSplashTransition', 'PageFlipTransition', 'TransitionManager']