import json
import unittest
from packaging.version import parse as parse_version

from uptime_kuma_test_case import UptimeKumaTestCase


class TestSettings(UptimeKumaTestCase):
    def test_settings(self):
        expected_settings = {
            "checkUpdate": False,
            "checkBeta": False,
            "keepDataPeriodDays": 180,
            "entryPage": "dashboard",
            "searchEngineIndex": False,
            "primaryBaseURL": "",
            "steamAPIKey": "",
            "tlsExpiryNotifyDays": [7, 14, 21],
            "disableAuth": False
        }

        if parse_version(self.api.version) >= parse_version("1.18"):
            expected_settings.update({
                "trustProxy": False
            })

        # set settings
        r = self.api.set_settings(self.password, **expected_settings)
        self.assertEqual(r["msg"], "Saved")

        # set settings without password
        r = self.api.set_settings(**expected_settings)
        self.assertEqual(r["msg"], "Saved")

        # get settings
        settings = self.api.get_settings()
        self.compare(settings, expected_settings)

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
