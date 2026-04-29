from database import get_engine
from etl import load_dim_dates, load_customer_records, load_products_records, load_facts_sales
from models import create_tables

engine = get_engine()
create_tables(engine)
load_facts_sales(engine)
print("Concluido com sucesso!")