from sqlalchemy import Table, Column, Integer, String, MetaData, Numeric

metadata = MetaData()

products = Table('products', metadata,
                 Column('product_id', Integer, primary_key=True),
                 Column('product_name', String(200)),
                 Column('category', String(200)),
                 Column('price', Numeric(10,2)),
)

def create_tables(engine):
    metadata.create_all(engine)