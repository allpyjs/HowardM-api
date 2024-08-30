import json

from tests.with_user_base import BaseTest
from hm_api import OpSession

from hm_api.hm_notifications.models.notifications_autogen import HmNotificationSubscription as Hns


class TestHmNotifications(BaseTest):

    def setUp(self) -> None:
        super().setUp()
        self.op_session = OpSession()
        self.product_skus = ["635113", "28488K6L1FF", "28488K4K4FC"]

    def test_create_subscriptions(self):
        self.logger.info(
            "HmNotificationsTest.test_create_subscriptions: started")

        response = self.create_subscription()
        self.assertEqual('OK', response.get_json()['result'])
        self.assertEqual(200, response.status_code)
        self.logger.info("HmNotificationsTest.test_create_subscriptions: done")

    def test_get_all_subscription(self):
        self.logger.info(
            "HmNotificationsTest.test_get_all_subscription: started")
        self.create_subscription()
        response = self.client.get(
            '/api/subscription-notifications', headers=self.headers, follow_redirects=True)

        self.assertEqual('OK', response.get_json()['result'])
        # self.assertEqual(3, len(response.get_json()['subscription']))
        self.assertEqual(200, response.status_code)
        self.logger.info("HmNotificationsTest.test_get_all_subscription: done")

    def test_remove_subscriptions(self):
        self.logger.info(
            "HmNotificationsTest.test_remove_subscriptions: started")
        self.create_subscription()
        payload = json.dumps({
            'skus': self.product_skus
        })

        response = self.client.delete('/api/subscription-notifications',
                                      headers=self.headers,
                                      data=payload)

        self.assertEqual('OK', response.get_json()['result'])
        self.assertEqual(200, response.status_code)
        self.logger.info("HmNotificationsTest.test_remove_subscriptions: done")

    def create_subscription(self):
        self.logger.info("Creating subscription")
        payload = json.dumps({
            "skus": self.product_skus
        })

        response = self.client.put('/api/subscription-notifications', headers=self.headers,
                                   data=payload, follow_redirects=True)

        return response

    def remove_all_subscription(self):
        self.op_session.query(Hns).filter(
            Hns.user_id == self.user_id).delete(synchronize_session=False)
        self.op_session.commit()
        self.logger.info("Removing subscription")

    def tearDown(self) -> None:
        super().tearDown()
        self.remove_all_subscription()
        self.logger.info("Tearing down HmNotificationsTest complete!")
        self.op_session.close()
