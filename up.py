from hm_api.public.r_bloom import Session, User

s = Session()
user = s.query(User).filter(User.id == 3).first()
from hm_api.public.r_bloom import NewOrder
import pandas as pd


f = "data/000-test-30.csv"
df = pd.read_csv(f)
with Session() as session:
    o = NewOrder(session, "3", if_exists_drop=True, testing=True)
    o.format_df(df)
    o.upload()

counter_key = f"hm_api:count:{o.order.id}"


from hm_api import rd
import time

while True:
    print(rd.get(counter_key))
    time.sleep(0.2)
