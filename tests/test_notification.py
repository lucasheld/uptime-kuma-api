import unittest
from uptime_kuma_test_case import UptimeKumaTestCase
from uptime_kuma_api import UptimeKumaException


class TestNotification(UptimeKumaTestCase):
    def test_notification(self):
        expected_notification = {
            "name": "notification 1",
            "default": True,
            "apply_existing": True,
            "type_": "push_by_techulus",
            "push_by_techulus_apikey": "123456789"
        }

        # test notification
        with self.assertRaisesRegex(UptimeKumaException, r'Invalid API key'):
            self.api.test_notification(**expected_notification)

        # add notification
        r = self.api.add_notification(**expected_notification)
        self.assertEqual(r["msg"], "Saved")
        notification_id = r["id"]

        # get notification
        notification = self.api.get_notification(notification_id)
        self.compare(notification, expected_notification)

        # get notifications
        notifications = self.api.get_notifications()
        notification = self.find_by_id(notifications, notification_id)
        self.assertIsNotNone(notification)
        self.compare(notification, expected_notification)

        # edit notification
        expected_notification["name"] = "notification 1 new"
        expected_notification["default"] = False
        expected_notification["apply_existing"] = False
        expected_notification["type_"] = "push_deer"
        expected_notification["push_deer_deer_key"] = "987654321"
        del expected_notification["push_by_techulus_apikey"]
        r = self.api.edit_notification(notification_id, **expected_notification)
        self.assertEqual(r["msg"], "Saved")
        notification = self.api.get_notification(notification_id)
        self.compare(notification, expected_notification)

        # delete notification
        r = self.api.delete_notification(notification_id)
        self.assertEqual(r["msg"], "Deleted")
        with self.assertRaises(UptimeKumaException):
            self.api.delete_notification(notification_id)


if __name__ == '__main__':
    unittest.main()
