import unittest

from packaging.version import parse as parse_version

from uptime_kuma_api import UptimeKumaException, IncidentStyle
from uptime_kuma_test_case import UptimeKumaTestCase


class TestStatusPage(UptimeKumaTestCase):
    def test_status_page(self):
        # get empty list to make sure that future accesses will also work
        self.api.get_status_pages()

        monitor_id = self.add_monitor()

        slug = "slug1"
        expected_status_page = {
            "slug": slug,
            "title": "status page 1",
            "description": "description 1",
            "theme": "light",
            "published": True,
            "showTags": False,
            "domainNameList": [],
            "customCSS": "",
            "footerText": None,
            "showPoweredBy": False,
            "icon": "/icon.svg",
            "publicGroupList": [
                {
                    'name': 'Services',
                    'weight': 1,
                    'monitorList': [
                        {
                            "id": monitor_id
                        }
                    ]
                }
            ]
        }
        if parse_version(self.api.version) >= parse_version("1.20"):
            expected_status_page.update({
                "googleAnalyticsId": ""
            })

        # add status page
        r = self.api.add_status_page(slug, expected_status_page["title"])
        self.assertEqual(r["msg"], "OK!")

        # save status page
        self.api.save_status_page(**expected_status_page)

        # get status page
        status_page = self.api.get_status_page(slug)
        self.compare(status_page, expected_status_page)

        # get status pages
        status_pages = self.api.get_status_pages()
        status_page = self.find_by_id(status_pages, slug, "slug")
        self.assertIsNotNone(status_page)
        # publicGroupList and incident is not available in status pages
        expected_status_page_config = {i: expected_status_page[i] for i in expected_status_page if i != "publicGroupList"}
        self.compare(status_page, expected_status_page_config)

        # edit status page
        expected_status_page["title"] = "status page 1 new"
        expected_status_page["theme"] = "dark"
        self.api.save_status_page(**expected_status_page)
        status_page = self.api.get_status_page(slug)
        self.compare(status_page, expected_status_page)

        # pin incident
        incident_expected = {
            "title": "title 1",
            "content": "content 1",
            "style": IncidentStyle.DANGER
        }
        incident = self.api.post_incident(slug, **incident_expected)
        self.compare(incident, incident_expected)
        status_page = self.api.get_status_page(slug)
        self.compare(status_page["incident"], incident)

        # unpin incident
        self.api.unpin_incident(slug)
        status_page = self.api.get_status_page(slug)
        self.assertIsNone(status_page["incident"])

        # delete status page
        self.api.delete_status_page(slug)
        with self.assertRaises(UptimeKumaException):
            self.api.get_status_page(slug)

        status_pages = self.api.get_status_pages()
        status_page = self.find_by_id(status_pages, slug, "slug")
        self.assertIsNone(status_page)


if __name__ == '__main__':
    unittest.main()
