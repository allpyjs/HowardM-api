from . import base
from base64 import b64encode
import logging
import uuid

from hm_api.app import app
from hm_api.public.models import User
from hm_api import OrdersSession
import warnings as warn

logger = logging.getLogger(__name__)


class BaseTest(base.BaseTest):
    def setUp(self) -> None:
        super().setUp()
        self.logger = logger
        self.logger.info("Setting up BaseTest")
        with warn.catch_warnings():
            warn.simplefilter("ignore")
            # the code that raises the warning goes here
            self.app = app
        self.app.testing = True
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()

        self.orders_session = OrdersSession()

        self.username = "test_username"
        self.password = "12345678"
        self.email = "testuser@gmail.com"
        self.user_id = 0
        self.create_user()

        self.headers = {
            "Authorization": "Basic " +
                             b64encode(bytes(self.email + ":" +
                                             self.password, 'ascii')).decode('ascii'),
            "Content-Type": "application/json"}

    def create_user(self):
        user = User()
        user.username = self.username
        user.password = self.password
        user.active = True
        user.email = self.email
        user.fs_uniquifier = str(uuid.uuid4())
        self.orders_session.add(user)
        self.orders_session.commit()
        self.user_id = user.id
        self.logger.info("User Created")

    def remove_user(self) -> None:
        user = self.orders_session.query(User).filter(
            User.username == self.username).first()

        if user:
            self.orders_session.delete(user)
            self.orders_session.commit()
            self.logger.info("User Removed")

    def tearDown(self) -> None:
        super().tearDown()
        self.logger.info("Tearing down HmNotificationsTest")
        self.appctx.pop()
        self.app = None
        self.appctx = None
        self.client = None
        self.remove_user()
        self.orders_session.close()
