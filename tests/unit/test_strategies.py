"""策略模式单元测试"""
import unittest
from src.application.strategies import (
    AudioAnalyzerContext,
    LibrosaStrategy,
    SimpleStrategy,
)


class TestAnalysisStrategy(unittest.TestCase):
    """测试分析策略"""

    def setUp(self):
        self.ctx = AudioAnalyzerContext()

    def test_default_strategy(self):
        """测试默认策略"""
        self.assertIsInstance(self.ctx.strategy, LibrosaStrategy)

    def test_get_available_strategies(self):
        """测试获取可用策略"""
        strategies = self.ctx.get_available_strategies()
        self.assertEqual(len(strategies), 2)
        names = [s['name'] for s in strategies]
        self.assertIn('librosa', names)
        self.assertIn('simple', names)

    def test_switch_strategy_by_name(self):
        """测试通过名称切换策略"""
        self.ctx.set_strategy_by_name('simple')
        self.assertIsInstance(self.ctx.strategy, SimpleStrategy)

    def test_switch_strategy_by_instance(self):
        """测试通过实例切换策略"""
        simple = SimpleStrategy()
        self.ctx.set_strategy(simple)
        self.assertEqual(self.ctx.strategy, simple)

    def test_invalid_strategy_name(self):
        """测试无效策略名称"""
        with self.assertRaises(ValueError):
            self.ctx.set_strategy_by_name('invalid')

    def test_pitch_to_note_librosa(self):
        """测试Librosa策略频率转音符"""
        self.ctx.set_strategy(LibrosaStrategy())
        # C4 = 261.63Hz -> 1
        self.assertEqual(self.ctx.pitch_to_note(261.63), '1')
        # A4 = 440Hz -> 6
        self.assertEqual(self.ctx.pitch_to_note(440.0), '6')

    def test_pitch_to_note_simple(self):
        """测试Simple策略频率转音符"""
        self.ctx.set_strategy(SimpleStrategy())
        # C4 = 261.63Hz -> 1
        self.assertEqual(self.ctx.pitch_to_note(261.63), '1')
        # A4 = 440Hz -> 6
        self.assertEqual(self.ctx.pitch_to_note(440.0), '6')


class TestLibrosaStrategy(unittest.TestCase):
    """测试Librosa策略"""

    def setUp(self):
        self.strategy = LibrosaStrategy()

    def test_name(self):
        """测试策略名称"""
        self.assertEqual(self.strategy.name, "Librosa")

    def test_description(self):
        """测试策略描述"""
        self.assertIn("Librosa", self.strategy.description)


class TestSimpleStrategy(unittest.TestCase):
    """测试Simple策略"""

    def setUp(self):
        self.strategy = SimpleStrategy()

    def test_name(self):
        """测试策略名称"""
        self.assertEqual(self.strategy.name, "Simple")

    def test_description(self):
        """测试策略描述"""
        self.assertIn("FFT", self.strategy.description)


if __name__ == '__main__':
    unittest.main()