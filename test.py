
# === Основное окно с кнопкой и графической сценой ===
import unittest
class GraphicsTest(unittest.TestCase):
    def __init__(self, methodName='runTest',num_img=None):
        super().__init__(methodName)
        self.num_img = num_img

    def test_graphics_item_count(self):
        count = self.num_img
        print(f"🔍 Элементов на сцене: {count}")
        self.assertEqual(count, 4, "Ожидается 4 элемента на сцене")


