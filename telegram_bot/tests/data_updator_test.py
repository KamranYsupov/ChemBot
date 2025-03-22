import unittest

from models import Metals
from programming_elements.enums import UpdaterDataKeys
from services import data_updator


class DataUpdatorTest(unittest.TestCase):
    async def test_message_courses(self):
        data = await data_updator.message_preparer({"A98": True}, Metals)
        self.assertEqual(data.get('message'), '[Золото | цена от 1 гр. ] Покупка: 5571.5 | Продажа: 5916.12')  # add assertion here


if __name__ == '__main__':
    unittest.main()
