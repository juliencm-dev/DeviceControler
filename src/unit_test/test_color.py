import unittest
from enum import Enum
from color import Color

class TestColor(unittest.TestCase):
    # TEST INIT
    def test_init_color_01(self):
      color = Color(Color.ColorBase.RED.value)
      self.assertEqual(color.rgb, (255, 0, 0))

    def test_init_color_02(self):
      color = Color((0, 24, 33))
      self.assertEqual(color.rgb, (0, 24, 33))

    def test_init_color_03(self):
      color = Color((0, -23, 33))
      self.assertEqual(color.rgb, (0, 0, 33))

    # TEST SETTER
    def test_rgb_setter_01(self):
        color = Color(Color.ColorBase.RED.value)
        color.rgb = (Color.ColorBase.GREEN.value)
        self.assertEqual(color.rgb, (0, 255, 0))

    def test_rgb_setter_02(self):
        color = Color(Color.ColorBase.RED.value)
        color.rgb = (Color.ColorBase.GREEN.value)
        color.rgb = (Color.ColorBase.BLACK.value)
        self.assertEqual(color.rgb, (0, 0, 0))
    
    def test_rgb_setter_min(self):
        color = Color(Color.ColorBase.RED.value)
        color.rgb = ((-10, -55, 30))
        self.assertEqual(color.rgb, (0, 0, 30))

    # TEST CHANGE_COLOR
    def test_change_color(self):
        color = Color(Color.ColorBase.RED.value)
        color.change_color((0, 10, 0))
        self.assertEqual(color.rgb, (255, 10, 0))

    def test_change_color_max(self):
        color = Color((255, 250, 0))
        color.change_color((0, 10, 0))
        self.assertEqual(color.rgb, (255, 255, 0))

    def test_change_color_min(self):
        color = Color((255, 10, 0))
        color.change_color((0, -30, 0))
        self.assertEqual(color.rgb, (255, 0, 0))

if __name__ == '__main__':
    unittest.main()