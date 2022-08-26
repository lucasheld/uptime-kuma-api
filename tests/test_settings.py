import unittest
import json

from uptime_kuma_test_case import UptimeKumaTestCase


class TestSettings(UptimeKumaTestCase):
    def test_settings(self):
        settings_before = self.api.get_settings()

        expected_check_update = not settings_before.get("checkUpdate", True)
        self.api.set_settings(self.password, checkUpdate=expected_check_update)

        settings = self.api.get_settings()
        self.assertEqual(settings["checkUpdate"], expected_check_update)

    def test_change_password(self):
        new_password = "321terces"

        # change password
        r = self.api.change_password(self.password, new_password)
        self.assertEqual(r["msg"], "Password has been updated successfully.")

        # check login
        r = self.api.login(self.username, new_password)
        self.assertIn("token", r)

        # restore password
        r = self.api.change_password(new_password, self.password)
        self.assertEqual(r["msg"], "Password has been updated successfully.")

    def test_upload_backup(self):
        data = {
            "version": "1.17.1",
            "notificationList": [],
            "monitorList": [],
            "proxyList": []
        }
        data_str = json.dumps(data)
        r = self.api.upload_backup(data_str, "overwrite")
        self.assertEqual(r["msg"], "Backup successfully restored.")


if __name__ == '__main__':
    unittest.main()
