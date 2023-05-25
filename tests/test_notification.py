import unittest

from uptime_kuma_api import UptimeKumaException, NotificationType
from uptime_kuma_test_case import UptimeKumaTestCase


class TestNotification(UptimeKumaTestCase):
    def test_notification(self):
        # get empty list to make sure that future accesses will also work
        self.api.get_notifications()

        expected_notification = {
            "name": "notification 1",
            "isDefault": True,
            "applyExisting": True,
            "type": NotificationType.TELEGRAM,
            "telegramChatID": "123456789",
            "telegramBotToken": "987654321"
        }

        # test notification
        with self.assertRaisesRegex(UptimeKumaException, r'Not Found'):
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
        expected_notification["applyExisting"] = False
        expected_notification["type"] = NotificationType.PUSHDEER
        expected_notification["pushdeerKey"] = "987654321"
        del expected_notification["telegramChatID"]
        del expected_notification["telegramBotToken"]
        r = self.api.edit_notification(notification_id, **expected_notification)
        self.assertEqual(r["msg"], "Saved")
        notification = self.api.get_notification(notification_id)
        self.compare(notification, expected_notification)
        self.assertIsNone(notification.get("pushAPIKey"))

        # delete notification
        r = self.api.delete_notification(notification_id)
        self.assertEqual(r["msg"], "Deleted")
        with self.assertRaises(UptimeKumaException):
            self.api.delete_notification(notification_id)

    def test_delete_not_existing_notification(self):
        with self.assertRaises(UptimeKumaException):
            self.api.delete_notification(42)


if __name__ == '__main__':
    unittest.main()
