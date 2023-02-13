import unittest

from packaging.version import parse as parse_version

from uptime_kuma_test_case import UptimeKumaTestCase


class TestGameList(UptimeKumaTestCase):
    def setUp(self):
        super(TestGameList, self).setUp()
        if parse_version(self.api.version) < parse_version("1.20"):
            super(TestGameList, self).tearDown()
            self.skipTest("Unsupported in this Uptime Kuma version")

    def test_game_list(self):
        game_list = self.api.get_game_list()
        self.assertTrue("keys" in game_list[0])


if __name__ == '__main__':
    unittest.main()
