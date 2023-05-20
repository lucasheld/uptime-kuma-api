import unittest

from uptime_kuma_test_case import UptimeKumaTestCase


class TestGameList(UptimeKumaTestCase):
    def test_game_list(self):
        game_list = self.api.get_game_list()
        self.assertTrue("keys" in game_list[0])


if __name__ == '__main__':
    unittest.main()
