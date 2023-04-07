import unittest

from packaging.version import parse as parse_version

from uptime_kuma_api import UptimeKumaException, MaintenanceStrategy
from uptime_kuma_test_case import UptimeKumaTestCase


class TestMaintenance(UptimeKumaTestCase):
    def setUp(self):
        super(TestMaintenance, self).setUp()
        if parse_version(self.api.version) < parse_version("1.19"):
            super(TestMaintenance, self).tearDown()
            self.skipTest("Unsupported in this Uptime Kuma version")

    def test_maintenance(self):
        expected_maintenance = {
            "title": "maintenance 1",
            "description": "test",
            "strategy": MaintenanceStrategy.SINGLE,
            "active": True,
            "intervalDay": 1,
            "dateRange": [
                "2022-12-27 22:36:00",
                "2022-12-29 22:36:00"
            ],
            "weekdays": [],
            "daysOfMonth": []
        }

        if parse_version(self.api.version) >= parse_version("1.21.2"):
            expected_maintenance.update({
                "timezone": "Europe/Berlin"
            })

        # add maintenance
        r = self.api.add_maintenance(**expected_maintenance)
        self.assertEqual(r["msg"], "Added Successfully.")
        maintenance_id = r["maintenanceID"]

        # get maintenance
        maintenance = self.api.get_maintenance(maintenance_id)
        self.compare(maintenance, expected_maintenance)

        # get maintenances
        maintenances = self.api.get_maintenances()
        maintenance = self.find_by_id(maintenances, maintenance_id)
        self.assertIsNotNone(maintenance)
        self.compare(maintenance, expected_maintenance)

        # edit maintenance
        expected_maintenance["strategy"] = MaintenanceStrategy.RECURRING_INTERVAL
        expected_maintenance["title"] = "maintenance 1 new"
        r = self.api.edit_maintenance(maintenance_id, **expected_maintenance)
        self.assertEqual(r["msg"], "Saved.")
        maintenance = self.api.get_maintenance(maintenance_id)
        self.compare(maintenance, expected_maintenance)

        # pause maintenance
        r = self.api.pause_maintenance(maintenance_id)
        self.assertEqual(r["msg"], "Paused Successfully.")

        # resume maintenance
        r = self.api.resume_maintenance(maintenance_id)
        self.assertEqual(r["msg"], "Resume Successfully")

        # add monitor maintenance
        monitor_name = "monitor 1"
        monitor_id = self.add_monitor(monitor_name)
        monitors = [
            {
                "id": monitor_id,
                "name": monitor_name
            },
        ]
        r = self.api.add_monitor_maintenance(maintenance_id, monitors)
        self.assertEqual(r["msg"], "Added Successfully.")

        # get monitor maintenance
        monitors = self.api.get_monitor_maintenance(maintenance_id)
        monitor = self.find_by_id(monitors, monitor_id)
        self.assertIsNotNone(monitor)

        # add status page maintenance
        status_page_title = "status page 1"
        status_page_id = self.add_status_page(status_page_title)
        status_pages = [
            {
                "id": status_page_id,
                "name": status_page_title
            }
        ]
        r = self.api.add_status_page_maintenance(maintenance_id, status_pages)
        self.assertEqual(r["msg"], "Added Successfully.")

        # get status page maintenance
        status_pages = self.api.get_status_page_maintenance(maintenance_id)
        status_page = self.find_by_id(status_pages, status_page_id)
        self.assertIsNotNone(status_page)

        # delete maintenance
        r = self.api.delete_maintenance(maintenance_id)
        self.assertEqual(r["msg"], "Deleted Successfully.")
        with self.assertRaises(UptimeKumaException):
            self.api.get_maintenance(maintenance_id)

    def test_maintenance_strategy_manual(self):
        expected_maintenance = {
            "title": "test",
            "description": "test",
            "strategy": MaintenanceStrategy.MANUAL,
            "active": True,
            "intervalDay": 1,
            "dateRange": [
                "2022-12-27 00:00:00"
            ],
            "weekdays": [],
            "daysOfMonth": []
        }
        self.do_test_maintenance_strategy(expected_maintenance)

    def test_maintenance_strategy_single(self):
        expected_maintenance = {
            "title": "test",
            "description": "test",
            "strategy": MaintenanceStrategy.SINGLE,
            "active": True,
            "intervalDay": 1,
            "dateRange": [
                "2022-12-27 22:36:00",
                "2022-12-29 22:36:00"
            ],
            "weekdays": [],
            "daysOfMonth": []
        }
        self.do_test_maintenance_strategy(expected_maintenance)

    def test_maintenance_strategy_recurring_interval(self):
        expected_maintenance = {
            "title": "test",
            "description": "test",
            "strategy": MaintenanceStrategy.RECURRING_INTERVAL,
            "active": True,
            "intervalDay": 1,
            "dateRange": [
                "2022-12-27 22:37:00",
                "2022-12-31 22:37:00"
            ],
            "timeRange": [
                {
                    "hours": 2,
                    "minutes": 0
                },
                {
                    "hours": 3,
                    "minutes": 0
                }
            ],
            "weekdays": [],
            "daysOfMonth": []
        }
        self.do_test_maintenance_strategy(expected_maintenance)

    def test_maintenance_strategy_recurring_weekday(self):
        expected_maintenance = {
            "title": "test",
            "description": "test",
            "strategy": MaintenanceStrategy.RECURRING_WEEKDAY,
            "active": True,
            "intervalDay": 1,
            "dateRange": [
                "2022-12-27 22:38:00",
                "2022-12-31 22:38:00"
            ],
            "timeRange": [
                {
                    "hours": 2,
                    "minutes": 0
                },
                {
                    "hours": 3,
                    "minutes": 0
                }
            ],
            "weekdays": [
                1,
                3,
                5,
                0
            ],
            "daysOfMonth": []
        }
        self.do_test_maintenance_strategy(expected_maintenance)

    def test_maintenance_strategy_recurring_day_of_month(self):
        expected_maintenance = {
            "title": "test",
            "description": "test",
            "strategy": MaintenanceStrategy.RECURRING_DAY_OF_MONTH,
            "active": True,
            "intervalDay": 1,
            "dateRange": [
                "2022-12-27 22:39:00",
                "2022-12-31 22:39:00"
            ],
            "timeRange": [
                {
                    "hours": 2,
                    "minutes": 0
                },
                {
                    "hours": 3,
                    "minutes": 0
                }
            ],
            "weekdays": [],
            "daysOfMonth": [
                1,
                10,
                20,
                30,
                "lastDay1"
            ]
        }
        self.do_test_maintenance_strategy(expected_maintenance)

    def test_maintenance_strategy_cron(self):
        if parse_version(self.api.version) < parse_version("1.21.2"):
            self.skipTest("Unsupported in this Uptime Kuma version")

        expected_maintenance = {
            "title": "test",
            "description": "test",
            "strategy": MaintenanceStrategy.CRON,
            "active": True,
            "intervalDay": 1,
            "dateRange": [
                "2022-12-27 22:37:00",
                "2022-12-31 22:37:00"
            ],
            "weekdays": [],
            "daysOfMonth": [],
            "cron": "50 5 * * *",
            "durationMinutes": 120,
            "timezone": "Europe/Berlin"
        }
        self.do_test_maintenance_strategy(expected_maintenance)

    def do_test_maintenance_strategy(self, expected_maintenance):
        # add maintenance
        r = self.api.add_maintenance(**expected_maintenance)
        self.assertEqual(r["msg"], "Added Successfully.")
        maintenance_id = r["maintenanceID"]

        # get maintenance
        maintenance = self.api.get_maintenance(maintenance_id)
        self.compare(maintenance, expected_maintenance)

        # get maintenances
        maintenances = self.api.get_maintenances()
        maintenance = self.find_by_id(maintenances, maintenance_id)
        self.assertIsNotNone(maintenance)
        self.compare(maintenance, expected_maintenance)

        # edit maintenance
        r = self.api.edit_maintenance(maintenance_id, title="name 2")
        self.assertEqual(r["msg"], "Saved.")
        maintenance = self.api.get_maintenance(maintenance_id)
        expected_maintenance["title"] = "name 2"
        self.compare(maintenance, expected_maintenance)

        # delete maintenance
        r = self.api.delete_maintenance(maintenance_id)
        self.assertEqual(r["msg"], "Deleted Successfully.")
        with self.assertRaises(UptimeKumaException):
            self.api.get_maintenance(maintenance_id)


if __name__ == '__main__':
    unittest.main()
