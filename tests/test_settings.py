import unittest

from uptime_kuma_test_case import UptimeKumaTestCase


class TestSettings(UptimeKumaTestCase):
    def test_settings(self):
        settings_before = self.api.get_settings()

        expected_check_update = not settings_before.get("checkUpdate", True)
        self.api.set_settings(self.password, checkUpdate=expected_check_update)

        settings = self.api.get_settings()
        self.assertEqual(settings["checkUpdate"], expected_check_update)


if __name__ == '__main__':
    unittest.main()
