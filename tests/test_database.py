import unittest

from uptime_kuma_test_case import UptimeKumaTestCase


class TestDatabase(UptimeKumaTestCase):
    def test_get_database_size(self):
        r = self.api.get_database_size()
        self.assertIn("size", r)

    def test_shrink_database(self):
        self.api.shrink_database()


if __name__ == '__main__':
    unittest.main()
