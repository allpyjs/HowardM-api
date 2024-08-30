import os

# import time

import pytest
import pandas as pd
from random import randint

from hm_api.orders import auth_get
from hm_api.utils.moz import parse
from hm_api.dealer_services.hm.services import req_dict, HM_ORDER_TEST_BASE_URL


def get_open_order(ord_seq, cust_seq="001", customer="77633"):
    """
    Returns the open orders for a customer. Mainly used for testing since
    it doesn't handle pagination and as of now isn't very useful.
    """
    req = req_dict(
        "/cgi-bin/EZ1004E",
        {
            "STrack": f"{ord_seq}",
            "SCusN": f"{customer}",
            "SSeq": f"{cust_seq}",
            "ZAction": " ",
        }
    )

    req['GET']['remote'] = {"Address": "96.36.3.83:80"}

    u = parse(req)
    url = u["url"]
    html = auth_get(url).text
    return html


curdir = os.path.dirname(__file__)

PO_MAP = {"000": "PO Number", "001": "PO#"}


def make_file(param):
    filepath = f"{curdir}/{param}-test.csv"
    suffix = randint(0, 10000)
    df = pd.read_csv(filepath)
    col = PO_MAP.get(param)
    po = df.head(1).to_dict("records")[0][col] + "-" + str(suffix)
    df[col] = po
    outfile = f"/tmp/HMCC-testing{param}-{suffix}.csv"
    df.to_csv(outfile, index=False)
    return outfile, po


base = "http://localhost:5000"


@pytest.fixture(params=["000", "001"])
def run_test(driver, request):
    # param is the seq
    param = request.param
    # open site in browser
    driver.get(base)
    driver.implicitly_wait(10)  # seconds

    # login
    driver.find_element_by_link_text("Log In").click()
    username = driver.find_element_by_id("username")
    username.send_keys(f"retail_bloom_{param}")
    password = driver.find_element_by_id("password")
    password.send_keys("changeme")
    driver.find_element_by_class_name("btn-lg").click()

    # go to order upload page
    driver.get(f"{base}/order")
    f = driver.find_element_by_id("customFile")
    # make csv file with dynamic po and then upload
    fp, po = make_file(param)
    f.send_keys(fp)
    driver.find_element_by_id("btn-pusher").click()
    # wait until table is visible
    driver.find_element_by_id("pandas-table_info")

    # assert the sku in our csv is visible
    assert "625296" in driver.page_source
    html = auth_get("%s?%s" % (HM_ORDER_TEST_BASE_URL, "SCUSN=")).text

    # make sure po is show in dealer services
    assert po in html
    seq = driver.find_element_by_id("order_seq_cancel").get_attribute("value")
    assert seq in html

    # make sure the custom attributes of 001 (address etc.) are working and visible in dealer services
    if param == "001":
        html = get_open_order(seq)
        assert "Radosveta Stoyanov" in html
    driver.find_element_by_class_name("restart-btn").click()
    driver.find_element_by_id("flashid")

    # test restart button
    assert "Cancelled" in driver.page_source
    html = auth_get("%s?" % HM_ORDER_TEST_BASE_URL)

    # make sure that the po was deleted
    assert po not in html


def test_app(run_test):
    pass
