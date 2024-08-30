import pandas as pd
from hm_api import OP_ENGINE


query = """
with a as (
select * 
    from hm_orders 
    where customer_no = '77633'
    and delivery_name not like 'RETAIL BLOOM%'

), b as (
    select order_no,
    count(*) as n
    from a
    group by 1
)
select 
    products.usps_ok,
    a.order_date as "Order Date",
    a.order_date as "Delivery By",
    concat('nick-po-testing-', a.order_no,  '-', floor(random() * 100 + 1)::int)::text as "PO#",
    a.sku as "SKU",
    a.order_qty as "Quantity",
    a.unit_cost as "Cost",
    a.delivery_name as "Name",
    a.delivery_street_1 as "Address1",
    a.delivery_street_2 as "Address2",
    a.delivery_city as "City",
    a.delivery_state as "State/province",
    a.delivery_zip as "Postal Code",
    'US' as "Country"
    from a
    left join products on products.sku = a.sku
    where a.order_no in (select order_no from b where n > 1)
    and a.unit_cost is not null
    order by "PO#"

"""
with OP_ENGINE.connect() as conn:
    df = pd.read_sql_query(query, conn)
