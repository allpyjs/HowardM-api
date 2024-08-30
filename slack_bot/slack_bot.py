"""
Howard Miller Clock Company Slack-bot server
"""
import logging
import os
from collections.abc import Callable
from functools import wraps
from typing import NamedTuple

import bugsnag
import httpx
import psycopg2
from flask import Flask, request
from flask.cli import load_dotenv

app = Flask(__name__)
if __name__ != "__main__":
    # Use gunicorn logger if not being run independently
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# Load configuration from .env file and env variables
load_dotenv()
for name in [
    "POSTGRES_URL",
    "HMCCDEV_USER",
    "HMCCDEV_PASS",
]:
    app.config[name] = os.environ[name]


class InventoryItem(NamedTuple):
    """
    Structure of an inventory item as retrieved from hmccdev API
    """

    avail_1_date: str
    avail_1_qty: str  # originally interface{} ?
    avail_2_date: str  # originally interface{} ?
    avail_2_qty: str  # originally interface{} ?
    avail_3_date: str  # originally interface{} ?
    avail_3_qty: str  # originally interface{} ?
    avail_4_date: str  # originally interface{} ?
    avail_4_qty: str  # originally interface{} ?
    brand: str
    created_at: str
    date_of_last_update: str
    in_stock: bool
    item: str
    monthly_usage: str  # originally interface{} ?
    name: str
    quantity: str  # originally interface{} ?
    status: str
    unit_cost: str  # originally interface{} ?
    upc: str


def sku_slack_command(response: Callable[[str], dict]):
    """
    Generic endpoint for forms with text and repsonse_url parameters.
    """

    @wraps(response)
    def command():
        sku = request.form["text"]
        response_url = request.form["response_url"]
        response_body = response(sku)
        app.logger.info(response_body)
        post_response = httpx.post(response_url, json=response_body)
        post_response.raise_for_status()
        app.logger.info("post response:\t%s", post_response.text)
        # must return a 200 response, though the actual message gets posted to
        # the response_url separately
        return {}

    return command


@app.route("/inventory", methods=["POST"])
@sku_slack_command
def inventory_command(sku: str) -> dict:
    """
    Produce the Slack response for an inventory SKU.
    """
    # Load data from the dev API
    user = app.config["HMCCDEV_USER"]
    password = app.config["HMCCDEV_PASS"]
    uri = f"http://{user}:{password}@hmccdev.com/api/v2/sku/" + sku
    item_response = httpx.get(uri)
    app.logger.info("foo")
    item_response.raise_for_status()
    item = InventoryItem(**item_response.json())

    if item.brand == "howard miller":
        link = (
            f"http://services.howardmiller.com/cgi-bin/sa7007f?SItem={item.item}&GO=Go"
        )
    elif item.brand == "hekman":
        link = f"http://services.hekman.com/cgi-bin/IN2006EONE?SItem={item.item}&GO=Go"
    else:
        link = ""

    avail_date = item.avail_1_date.replace("T00:00:00.000Z", "")
    avail_qty = item.avail_1_qty or ""

    result_body = {
        "response_type": "in_channel",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": item.name, "emoji": True},
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Quantity Available:*\n{item.quantity}",
                    },
                    {"type": "mrkdwn", "text": f"<{link}|Dealer Services Link>"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Next Available Qty:*\n{avail_qty}"},
                    {"type": "mrkdwn", "text": f"*Next Available Date:*\n{avail_date}"},
                ],
            },
        ],
    }
    return result_body


@app.route("/history", methods=["POST"])
@sku_slack_command
def history_command(sku: str) -> dict:
    """
    Fetch historical inventory information for a SKU;
    present the results as a table.
    """
    query = """
    SELECT sku, hm_quantity, logged_at FROM (
      SELECT
        sku,
        logged_at,
        hm_quantity,
        hm_quantity - LAG(hm_quantity) OVER (ORDER BY logged_at) as diff
      FROM stock_quantities
      WHERE sku = %s
      ) sq
    WHERE diff IS NULL OR diff != 0
    ORDER BY logged_at DESC LIMIT 50;
    """
    header = "SKU       QUANTITY    TIMESTAMP\n"
    with psycopg2.connect(app.config["POSTGRES_URL"]) as conn, conn.cursor() as cur:
        cur.execute(query, (sku,))
        result = "".join(
            [
                "```",
                header,
                "\n".join(
                    f"{_sku:<6}    {quantity:>3}         {logged_at.isoformat()}"
                    for (_sku, quantity, logged_at) in cur
                ),
                "```",
            ]
        )
    result_body = {"response_type": "in_channel", "text": result}
    return result_body


if __name__ == "__main__":
    bugsnag.configure(
        api_key="aad2c2bb6f982c191723199acd7d1c14",
        project_root=os.path.dirname(__file__),
        app_type="slack_bot",
        enabled_breadcrumb_types=[
            bugsnag.BreadcrumbType.ERROR,
            bugsnag.BreadcrumbType.LOG,
        ],
    )
    handler = bugsnag.handlers.BugsnagHandler()
    handler.setLevel(logging.WARNING)
    logging.getLogger().addFilter(handler.leave_breadcrumbs)
    logging.getLogger().addHandler(handler)
    app.run()
