"""策略模式测试"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.audio.strategies import (
    AudioAnalyzerContext,
    LibrosaStrategy,
    SimpleStrategy,
)


def test_strategy_pattern():
    """测试策略模式"""
    print("=" * 50)
    print("策略模式测试")
    print("=" * 50)

    # 1. 测试上下文创建
    print("\n1. 创建上下文（默认策略）:")
    ctx = AudioAnalyzerContext()
    print(f"   当前策略: {ctx.current_strategy_name}")

    # 2. 测试获取可用策略
    print("\n2. 可用策略列表:")
    strategies = ctx.get_available_strategies()
    for s in strategies:
        print(f"   - {s['name']}: {s['instance'].description}")

    # 3. 测试切换策略
    print("\n3. 切换到Simple策略:")
    ctx.set_strategy_by_name('simple')
    print(f"   当前策略: {ctx.current_strategy_name}")

    # 4. 测试切换回Librosa
    print("\n4. 切换回Librosa策略:")
    ctx.set_strategy(LibrosaStrategy())
    print(f"   当前策略: {ctx.current_strategy_name}")

    # 5. 测试直接设置策略实例
    print("\n5. 直接设置策略实例:")
    simple = SimpleStrategy()
    ctx.set_strategy(simple)
    print(f"   当前策略: {ctx.current_strategy_name}")

    # 6. 测试频率转音符
    print("\n6. 频率转音符测试:")
    test_freqs = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]
    note_names = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4']

    ctx.set_strategy(LibrosaStrategy())
    print("   Librosa策略:")
    for freq, name in zip(test_freqs, note_names):
        note = ctx.pitch_to_note(freq)
        print(f"     {name} ({freq:.2f}Hz) -> {note}")

    ctx.set_strategy(SimpleStrategy())
    print("\n   Simple策略:")
    for freq, name in zip(test_freqs, note_names):
        note = ctx.pitch_to_note(freq)
        print(f"     {name} ({freq:.2f}Hz) -> {note}")

    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)


if __name__ == '__main__':
    test_strategy_pattern()