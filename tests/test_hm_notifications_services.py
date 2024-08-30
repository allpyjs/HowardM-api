import json
import time
from uuid import uuid4
from datetime import datetime, timedelta
import pytz
from sqlalchemy.orm import Session

from hm_api import config
from hm_api import OpSession
from hm_api.engines import OP_ENGINE
import hm_api.hm_notifications.services as services
from hm_api.hm_notifications.models.notifications_autogen import HmNotificationStock as Hnstock
from hm_api.hm_notifications.models.notifications_autogen import HmNotificationMessage as Hnm
from hm_api.hm_notifications.models.notifications_autogen import HmNotificationSubscription as Hnsub

from tests.with_user_base import BaseTest


class TestHmNotificationsServices(BaseTest):
    def setUp(self) -> None:

        super().setUp()
        self.op_session = OpSession()
        self.product_skus = ["635113FDS", "28488K6L1FFFAD", "28488K4K4FCDS"]
        self.real_product_skus = ["635113", "28488K6L1FF", "28488K4K4FC"]

        self.stocks = []

    def test_check_restock(self):
        self.logger.info(
            "TestHmNotificationsServices.test_check_restock: started")
        self.create_product_stock()
        self.subscribe_to_products()

        config.UNITTESTING_ENABLED = True
        services.check_restock(testing_args=self.stocks,
                               is_unit_test=config.UNITTESTING_ENABLED)
        config.UNITTESTING_ENABLED = False

        # quantity > 0 and out_of_stock_date was not null
        stock = self.get_product_stock(self.stocks[0]['id'])
        self.assertEqual(stock.out_of_stock_date, None)

        stock = self.get_product_stock(self.stocks[1]['id'])
        self.assertEqual(stock.out_of_stock_date, None)

        # quantity < 1 and out_of_stock_date was null
        stock = self.get_product_stock(self.stocks[2]['id'])
        self.assertNotEqual(stock.out_of_stock_date, None)

        # self.assertNotEqual(self.get_notifications_message(), None)
        self.logger.info(
            "TestHmNotificationsServices.test_check_restock: done")

    def test_send_mail(self):
        self.logger.info("TestHmNotificationsServices.test_send_mail: started")
        self.create_notification_message()

        message = self.get_notifications_message()
        self.assertEqual(message.notification_send_date, None)

        config.UNITTESTING_ENABLED = True
        services.process_notifications_queue(test_user_id=self.user_id,
                                             is_unit_test=config.UNITTESTING_ENABLED)
        config.UNITTESTING_ENABLED = False
        time.sleep(5)

        message = self.get_notifications_message()

        self.assertNotEqual(message.notification_send_date, None)

        self.logger.info("TestHmNotificationsServices.test_send_mail: done")

    def create_notification_message(self):
        self.logger.info("Creating Notification Message")

        message = Hnm(
            user_id=self.user_id,
            message_code=str(uuid4()),
            sku=self.real_product_skus[0],
            notification_send_date=None
        )

        self.op_session.add(message)
        self.op_session.commit()

    def get_product_stock(self, entry_id):
        return self.op_session.query(Hnstock).filter(Hnstock.id == entry_id).first()

    def get_notifications_message(self):
        with Session(OP_ENGINE) as session:
            return session.query(Hnm).filter(Hnm.user_id == self.user_id).first()

    def create_product_stock(self):
        self.logger.info("Creating Product Stocks")

        quantities = [10, 15, 0]
        dates = [datetime.now(pytz.utc), datetime.now(
            pytz.utc) - timedelta(7), None]

        for sku, quantity, date in zip(self.product_skus, quantities, dates):
            stock = dict(
                id=str(uuid4()),
                inventory_updated_at=datetime.now(pytz.utc),
                sku=sku,
                quantity=quantity,
                out_of_stock_date=date
            )
            self.stocks.append(stock)

        self.op_session.bulk_insert_mappings(Hnstock, self.stocks)
        self.op_session.commit()

    def subscribe_to_products(self):
        self.logger.info("Creating subscription")

        payload = json.dumps({
            "skus": self.product_skus
        })

        response = self.client.put('/api/subscription-notifications', headers=self.headers,
                                   data=payload, follow_redirects=True)

        if response.status_code == 200:
            return True
        else:
            raise Exception("Couldn't subscribe to products")

    def remove_product_stock(self):
        self.op_session.query(Hnstock).filter(Hnstock.sku.in_(
            self.product_skus)).delete(synchronize_session=False)
        self.op_session.commit()
        self.logger.info("Removed product stock")

    def remove_all_subscription(self):
        self.op_session.query(Hnsub).filter(
            Hnsub.user_id == self.user_id).delete(synchronize_session=False)
        self.op_session.commit()
        self.logger.info("Removed subscription")

    def remove_all_message(self):
        self.op_session.query(Hnm).filter(
            Hnm.user_id == self.user_id).delete(synchronize_session=False)
        self.op_session.commit()
        self.logger.info("Removed messages")

    def tearDown(self) -> None:
        """
            1. delete products
            2. delete account
        """
        super().tearDown()
        self.remove_product_stock()
        self.remove_all_message()
        self.remove_all_subscription()
        self.op_session.close()
